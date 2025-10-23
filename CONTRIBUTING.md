# Contributing to Design Assistant

Thank you for contributing to the Design Assistant project!

## Development Setup

Follow the [SETUP_GUIDE.md](SETUP_GUIDE.md) to set up your development environment.

## Code Structure

### Backend (`/backend`)

- **`main.py`**: FastAPI application and endpoints
- **`config.py`**: Environment configuration
- **`auth.py`**: Okta authentication middleware
- **`analyzer.py`**: Image analysis with GPT-4 Vision
- **`integrations/`**: External API clients (Figma, Google Slides)
- **`rag/`**: RAG pipeline (embeddings, retrieval)

### Frontend (`/frontend`)

- **`App.js`**: Main application with routing
- **`api.js`**: Backend API client
- **`components/`**: React components

## Adding New Features

### Adding a New Data Source

1. Create integration client in `backend/integrations/`
2. Add sync method to extract and structure data
3. Update `embeddings.py` to handle new document type
4. Add sync endpoint in `main.py`
5. Add sync button in `AdminPanel.js`

Example structure:
```python
# backend/integrations/your_source.py
class YourSourceClient:
    def get_data(self):
        # Fetch data from API
        pass
    
    def extract_content(self, data):
        # Structure data for embedding
        pass
```

### Adding a New Chat Feature

1. Update system prompt in `main.py`
2. Add any specialized retrieval logic in `retrieval.py`
3. Create UI component if needed
4. Test with various queries

### Adding a New Analysis Type

1. Add analysis method to `analyzer.py`
2. Create new endpoint in `main.py`
3. Add UI in `ImageAnalyzer.js` or create new component
4. Update frontend routing if necessary

## Code Style

### Python (Backend)

- Follow PEP 8
- Use type hints where applicable
- Document functions with docstrings
- Keep functions focused and single-purpose

Example:
```python
def sync_data(source: str, force: bool = False) -> Dict[str, Any]:
    """
    Sync data from external source.
    
    Args:
        source: The data source identifier
        force: Force full resync if True
        
    Returns:
        Sync results dictionary
    """
    pass
```

### JavaScript (Frontend)

- Use functional components with hooks
- Keep components focused
- Use meaningful variable names
- Comment complex logic

Example:
```javascript
/**
 * Fetch and display analysis results.
 */
const handleAnalyze = async () => {
    // Implementation
};
```

## Testing

### Backend Testing

```bash
cd backend
source venv/bin/activate
pytest tests/
```

### Frontend Testing

```bash
cd frontend
npm test
```

## Committing Changes

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes

3. Test thoroughly:
   - Run backend server and test endpoints
   - Test frontend UI
   - Check for console errors

4. Commit with descriptive message:
   ```bash
   git commit -m "Add feature: description"
   ```

5. Push and create pull request:
   ```bash
   git push origin feature/your-feature-name
   ```

## Pull Request Guidelines

- Describe what the PR does
- Reference any related issues
- Include screenshots for UI changes
- Ensure all tests pass
- Update documentation if needed

## Common Development Tasks

### Update Dependencies

**Backend:**
```bash
cd backend
pip install --upgrade package-name
pip freeze > requirements.txt
```

**Frontend:**
```bash
cd frontend
npm update package-name
```

### Add Environment Variable

1. Add to `backend/config.py` Settings class
2. Add to `backend/env.example`
3. Update SETUP_GUIDE.md
4. Document in README.md

### Debugging

**Backend:**
- Set `DEBUG=True` in `.env`
- Check terminal output
- Add print statements or use debugger

**Frontend:**
- Check browser console
- Use React DevTools
- Check Network tab for API calls

## Architecture Decisions

### Why ChromaDB?

- Lightweight, embedded vector store
- No separate database server needed
- Fast semantic search
- Easy to deploy

### Why FastAPI?

- Modern, fast Python framework
- Built-in async support
- Automatic API documentation
- Easy to test

### Why React?

- Component-based architecture
- Large ecosystem
- Good developer experience
- Okta has official React SDK

## Performance Considerations

### Backend

- Use async/await for I/O operations
- Cache expensive API calls
- Batch embeddings creation
- Limit context size for LLM calls

### Frontend

- Lazy load components
- Minimize re-renders
- Use React.memo for expensive components
- Optimize images before upload

## Security Best Practices

- Never commit API keys or secrets
- Validate all user inputs
- Use HTTPS in production
- Keep dependencies updated
- Follow OWASP guidelines

## Getting Help

- Check existing issues on the repository
- Review documentation
- Ask in team chat
- Contact project maintainers

## License

Internal use only - proprietary

