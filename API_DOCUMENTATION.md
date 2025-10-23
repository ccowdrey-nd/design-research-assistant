# Design Assistant API Documentation

Base URL: `http://localhost:8000` (development) or your production domain

All endpoints except `/api/health` require Okta JWT authentication via Bearer token.

## Authentication

All authenticated endpoints require an `Authorization` header:

```
Authorization: Bearer <okta-jwt-token>
```

The frontend handles this automatically via the Okta React SDK.

---

## Endpoints

### Health Check

**GET** `/api/health`

Check API health and service availability.

**Authentication:** Not required

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "openai": true,
    "figma": true,
    "google_slides": true
  }
}
```

---

### Chat (Streaming)

**POST** `/api/chat`

Send a message and receive a streaming response with RAG context.

**Authentication:** Required

**Request Body:**
```json
{
  "message": "What are our brand colors?",
  "conversation_history": [
    {
      "role": "user",
      "content": "Previous message"
    },
    {
      "role": "assistant",
      "content": "Previous response"
    }
  ]
}
```

**Response:**

Server-Sent Events (SSE) stream:

```
data: {"content": "Our brand"}
data: {"content": " colors are..."}
data: {"sources": [{"name": "Brand Colors", "url": "..."}]}
data: [DONE]
```

---

### Chat (Simple)

**POST** `/api/chat-simple`

Send a message and receive a complete response (non-streaming).

**Authentication:** Required

**Request Body:**
```json
{
  "message": "What are our brand colors?",
  "conversation_history": []
}
```

**Response:**
```json
{
  "response": "Our brand colors include...",
  "sources": [
    {
      "name": "Brand Colors",
      "source": "figma",
      "type": "color",
      "url": "https://www.figma.com/file/..."
    }
  ]
}
```

---

### Analyze Image

**POST** `/api/analyze-image`

Upload an image for brand compliance analysis.

**Authentication:** Required

**Request:**

Multipart form data with file upload:

```
file: <image-file>
```

**Supported formats:** PNG, JPG, JPEG, GIF, WebP

**Response:**
```json
{
  "analysis": "## Color Usage\n\nThe colors used in this creative...",
  "sources": [
    {
      "name": "Brand Colors",
      "source": "figma",
      "type": "color",
      "url": "https://www.figma.com/file/..."
    }
  ],
  "recommendations": [
    "Use the primary brand blue instead of the current shade",
    "Increase logo size to meet minimum requirements"
  ]
}
```

---

### Sync Figma

**POST** `/api/sync/figma`

Sync design system data from Figma to the vector database.

**Authentication:** Required

**Request Body:**
```json
{
  "force": false
}
```

**Response:**
```json
{
  "status": "success",
  "synced_files": [
    {
      "file_key": "AbCdEfGhIj",
      "name": "Design System",
      "components": 45,
      "styles": 23
    }
  ],
  "total_documents": 150
}
```

---

### Sync Google Slides

**POST** `/api/sync/slides`

Sync design documentation from Google Slides to the vector database.

**Authentication:** Required

**Request Body:**
```json
{
  "force": false
}
```

**Response:**
```json
{
  "status": "success",
  "synced_presentations": [
    {
      "name": "Brand Guidelines 2024",
      "slides": 25
    }
  ],
  "total_documents": 175
}
```

---

### Get Stats

**GET** `/api/stats`

Get statistics about the vector database.

**Authentication:** Required

**Response:**
```json
{
  "total_documents": 150,
  "collection_name": "design_system"
}
```

---

### Search

**POST** `/api/search`

Search the design system directly (useful for testing).

**Authentication:** Required

**Query Parameters:**
- `query` (required): Search query string
- `top_k` (optional): Number of results, default: 5

**Response:**
```json
{
  "documents": [
    "Color Style: Primary Blue\nDescription: Main brand color...",
    "Component: Button\nDescription: Primary action button..."
  ],
  "metadatas": [
    {
      "source": "figma",
      "type": "color",
      "name": "Primary Blue",
      "file_key": "AbCdEfGhIj",
      "url": "https://www.figma.com/file/..."
    }
  ],
  "distances": [0.15, 0.23]
}
```

---

## Error Responses

### 400 Bad Request

```json
{
  "detail": "Invalid image file"
}
```

### 401 Unauthorized

```json
{
  "detail": "Invalid authentication credentials"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Rate Limiting

Currently no rate limiting is implemented. For production, consider:

- Adding rate limiting middleware
- Implementing per-user quotas
- Caching frequent queries

---

## Webhook Support (Future)

Future versions may support webhooks for:

- Automatic Figma file updates
- Scheduled syncs
- Status notifications

---

## SDK/Client Libraries

### JavaScript/TypeScript

Use the included `api.js` client:

```javascript
import apiClient from './api';

// Set auth token
apiClient.setAuthToken(token);

// Send message
const response = await apiClient.sendMessage('What are our brand colors?');

// Analyze image
const analysis = await apiClient.analyzeImage(file);

// Sync Figma
const syncResult = await apiClient.syncFigma();
```

### Python

Example Python client:

```python
import requests

BASE_URL = "http://localhost:8000"
headers = {"Authorization": f"Bearer {token}"}

# Send message
response = requests.post(
    f"{BASE_URL}/api/chat-simple",
    headers=headers,
    json={"message": "What are our brand colors?"}
)
```

---

## OpenAPI/Swagger Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

These interfaces allow you to:
- View all endpoints
- See request/response schemas
- Test endpoints interactively

---

## Best Practices

### Conversation History

- Keep last 5-10 messages for context
- Don't send entire chat history (expensive)
- Clear history for new topics

### Image Analysis

- Resize large images before upload (< 4MB)
- Use common formats (PNG, JPG)
- Include context in file names

### Data Syncing

- Run syncs during off-hours
- Don't sync too frequently (once daily is enough)
- Monitor sync results for errors

### Error Handling

- Always handle network errors
- Retry failed requests with exponential backoff
- Show user-friendly error messages

---

## Support

For API issues or questions, contact your internal development team.

