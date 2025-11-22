"""
Wallet analysis logic: Justice Algorithm using deterministic on-chain data.
"""
import json
from web3 import Web3
from pydantic import BaseModel
from typing import List, Dict

# Base Mainnet RPC
RPC_URL = "https://mainnet.base.org"
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Contract Addresses (Base Mainnet)
CONTRACTS = {
    "BRETT": "0x532f27101965dd16442E59d40670FaF5eBB142E4",
    "TOSHI": "0xAC1Bd2486aAf3B5C0fc3Fd868558b082a531B2B4",
    "DEGEN": "0x4ed4E862860beD51a9570b96d89aF5E1B0Efefed",
    "AERO": "0x940181a94A35A4569E4529A3CDfB74e38FD98631",
    "USDC": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    "BASE_PAINT": "0xba5e05cb26b78eda3a2f8e3b3814726305dcac83"
}

# Minimal ERC-20 ABI for balanceOf
ERC20_ABI = json.loads('[{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"}]')


class WalletStats(BaseModel):
    """Wallet statistics from on-chain analysis."""
    address: str
    eth_balance: float
    tx_count: int
    holdings: Dict[str, float]  # token_name -> balance
    wealth_score: float
    vitality_score: float
    community_score: float
    final_score: float
    tier: str


def get_token_balance(wallet_address: str, token_address: str) -> float:
    """
    Safely get token balance with error handling.
    
    Args:
        wallet_address: Wallet address to check
        token_address: Token contract address
        
    Returns:
        Token balance (0 if error)
    """
    try:
        contract = w3.eth.contract(
            address=w3.to_checksum_address(token_address),
            abi=ERC20_ABI
        )
        balance_wei = contract.functions.balanceOf(w3.to_checksum_address(wallet_address)).call()
        # Most tokens use 18 decimals, but we'll divide by 1e18 for simplicity
        # For USDC (6 decimals), this will be slightly off, but acceptable for scoring
        return balance_wei / 10**18
    except Exception:
        return 0.0


def calculate_wealth_score(eth_balance: float) -> float:
    """Calculate wealth score (0-100) based on ETH balance."""
    if eth_balance >= 10:
        return 100.0
    elif eth_balance >= 1:
        return 80.0
    elif eth_balance >= 0.1:
        return 50.0
    else:
        return 20.0


def calculate_vitality_score(tx_count: int) -> float:
    """Calculate vitality score (0-100) based on transaction count."""
    if tx_count >= 1000:
        return 100.0
    elif tx_count >= 500:
        return 85.0
    elif tx_count >= 100:
        return 60.0
    elif tx_count >= 20:
        return 40.0
    else:
        return 10.0


def calculate_community_score(holdings: Dict[str, float]) -> float:
    """
    Calculate community score (0-100) based on token holdings.
    +20 points for each token found (max 100).
    """
    score = 0.0
    for token_name, balance in holdings.items():
        if balance > 0:
            score += 20.0
    
    return min(100.0, score)


def calculate_tier(final_score: float) -> str:
    """Calculate tier based on final weighted score."""
    if final_score >= 85:
        return "GODLY"
    elif final_score >= 65:
        return "LEGENDARY"
    elif final_score >= 40:
        return "RARE"
    else:
        return "COMMON"


def analyze_wallet(address: str) -> WalletStats:
    """
    Analyze wallet using the Justice Algorithm.
    
    Args:
        address: Wallet address to analyze
        
    Returns:
        WalletStats object with all analysis data
    """
    if not w3.is_connected():
        raise ConnectionError("Failed to connect to Base Mainnet RPC")
    
    # Validate and checksum address
    if not w3.is_address(address):
        raise ValueError(f"Invalid wallet address: {address}")
    
    checksum_addr = w3.to_checksum_address(address)
    
    # Fetch hard data
    try:
        eth_balance_wei = w3.eth.get_balance(checksum_addr)
        eth_balance = eth_balance_wei / 10**18
        tx_count = w3.eth.get_transaction_count(checksum_addr)
    except Exception as e:
        raise ConnectionError(f"Failed to fetch wallet data: {e}")
    
    # Check token holdings
    holdings = {}
    for token_name, token_address in CONTRACTS.items():
        balance = get_token_balance(checksum_addr, token_address)
        if balance > 0:
            holdings[token_name] = balance
    
    # Calculate scores
    wealth_score = calculate_wealth_score(eth_balance)
    vitality_score = calculate_vitality_score(tx_count)
    community_score = calculate_community_score(holdings)
    
    # Calculate final weighted score
    final_score = (wealth_score * 0.3) + (vitality_score * 0.4) + (community_score * 0.3)
    
    # Determine tier
    tier = calculate_tier(final_score)
    
    return WalletStats(
        address=address,
        eth_balance=eth_balance,
        tx_count=tx_count,
        holdings=holdings,
        wealth_score=wealth_score,
        vitality_score=vitality_score,
        community_score=community_score,
        final_score=final_score,
        tier=tier
    )
