import streamlit as st
import plotly.graph_objects as go
import urllib.parse
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from database import Database
from graph import run_identity_agent
from analysis import RPC_URL
from web3 import Web3

# Page config
st.set_page_config(page_title="Base Identity Protocol", page_icon="🔵", layout="centered")

# Initialize Web3
w3 = Web3(Web3.HTTPProvider(RPC_URL))

def validate_address(address: str) -> bool:
    return w3.is_address(address)

# --- LIGHT MODE CSS ---
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; color: #000000; }
    .identity-card {
        background: linear-gradient(145deg, #ffffff, #f8f9fa);
        padding: 2rem;
        border-radius: 20px;
        border: 1px solid #E0E6ED;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        text-align: center;
        margin-bottom: 20px;
    }
    .tier-badge { font-size: 24px; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; padding: 5px 15px; border-radius: 50px; }
    .tier-godly { background: #FFF8E1; color: #D4AF37; border: 1px solid #D4AF37; }
    .tier-legendary { background: #F3E5F5; color: #800080; border: 1px solid #800080; }
    .tier-rare { background: #E3F2FD; color: #0052FF; border: 1px solid #0052FF; }
    .tier-common { background: #F5F5F5; color: #555555; border: 1px solid #999; }
    
    .verdict-text { font-style: italic; color: #333; margin-top: 10px; font-size: 18px; }
    .token-badge { display: inline-block; background: #F0F2F6; padding: 2px 10px; border-radius: 10px; margin: 2px; font-size: 12px; border: 1px solid #ddd; }
    
    .share-btn {
        display: flex; align-items: center; justify-content: center;
        background-color: #000000; color: white !important;
        padding: 12px 24px; border-radius: 50px; text-decoration: none;
        font-weight: bold; margin-top: 10px; width: 100%;
    }
    .share-btn:hover { opacity: 0.8; }
</style>
""", unsafe_allow_html=True)

def get_tier_class(tier):
    return f"tier-{tier.lower()}"

def create_badge_image(data):
    W, H = 800, 400
    img = Image.new('RGB', (W, H), color='#FFFFFF')
    draw = ImageDraw.Draw(img)
    blue, black, grey = "#0052FF", "#000000", "#555555"
    
    draw.rectangle([(0,0), (W,15)], fill=blue)
    draw.rectangle([(0,H-15), (W,H)], fill=blue)
    
    try:
        font_lg = ImageFont.truetype("arial.ttf", 50)
        font_md = ImageFont.truetype("arial.ttf", 30)
        font_sm = ImageFont.truetype("arial.ttf", 20)
    except:
        font_lg = ImageFont.load_default()
        font_md = ImageFont.load_default()
        font_sm = ImageFont.load_default()

    draw.text((W/2, 60), data['tier'], font=font_md, fill=blue, anchor="mm")
    draw.text((W/2, 140), data['name'], font=font_lg, fill=black, anchor="mm")
    
    verdict = data['verdict'][:60] + "..." if len(data['verdict']) > 60 else data['verdict']
    draw.text((W/2, 220), f'"{verdict}"', font=font_sm, fill=grey, anchor="mm")
    
    stats_txt = f"Wealth: {data['scores']['wealth']} | Vitality: {data['scores']['vitality']} | Community: {data['scores']['community']}"
    draw.text((W/2, 320), stats_txt, font=font_sm, fill=black, anchor="mm")
    
    return img

def main():
    st.title("🔵 Base Identity Protocol")
    st.caption("Discover Your On-Chain Reputation")
    
    address = st.text_input("Enter Base Address:", placeholder="0x...")
    
    if st.button("🔍 Analyze Wallet", type="primary", use_container_width=True):
        if not address or not validate_address(address):
            st.warning("Please enter a valid address.")
            st.stop()
            
        address = w3.to_checksum_address(address)
        db = Database()
        record = db.get_identity(address)
        
        if record:
            data = {"name": record.name, "tier": record.tier, "verdict": record.verdict, "stats": record.stats, "scores": record.scores}
            st.success("Identity Loaded")
        else:
            with st.spinner("Analyzing Chain..."):
                data = run_identity_agent(address)
                if "error" in data:
                    st.error(data["error"])
                    st.stop()

        # DASHBOARD
        tier_class = get_tier_class(data['tier'])
        st.markdown(f"""
        <div class="identity-card">
            <span class="tier-badge {tier_class}">{data['tier']}</span>
            <h1 style="margin: 10px 0; color: black;">{data['name']}</h1>
            <p class="verdict-text">"{data['verdict']}"</p>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("ETH Balance", f"{data['stats']['eth_balance']:.3f}")
        c2.metric("Transactions", data['stats']['tx_count'])
        c3.metric("Score", f"{data['scores']['final']}/100")

        # RADAR
        fig = go.Figure(data=go.Scatterpolar(
            r=[data['scores']['wealth'], data['scores']['vitality'], data['scores']['community']],
            theta=['Wealth', 'Vitality', 'Community'],
            fill='toself',
            line_color='#0052FF'
        ))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, height=300, margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

        # SHARE
        st.divider()
        st.markdown("### 🚀 Go Viral")
        
        # Generate Image
        badge_img = create_badge_image(data)
        buf = BytesIO()
        badge_img.save(buf, format="PNG")
        
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("⬇️ Download Badge", data=buf.getvalue(), file_name="identity.png", mime="image/png", use_container_width=True)
        with c2:
            share_text = f"I am the {data['name']} ({data['tier']}). Verified on Base Identity Protocol. 🔵\n\nCheck your status:"
            share_link = f"https://twitter.com/intent/tweet?text={urllib.parse.quote(share_text)}&url=https://base.org"
            st.markdown(f'<a href="{share_link}" target="_blank" class="share-btn">🐦 Post on X</a>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()