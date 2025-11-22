"""
Prompt templates for LLM-based name generation.
"""
from langchain.prompts import ChatPromptTemplate


def get_naming_prompt(temperature: float = 0.7) -> ChatPromptTemplate:
    """
    Get the prompt template for generating wallet identity names.
    
    Args:
        temperature: Temperature for generation (higher = more creative)
        
    Returns:
        ChatPromptTemplate for name generation
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a creative naming agent for cryptocurrency wallets. 
        Based on wallet behavior scores, generate unique, memorable, and gamified names.
        
        Instructions:
        - Names should be creative and thematic (e.g., "Void Walker", "Diamond Handed Ape", "Whale Rider")
        - Names should reflect the wallet's behavior (diamond hands, degen trading, whale activity)
        - Names should sound cool and memorable
        - Names should be 2-4 words typically
        
        Output format: Return ONLY a valid JSON array of exactly 5 name strings. No other text, no markdown, just the JSON array."""),
        ("human", """Generate 5 unique wallet identity names based on these scores:
        
        Diamond Hands Score: {diamond_hands_score}/100
        Degen Score: {degen_score}/100
        Whale Score: {whale_score}/100
        
        Return a JSON array like: ["Name 1", "Name 2", "Name 3", "Name 4", "Name 5"]""")
    ])
    
    return prompt


def get_retry_naming_prompt() -> ChatPromptTemplate:
    """
    Get the prompt template for retry name generation (higher temperature).
    
    Returns:
        ChatPromptTemplate for retry name generation
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a creative naming agent for cryptocurrency wallets. 
        Previous names were already taken. Generate MORE UNIQUE and CREATIVE names.
        
        Instructions:
        - Be even more creative and unusual than before
        - Think outside the box
        - Use more unique combinations and references
        
        Output format: Return ONLY a valid JSON array of exactly 5 name strings. No other text, no markdown, just the JSON array."""),
        ("human", """All previous names were taken. Generate 5 NEW unique wallet identity names based on these scores:
        
        Diamond Hands Score: {diamond_hands_score}/100
        Degen Score: {degen_score}/100
        Whale Score: {whale_score}/100
        
        Return a JSON array like: ["Name 1", "Name 2", "Name 3", "Name 4", "Name 5"]""")
    ])
    
    return prompt

