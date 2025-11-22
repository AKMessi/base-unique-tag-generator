"""
Base Identity Protocol - Streamlit Dashboard
"""
import streamlit as st
import plotly.graph_objects as go
from web3 import Web3
import qrcode
from io import BytesIO
from PIL import Image
import urllib.parse
from typing import Tuple

from graph import create_wallet_identity_graph, GraphState
from database import get_identity, mark_as_minted
from analysis import analyze_wallet, RPC_URL

# Mint configuration
MINT_AMOUNT_ETH = 0.5
MINT_RECIPIENT_ADDRESS = "0x0000000000000000000000000000000000000000"  # TODO: Replace with actual recipient address

# Page config
st.set_page_config(
    page_title="Base Identity Protocol",
    page_icon="🔷",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for dark theme
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
        color: white;
    }
    .stTextInput > div > div > input {
        background-color: #1E2130;
        color: white;
    }
    .stButton > button {
        background-color: #0066FF;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #0052CC;
    }
    .mint-button {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: #000;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-weight: bold;
        cursor: pointer;
    }
    .share-button {
        background-color: #1DA1F2;
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-weight: bold;
        cursor: pointer;
    }
    .tier-godly {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: #000;
        padding: 0.5rem 1.5rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        text-transform: uppercase;
        font-size: 0.9rem;
    }
    .tier-legendary {
        background: linear-gradient(135deg, #9D4EDD 0%, #7B2CBF 100%);
        color: white;
        padding: 0.5rem 1.5rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        text-transform: uppercase;
        font-size: 0.9rem;
    }
    .tier-rare {
        background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%);
        color: white;
        padding: 0.5rem 1.5rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        text-transform: uppercase;
        font-size: 0.9rem;
    }
    .tier-common {
        background: linear-gradient(135deg, #6C757D 0%, #495057 100%);
        color: white;
        padding: 0.5rem 1.5rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        text-transform: uppercase;
        font-size: 0.9rem;
    }
    .token-badge {
        display: inline-block;
        background-color: #1E2130;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        margin: 0.2rem;
        font-size: 0.85rem;
        border: 1px solid #0066FF;
    }
    .verdict-box {
        background-color: #1E2130;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #0066FF;
        margin: 1rem 0;
        font-style: italic;
    }
    .minted-badge {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: #000;
        padding: 0.5rem 1rem;
        border-radius: 15px;
        font-weight: bold;
        display: inline-block;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Web3 for address validation and payment checking
w3 = Web3(Web3.HTTPProvider(RPC_URL))


def validate_address(address: str) -> bool:
    """Validate Ethereum address."""
    return w3.is_address(address)


def get_tier_class(tier: str) -> str:
    """Get CSS class for tier."""
    tier_lower = tier.lower()
    if tier_lower == "godly":
        return "tier-godly"
    elif tier_lower == "legendary":
        return "tier-legendary"
    elif tier_lower == "rare":
        return "tier-rare"
    else:
        return "tier-common"


def create_radar_chart(wealth: float, vitality: float, community: float):
    """Create a radar chart for the three scores."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=[wealth, vitality, community],
        theta=['Wealth', 'Vitality', 'Community'],
        fill='toself',
        name='Scores',
        line_color='#0066FF'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=False,
        paper_bgcolor='#0E1117',
        plot_bgcolor='#1E2130',
        font=dict(color='white'),
        height=400
    )
    
    return fig


def generate_qr_code(data: str) -> Image.Image:
    """Generate QR code image."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="white", back_color="black")
    return img


def create_twitter_share_url(name: str, tier: str, address: str) -> str:
    """Create Twitter/X share URL with pre-filled text."""
    text = f"🔷 I'm {name}, a {tier} tier identity on Base L2! Check out Base Identity Protocol:"
    url = f"https://baseidentity.xyz/{address}"  # TODO: Replace with actual domain
    
    params = {
        'text': text,
        'url': url,
        'hashtags': 'BaseIdentity,BaseL2,OnChainIdentity'
    }
    
    return f"https://twitter.com/intent/tweet?{urllib.parse.urlencode(params)}"


def check_payment_status(address: str, recipient: str, amount_eth: float) -> Tuple[bool, str]:
    """
    Check if payment was made by scanning recent transactions.
    Returns (is_paid, tx_hash).
    """
    try:
        # Get recent transactions (simplified - in production, use a proper indexer)
        # For MVP, we'll just check if user has enough balance and let them mark as paid
        # In production, integrate with BaseScan API or similar
        balance = w3.eth.get_balance(w3.to_checksum_address(address))
        balance_eth = balance / 10**18
        
        # Simple check: if balance is sufficient, allow manual confirmation
        # In production, implement proper transaction monitoring
        return False, ""
    except Exception:
        return False, ""


def main():
    # Header
    st.title("🔷 Base Identity Protocol")
    st.markdown("### Discover Your On-Chain Identity on Base L2")
    st.markdown("---")
    
    # Input section
    address = st.text_input(
        "Enter Base Wallet Address",
        placeholder="0x...",
        help="Enter a valid Base Mainnet wallet address"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        generate_btn = st.button("Generate Identity", type="primary", use_container_width=True)
    
    # Process request
    if generate_btn:
        if not address:
            st.error("Please enter a wallet address")
            st.stop()
        
        if not validate_address(address):
            st.error("Invalid wallet address format")
            st.stop()
        
        # Normalize address
        address = w3.to_checksum_address(address)
        
        # Check database first
        existing = get_identity(address)
        
        if existing:
            st.info("📦 Loading cached identity...")
            identity_data = existing
            cached = True
        else:
            st.info("🔄 Generating new identity...")
            
            # Run graph
            graph = create_wallet_identity_graph()
            
            initial_state: GraphState = {
                "address": address,
                "wallet_stats": {},
                "name": "",
                "verdict": "",
                "tier": ""
            }
            
            with st.spinner("Analyzing on-chain data and generating identity..."):
                try:
                    final_state = graph.invoke(initial_state)
                    identity_data = get_identity(address)
                    cached = False
                except Exception as e:
                    st.error(f"Error generating identity: {e}")
                    st.stop()
        
        if identity_data:
            # Display identity
            st.markdown("---")
            
            # Header with name and tier
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"# {identity_data.name}")
            with col2:
                tier_class = get_tier_class(identity_data.tier)
                st.markdown(f'<div class="{tier_class}">{identity_data.tier}</div>', unsafe_allow_html=True)
            
            # Mint status badge
            if identity_data.minted:
                st.markdown('<div class="minted-badge">✨ OFFICIALLY MINTED</div>', unsafe_allow_html=True)
                if identity_data.mint_tx_hash:
                    st.caption(f"Transaction: {identity_data.mint_tx_hash}")
            
            # Verdict
            st.markdown(f'<div class="verdict-box">"{identity_data.verdict}"</div>', unsafe_allow_html=True)
            
            # Action buttons row
            col1, col2 = st.columns(2)
            
            with col1:
                # Mint button
                if not identity_data.minted:
                    st.markdown("### 🪙 Officialize Your Identity")
                    st.markdown(f"**Cost:** {MINT_AMOUNT_ETH} ETH (~$0.50)")
                    st.markdown(f"**Recipient:** `{MINT_RECIPIENT_ADDRESS}`")
                    
                    # Generate payment QR code
                    payment_data = f"ethereum:{MINT_RECIPIENT_ADDRESS}?value={int(MINT_AMOUNT_ETH * 10**18)}"
                    qr_img = generate_qr_code(payment_data)
                    
                    # Display QR code
                    st.image(qr_img, caption="Scan to Pay", width=200)
                    
                    # Payment instructions
                    st.info(f"""
                    **Payment Instructions:**
                    1. Send exactly **{MINT_AMOUNT_ETH} ETH** to:
                       `{MINT_RECIPIENT_ADDRESS}`
                    2. Copy the transaction hash
                    3. Paste it below and click "Confirm Payment"
                    """)
                    
                    # Transaction hash input
                    tx_hash = st.text_input(
                        "Transaction Hash",
                        placeholder="0x...",
                        key="mint_tx_hash",
                        help="Paste the transaction hash after sending payment"
                    )
                    
                    if st.button("✅ Confirm Payment", type="primary", use_container_width=True):
                        if tx_hash:
                            # Verify transaction (simplified - in production, verify on-chain)
                            try:
                                # Mark as minted
                                mark_as_minted(address, tx_hash)
                                st.success("🎉 Identity officially minted!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error confirming payment: {e}")
                        else:
                            st.warning("Please enter the transaction hash")
                else:
                    st.success("✅ Identity is officially minted!")
            
            with col2:
                # Share button
                st.markdown("### 📱 Share Your Identity")
                twitter_url = create_twitter_share_url(
                    identity_data.name,
                    identity_data.tier,
                    address
                )
                
                st.markdown(f"""
                <a href="{twitter_url}" target="_blank" style="text-decoration: none;">
                    <button class="share-button" style="width: 100%;">
                        🐦 Share on X (Twitter)
                    </button>
                </a>
                """, unsafe_allow_html=True)
                
                # Generate shareable QR code
                share_url = f"https://baseidentity.xyz/{address}"  # TODO: Replace with actual domain
                share_qr = generate_qr_code(share_url)
                st.image(share_qr, caption="Share QR Code", width=200)
            
            # Metrics row
            stats = identity_data.stats
            scores = identity_data.scores
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("ETH Balance", f"{stats['eth_balance']:.4f} ETH")
            with col2:
                st.metric("Transactions", f"{stats['tx_count']:,}")
            with col3:
                token_count = len([k for k, v in stats['holdings'].items() if v > 0])
                st.metric("Tokens Held", token_count)
            
            # Radar chart
            st.markdown("### Score Breakdown")
            radar_fig = create_radar_chart(
                scores['wealth_score'],
                scores['vitality_score'],
                scores['community_score']
            )
            st.plotly_chart(radar_fig, use_container_width=True)
            
            # Token badges
            if stats['holdings']:
                st.markdown("### Token Holdings")
                holdings = stats['holdings']
                for token_name, balance in holdings.items():
                    if balance > 0:
                        # Format balance
                        if balance >= 1:
                            balance_str = f"{balance:,.2f}"
                        else:
                            balance_str = f"{balance:.6f}".rstrip('0').rstrip('.')
                        
                        # Emoji mapping
                        emoji_map = {
                            "BRETT": "🚀",
                            "TOSHI": "🐱",
                            "DEGEN": "💎",
                            "AERO": "✈️",
                            "USDC": "💵",
                            "BASE_PAINT": "🎨"
                        }
                        emoji = emoji_map.get(token_name, "🪙")
                        
                        st.markdown(
                            f'<span class="token-badge">{emoji} {token_name}: {balance_str}</span>',
                            unsafe_allow_html=True
                        )
            
            # Cache indicator
            if cached:
                st.caption("ℹ️ This identity was loaded from cache")
            else:
                st.caption("✨ New identity generated and saved")
            
            # Raw data expander
            with st.expander("📊 View Raw Data"):
                st.json({
                    "address": identity_data.address,
                    "name": identity_data.name,
                    "tier": identity_data.tier,
                    "verdict": identity_data.verdict,
                    "stats": stats,
                    "scores": scores,
                    "minted": identity_data.minted,
                    "mint_tx_hash": identity_data.mint_tx_hash,
                    "created_at": str(identity_data.created_at)
                })


if __name__ == "__main__":
    main()
