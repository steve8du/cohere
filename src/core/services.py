import json
import uuid
from datetime import datetime
from pathlib import Path

from cohere import ClientV2

from .config import settings
from .models import ChatHistoryEntry
from ..tools.wikipedia import search_wikipedia, get_tool_definition

# Cohere client management
cohere_client = None

def get_cohere_client():
    global cohere_client
    if cohere_client is None:
        cohere_client = ClientV2(api_key=settings.cohere_api_key)
    return cohere_client

# Main chat processing
async def process_query(query: str):
    conversation_id = str(uuid.uuid4())
    client = get_cohere_client()
    used_wikipedia = False
    
    response = client.chat(
        model=settings.model_name,
        messages=[{"role": "user", "content": query}],
        tools=[get_tool_definition()]
    )
    
    final_text = response.message.content[0].text if response.message.content else ""
    
    if response.message.tool_calls:
        for tool_call in response.message.tool_calls:
            if tool_call.function.name == "search_wikipedia":
                args = json.loads(tool_call.function.arguments)
                wiki_result = search_wikipedia(args.get("query", ""))
                used_wikipedia = True
                
                final_response = client.chat(
                    model=settings.model_name,
                    messages=[
                        {"role": "user", "content": query},
                        {"role": "assistant", "content": final_text or "Let me search for information."},
                        {"role": "user", "content": f"Wikipedia info: {wiki_result}\n\nAnswer the original question."}
                    ]
                )
                final_text = final_response.message.content[0].text
                break
    
    add_to_history(conversation_id, query, final_text, used_wikipedia)
    
    return {
        "response": final_text,
        "conversation_id": conversation_id,
        "timestamp": datetime.now().isoformat(),
        "used_wikipedia": used_wikipedia
    }


# Chat history management
def load_history():
    if not Path(settings.history_file).exists():
        return []
    try:
        with open(settings.history_file, 'r') as f:
            data = json.load(f)
            return [ChatHistoryEntry(**entry) for entry in data]
    except:
        return []

def save_history(history):
    with open(settings.history_file, 'w') as f:
        json.dump([entry.model_dump() for entry in history], f, indent=2)

def add_to_history(conversation_id: str, user_query: str, response: str, used_wikipedia: bool):
    history = load_history()
    history.append(ChatHistoryEntry(
        conversation_id=conversation_id,
        user_query=user_query,
        response=response,
        timestamp=datetime.now().isoformat(),
        used_wikipedia=used_wikipedia
    ))
    save_history(history)

async def get_history():
    history = load_history()
    return {
        "history": history,
        "total_conversations": len(history)
    }
