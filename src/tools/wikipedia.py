import wikipedia

def search_wikipedia(query: str, sentences: int = 3) -> str:
    try:
        summary = wikipedia.summary(query, sentences=sentences)
        page = wikipedia.page(query)
        return f"Wikipedia Summary: {summary}\n\nSource: {page.url}"
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Multiple pages found. Top options: {', '.join(e.options[:5])}"
    except wikipedia.exceptions.PageError:
        return f"No Wikipedia page found for '{query}'"
    except Exception as e:
        return f"Error searching Wikipedia: {str(e)}"

def get_tool_definition():
    return {
        "type": "function",
        "function": {
            "name": "search_wikipedia",
            "description": "Search Wikipedia for information about a topic",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to look up on Wikipedia"
                    }
                },
                "required": ["query"]
            }
        }
    }