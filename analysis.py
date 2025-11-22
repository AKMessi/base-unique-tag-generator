import os
from web3 import Web3
from pydantic import BaseModel

# Base Mainnet RPC
RPC_URL = "https://mainnet.base.org"
w3 = Web3(Web3.HTTPProvider(RPC_URL))

CONTRACTS = {
    "BRETT": "0x532f27101965dd16442E59d40670FaF5eBB142E4",
    "TOSHI": "0xAC1Bd2486aAf3B5C0fc3Fd868558b082a531B2B4",
    "DEGEN": "0x4ed4E862860beD51a9570b96d89aF5E1B0Efefed",
    "AERO": "0x940181a94A35A4569E4529A3CDfB74e38FD98631",
    "USDC": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    "BASE_PAINT": "0xba5e05cb26b78eda3a2f8e3b3814726305dcac83"
}

ERC20_ABI = '[{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"}]'

class WalletStats(BaseModel):
    address: str
    eth_balance: float
    tx_count: int
    holdings: list[str]
    scores: dict
    tier: str

def analyze_wallet(address: str) -> WalletStats:
    if not w3.is_connected(): raise ConnectionError("RPC Connection Failed")
    checksum = w3.to_checksum_address(address)
    
    try:
        bal_wei = w3.eth.get_balance(checksum)
        eth_bal = bal_wei / 10**18
        tx_count = w3.eth.get_transaction_count(checksum)
    except:
        eth_bal, tx_count = 0, 0

    holdings = []
    for name, addr in CONTRACTS.items():
        try:
            ctr = w3.eth.contract(address=addr, abi=ERC20_ABI)
            if ctr.functions.balanceOf(checksum).call() > 0:
                holdings.append(name)
        except:
            continue

    # Scoring
    if eth_bal >= 5.0: s_wealth = 100
    elif eth_bal >= 1.0: s_wealth = 80
    elif eth_bal >= 0.1: s_wealth = 50
    else: s_wealth = 20

    if tx_count >= 1000: s_vitality = 100
    elif tx_count >= 500: s_vitality = 85
    elif tx_count >= 100: s_vitality = 60
    elif tx_count >= 20: s_vitality = 40
    else: s_vitality = 10

    s_comm = min(100, len(holdings) * 20)

    final_score = (s_wealth * 0.3) + (s_vitality * 0.4) + (s_comm * 0.3)
    if final_score >= 85: tier = "GODLY"
    elif final_score >= 65: tier = "LEGENDARY"
    elif final_score >= 40: tier = "RARE"
    else: tier = "COMMON"

    return WalletStats(
        address=address,
        eth_balance=eth_bal,
        tx_count=tx_count,
        holdings=holdings,
        scores={"wealth": s_wealth, "vitality": s_vitality, "community": s_comm, "final": int(final_score)},
        tier=tier
    )