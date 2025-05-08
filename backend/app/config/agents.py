"""
Configuration for different AI agents/models available in the application.
Each agent is configured with a unique ID, model name, display name, and description.
"""

AVAILABLE_AGENTS = {
    "mistral": {
        "id": "mistral",
        "model": "mistralai/mistral-small-3.1-24b-instruct:free",
        "display_name": "Mistral (Default)",
        "description": "Mistral Small 3.1 - 24B instruction model. Great for general questions.",
        "avatar": "🧠", 
        "temperature": 0.7,
        "is_default": True
    },
    "gemma": {
        "id": "gemma",
        "model": "google/gemma-3-4b-it:free",
        "display_name": "Gemma",
        "description": "Google's Gemma 3 - 4B instruction model. Balances efficiency and knowledge.",
        "avatar": "🔍",
        "temperature": 0.7,
        "is_default": False
    },
    "deepseek": {
        "id": "deepseek",
        "model": "deepseek/deepseek-chat-v3-0324:free",
        "display_name": "DeepSeek",
        "description": "DeepSeek Chat v3 - Excels at technical topics and detailed explanations.",
        "avatar": "🔬",
        "temperature": 0.6,
        "is_default": False
    },
    "llama": {
        "id": "llama",
        "model": "meta-llama/llama-4-maverick:free",
        "display_name": "Llama 4",
        "description": "Meta's Llama 4 Maverick model - Creative and diverse responses.",
        "avatar": "🦙",
        "temperature": 0.75,
        "is_default": False
    },
    "qwen": {
        "id": "qwen",
        "model": "qwen/qwen3-30b-a3b:free",
        "display_name": "Qwen",
        "description": "Alibaba's Qwen3 30B model - Very knowledgeable and precise.",
        "avatar": "⚡",
        "temperature": 0.65,
        "is_default": False
    }
}

# Helper function to get agent by ID
def get_agent(agent_id):
    """
    Retrieves agent configuration by ID.
    Falls back to default agent if requested ID doesn't exist.
    
    Args:
        agent_id (str): The ID of the agent to retrieve
        
    Returns:
        dict: Agent configuration dictionary
    """
    if agent_id in AVAILABLE_AGENTS:
        return AVAILABLE_AGENTS[agent_id]
    
    # Return default agent if requested agent isn't found
    for agent in AVAILABLE_AGENTS.values():
        if agent.get("is_default", False):
            return agent
    
    # Fallback to first agent if no default is set
    return list(AVAILABLE_AGENTS.values())[0]

# Helper function to get all available agents
def get_all_agents():
    """
    Returns a list of all available agents.
    
    Returns:
        list: List of agent configuration dictionaries
    """
    return list(AVAILABLE_AGENTS.values()) 