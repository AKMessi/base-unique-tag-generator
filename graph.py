import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from database import Database
from analysis import analyze_wallet

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.9
)

def run_identity_agent(address: str):
    # 1. Analyze
    stats = analyze_wallet(address)
    
    # 2. AI Reasoning
    prompt = f"""
    Act as an Onchain Judge. Assign a Creative Title and Verdict for this Base user.
    
    STATS:
    - Wealth: {stats.scores['wealth']}/100
    - Vitality: {stats.scores['vitality']}/100
    - Holdings: {', '.join(stats.holdings)}
    - Tier: {stats.tier}
    
    INSTRUCTIONS:
    - Title: Creative name (2-4 words).
    - Verdict: One savage or complimentary sentence explaining the title.
    
    OUTPUT JSON: {{ "name": "Title", "verdict": "Sentence" }}
    """
    
    try:
        res = llm.invoke([SystemMessage(content="Return JSON only."), HumanMessage(content=prompt)])
        clean = res.content.replace("```json", "").replace("```", "").strip()
        ai_data = json.loads(clean)
        
        final_data = {
            "address": address,
            "name": ai_data["name"],
            "tier": stats.tier,
            "verdict": ai_data["verdict"],
            "stats": stats.model_dump(),
            "scores": stats.scores
        }
        
        db = Database()
        db.save_identity(final_data)
        return final_data
        
    except Exception as e:
        return {"error": str(e)}