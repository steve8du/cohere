# Cohere Chat API Service

A REST API service built with FastAPI that integrates Cohere's model with tools like Wikipedia. The service determines when external information is needed and retrieves relevant Wikipedia content to enhance responses.

## Summary
- RESTful chat endpoint with Cohere's latest V2 API
- Introduce Wikipedia tool integration using function calling
- Persistent conversation history with full query/response tracking  

## API Endpoints

#### POST /chat
Send a chat query to the Cohere API with Wikipedia integration.

**Request Body**:
```json
{
  "query": "Who was the second person to walk on the moon?"
}
```

**Response**:
```json
{
  "response": "The second person to walk on the moon was Edwin 'Buzz' Aldrin...",
  "conversation_id": "uuid-string",
  "timestamp": "2025-09-05T10:30:00"
}
```

#### GET /chat/history
Retrieve complete chat history.

**Response**:
```json
{
  "history": [
    {
      "conversation_id": "uuid-string",
      "user_query": "Who was the second person to walk on the moon?",
      "response": "The second person to walk on the moon was Edwin 'Buzz' Aldrin...",
      "timestamp": "2025-09-05T10:30:00",
      "used_wikipedia": true
    }
  ],
  "total_conversations": 1
}
```

## Technical Architecture

### Integration Approach

**Cohere V2 API Integration**: Utilizes Cohere's native function calling capabilities rather than response parsing, providing more reliable tool invocation and better conversation context management.

**Wikipedia Tool Implementation**: Direct integration with Wikipedia's API through the `wikipedia` Python library, with comprehensive error handling for disambiguation pages and missing articles.

## Resources Used

### Documentation & References
- **Cohere API Documentation**: https://docs.cohere.com/v2/reference/chat
- **Cohere Tool Use Guide**: https://docs.cohere.com/docs/tool-use
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Wikipedia API Documentation**: https://wikipedia.readthedocs.io/

### Programming Tool Assistants
- **Cursor**: Utilized for adding test cases

### Key Libraries & Their Rationales
- **FastAPI**: Modern async web framework with automatic API documentation
- **Cohere Python SDK**: Official SDK for reliable API integration  
- **Wikipedia**: Simple library for Wikipedia content access
- **Pydantic**: Type validation and serialization
- **Python-dotenv**: Environment variable management
- **Uvicorn**: ASGI server for FastAPI applications

## Testing

### Manual Testing
To test the application:

1. **Start the server**: `python main.py`
2. **Test basic chat**: 
   ```bash
   curl -X POST "http://localhost:8000/chat" \
        -H "Content-Type: application/json" \
        -d '{"query": "What is the capital of France?"}'
   ```
3. **Test Wikipedia integration**:
   ```bash
   curl -X POST "http://localhost:8000/chat" \
        -H "Content-Type: application/json" \
        -d '{"query": "Tell me about Neil Armstrong"}'
   ```
4. **Test history endpoint**:
   ```bash
   curl "http://localhost:8000/chat/history"
   ```

### Unit Tests
The project includes comprehensive unit tests in `tests/test_services.py` that cover:

#### WikipediaService Tests
- **Successful Wikipedia searches** - Tests retrieval of content with proper formatting
- **Disambiguation handling** - Tests automatic selection of first option when multiple pages exist
- **Page not found scenarios** - Tests error handling for non-existent Wikipedia pages
- **Error edge cases** - Tests various Wikipedia API exceptions

#### ChatHistoryService Tests
- **File persistence** - Tests loading/saving chat history to JSON file
- **Empty state handling** - Tests behavior when no history file exists
- **Entry addition** - Tests adding new conversations with proper metadata
- **Data integrity** - Ensures conversation data is correctly structured

#### ChatService Tests
- **Direct responses** - Tests queries that don't require Wikipedia (math, simple facts)
- **Tool-triggered responses** - Tests Wikipedia integration via function calling
- **Conversation flow** - Tests multi-step tool usage with proper context management
- **History integration** - Tests that all conversations are properly saved with metadata
- **Async operations** - All tests use proper async/await patterns


#### Running Tests
```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src

# Run specific test class
pytest tests/test_services.py::TestWikipediaService
```