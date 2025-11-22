"""
LangGraph workflow for Base Identity Protocol AI Agent.
"""
from typing import TypedDict, Literal
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

from analysis import analyze_wallet
from database import get_identity, save_identity

load_dotenv()

class GraphState(TypedDict):
    """State for the LangGraph workflow."""
    address: str
    wallet_stats: dict
    name: str
    verdict: str
    tier: str


def analyst_node(state: GraphState) -> GraphState:
    """Node 1: Analyze wallet using Justice Algorithm."""
    address = state['address']
    
    # Analyze wallet
    wallet_stats = analyze_wallet(address)
    
    # Convert to dict for state
    state['wallet_stats'] = wallet_stats.model_dump()
    state['tier'] = wallet_stats.tier
    
    return state


def identity_node(state: GraphState) -> GraphState:
    """Node 2: Generate identity name and verdict using AI."""
    wallet_stats = state['wallet_stats']
    tier = state['tier']
    
    # Extract key information for prompt
    eth_balance = wallet_stats['eth_balance']
    tx_count = wallet_stats['tx_count']
    holdings = wallet_stats['holdings']
    wealth_score = wallet_stats['wealth_score']
    vitality_score = wallet_stats['vitality_score']
    community_score = wallet_stats['community_score']
    
    # Build context for AI
    holdings_list = list(holdings.keys()) if holdings else []
    has_brett = 'BRETT' in holdings_list
    has_base_paint = 'BASE_PAINT' in holdings_list
    
    # Create prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an Onchain Judge analyzing cryptocurrency wallet behavior on Base L2.
        
        Your task is to assign a Creative Name (Title) and a 1-sentence Verdict based on the wallet's on-chain activity.
        
        Naming Guidelines:
        - If Tier is GODLY: Use terms like "Titan", "Apex", "Sovereign", "Legend"
        - If Tier is LEGENDARY: Use terms like "Champion", "Master", "Elite"
        - If Tier is RARE: Use terms like "Warrior", "Explorer", "Voyager"
        - If Tier is COMMON: Use terms like "Citizen", "Member", "User"
        - If BRETT token is held: Include 'Degen' or 'Based' references
        - If BASE_PAINT token is held: Include 'Art' or 'Creator' references
        - Be creative and memorable (2-4 words typically)
        
        Verdict Guidelines:
        - Write ONE compelling sentence that captures the wallet's essence
        - Reference their activity level, wealth, or community participation
        - Be poetic but accurate
        
        Return ONLY valid JSON with "name" and "verdict" keys. No markdown, no extra text."""),
        ("human", """Analyze this wallet:
        
        Tier: {tier}
        ETH Balance: {eth_balance:.4f} ETH
        Transaction Count: {tx_count}
        Tokens Held: {holdings_list}
        Wealth Score: {wealth_score}/100
        Vitality Score: {vitality_score}/100
        Community Score: {community_score}/100
        
        Generate a creative name and verdict.""")
    ])
    
    # Initialize LLM
    llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0.8)
    
    # Create chain
    chain = prompt | llm | JsonOutputParser()
    
    try:
        result = chain.invoke({
            "tier": tier,
            "eth_balance": eth_balance,
            "tx_count": tx_count,
            "holdings_list": ", ".join(holdings_list) if holdings_list else "None",
            "wealth_score": wealth_score,
            "vitality_score": vitality_score,
            "community_score": community_score
        })
        
        state['name'] = result.get('name', 'Unknown Identity')
        state['verdict'] = result.get('verdict', 'A wallet on Base.')
        
    except Exception as e:
        # Fallback if AI fails
        state['name'] = f"Base {tier} Wallet"
        state['verdict'] = f"A {tier.lower()} tier wallet on Base with {tx_count} transactions."
    
    return state


def save_node(state: GraphState) -> GraphState:
    """Node 3: Save identity to database."""
    address = state['address']
    wallet_stats = state['wallet_stats']
    
    # Prepare data for database
    data = {
        'address': address,
        'name': state['name'],
        'tier': state['tier'],
        'verdict': state['verdict'],
        'stats': {
            'eth_balance': wallet_stats['eth_balance'],
            'tx_count': wallet_stats['tx_count'],
            'holdings': wallet_stats['holdings']
        },
        'scores': {
            'wealth_score': wallet_stats['wealth_score'],
            'vitality_score': wallet_stats['vitality_score'],
            'community_score': wallet_stats['community_score'],
            'final_score': wallet_stats['final_score']
        }
    }
    
    # Save to database
    save_identity(data)
    
    return state


def create_wallet_identity_graph():
    """Create and compile the LangGraph workflow."""
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("identity", identity_node)
    workflow.add_node("save", save_node)
    
    # Add edges
    workflow.set_entry_point("analyst")
    workflow.add_edge("analyst", "identity")
    workflow.add_edge("identity", "save")
    workflow.add_edge("save", END)
    
    return workflow.compile()
