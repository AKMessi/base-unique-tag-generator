# Base Identity Protocol - Production Dashboard

A production-ready Streamlit dashboard that analyzes Base L2 wallets and assigns unique on-chain identities using AI.

## Features

- **Justice Algorithm**: Deterministic on-chain analysis (Wealth, Vitality, Community scores)
- **AI-Powered Identity**: Gemini 1.5 Flash generates creative names and verdicts
- **Beautiful UI**: Dark theme with radar charts and token badges
- **Caching**: Instant results for previously analyzed wallets
- **Real-Time Data**: Direct connection to Base Mainnet RPC

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variable**
   Create a `.env` file:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   ```

3. **Run the App**
   ```bash
   streamlit run app.py
   ```

4. **Open Browser**
   The app will open at `http://localhost:8501`

## How It Works

1. Enter a Base wallet address
2. Click "Generate Identity"
3. The system:
   - Analyzes on-chain data (ETH balance, transactions, token holdings)
   - Calculates scores using the Justice Algorithm
   - Generates a creative name and verdict using AI
   - Displays results with visualizations

## Scoring System

- **Wealth Score (30%)**: Based on ETH balance
- **Vitality Score (40%)**: Based on transaction count
- **Community Score (30%)**: Based on token holdings

## Tiers

- **GODLY**: Final score ≥ 85
- **LEGENDARY**: Final score ≥ 65
- **RARE**: Final score ≥ 40
- **COMMON**: Final score < 40

## Supported Tokens

- BRETT, TOSHI, DEGEN, AERO, USDC, BASE_PAINT

## Tech Stack

- Streamlit (Frontend)
- LangGraph (AI Workflow)
- Gemini 1.5 Flash (LLM)
- Web3.py (Blockchain)
- SQLite (Database)
- Plotly (Visualizations)
# base-unique-tag-generator
