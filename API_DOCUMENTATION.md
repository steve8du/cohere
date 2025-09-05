# Cohere Chat API Documentation

## Base URL
```
http://localhost:8000
```
## Endpoints

### 1. Root Information
**GET /**

Returns API information and available endpoints.

#### Response
```json
{
  "message": "Cohere Chat API with Wikipedia Integration",
  "endpoints": {
    "POST /chat": "Send a query to Cohere Chat API with Wikipedia tool integration",
    "GET /chat/history": "Retrieve complete chat history",
  },
  "version": "1.0.0"
}
```

---

### 2. Chat Query
**POST /chat**

Process a chat query with automatic Wikipedia tool integration when needed.

#### Request Body
```json
{
  "query": "string (required, min: 1 char, max: 5000 chars)"
}
```

#### Response
```json
{
  "response": "string - The AI-generated response",
  "conversation_id": "string - Unique UUID for this conversation",
  "timestamp": "string - ISO 8601 timestamp",
  "used_wikipedia": "boolean - Whether Wikipedia was searched"
}
```

#### Examples

##### Basic Question (No Wikipedia)
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is 2+2?"}'
```

Response:
```json
{
  "response": "2 + 2 = 4",
  "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
  "timestamp": "2025-09-04T22:17:31.849643",
  "used_wikipedia": false
}
```

##### Historical Query
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "Tell me about Albert Einstein"}'
```

Response:
```json
{
  "response": "Albert Einstein (1879-1955) was a German-born theoretical physicist...",
  "conversation_id": "456e7890-e89b-12d3-a456-426614174000",
  "timestamp": "2025-09-04T22:18:45.123456",
  "used_wikipedia": true
}
```

#### Error Responses

##### 400 Bad Request
```json
{
  "detail": "Invalid request format or missing required fields"
}
```

##### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "query"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

##### 500 Internal Server Error
```json
{
  "detail": "An error occurred while processing your request. Please try again."
}
```

---

### 4. Chat History
**GET /chat/history**

Retrieve complete chat history with all conversations.

#### Response
```json
{
  "history": [
    {
      "conversation_id": "string",
      "user_query": "string",
      "response": "string",
      "timestamp": "string",
      "used_wikipedia": "boolean"
    }
  ],
  "total_conversations": "integer"
}
```

#### Example
```bash
curl -X GET "http://localhost:8000/chat/history"
```

---

## Rate Limits
- Development: No rate limits
- Production: Implement rate limiting (suggested: 100 requests/minute per IP)

## Response Times
- Basic queries: ~1-3 seconds
- Wikipedia searches: ~3-7 seconds (includes Wikipedia API call)

## Error Handling
- All errors return appropriate HTTP status codes
- Error messages are user-friendly and don't expose internal details
- Detailed error logging on server side

## Data Storage
- Chat history stored in `chat_history.json`
- In production, migrate to database (PostgreSQL/MongoDB)

## Tool Integration

### Wikipedia Tool
The API automatically determines when to search Wikipedia based on the query context.

**Triggers Wikipedia search for:**
- Historical figures and events
- Scientific concepts and theories
- Geographic locations and landmarks
- Technical definitions requiring current information
