"""
Main CLI entry point for Wallet Identity Protocol.
"""
import os
import sys
from dotenv import load_dotenv

from graph import create_wallet_identity_graph, GraphState
from database import Database


def main():
    """Main CLI function."""
    # Load environment variables
    load_dotenv()
    
    # Check for Google API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("ERROR: GOOGLE_API_KEY not found in environment variables.")
        print("Please create a .env file with your Google API key:")
        print("GOOGLE_API_KEY=your_key_here")
        sys.exit(1)
    
    print("=" * 60)
    print("  WALLET IDENTITY PROTOCOL")
    print("=" * 60)
    print()
    
    # Initialize database
    db = Database()
    
    # Get wallet address from user
    address = input("Enter wallet address: ").strip()
    
    if not address:
        print("Error: Wallet address cannot be empty.")
        sys.exit(1)
    
    # Check if address already exists
    existing = db.get_identity(address)
    if existing:
        print(f"\n✓ Wallet already registered!")
        print(f"  Name: {existing.generated_name}")
        print(f"  Tier: {existing.tier}")
        print(f"  Stats: {existing.stats}")
        print(f"  Created: {existing.created_at}")
        return
    
    print(f"\n🚀 Starting analysis for wallet: {address}")
    print("-" * 60)
    
    # Create and run the graph
    graph = create_wallet_identity_graph()
    
    # Initial state
    initial_state: GraphState = {
        "address": address,
        "wallet_stats": None,
        "scores": None,
        "tier": "",
        "generated_names": [],
        "current_name_index": 0,
        "registered_name": None,
        "is_retry": False
    }
    
    # Run the workflow
    try:
        final_state = graph.invoke(initial_state)
        
        print("\n" + "=" * 60)
        print("  ✓ IDENTITY ASSIGNED SUCCESSFULLY")
        print("=" * 60)
        print(f"  Address: {final_state['address']}")
        print(f"  Name: {final_state['registered_name']}")
        print(f"  Tier: {final_state['tier']}")
        
        # Reconstruct scores from dict for display
        from analysis import WalletScores
        scores = WalletScores(**final_state['scores'])
        print(f"  Diamond Hands: {scores.diamond_hands_score}/100")
        print(f"  Degen Score: {scores.degen_score}/100")
        print(f"  Whale Score: {scores.whale_score}/100")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
