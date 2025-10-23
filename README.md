# Design & Research Assistant

A powerful AI-powered design assistant that integrates with Figma, Google Slides, and provides brand compliance analysis for Nextdoor's design team.

## Features

### 🎨 **Figma Integration**
- **File Search**: Search and link to any Figma file across your team
- **Asset Export**: Export any asset from the Brand Asset Kit as SVG with custom colors
- **Visual Examples**: Show visual examples of components directly in chat
- **Real-time Activity**: Get the latest modified files from your team

### 📊 **Google Slides Integration**
- **UXR Deck Access**: Search and synthesize findings from research presentations
- **Recursive Search**: Automatically indexes all subfolders in your UXR library
- **Research Insights**: Get AI-powered summaries of research findings

### 🔍 **Image Analysis**
- **Brand Compliance**: Upload designs to check against brand guidelines
- **Component Analysis**: Compare buttons against Blocks 3.0 kit
- **Creative Type Detection**: Automatically detects email vs. ad designs
- **Approved Examples**: References approved designs for comparison

### 🏢 **Organizational Intelligence**
- **Team Structure**: Answer questions about design organization and ownership
- **Business Verticals**: Know who owns what business areas
- **Design Leadership**: Access to organizational charts and team structure

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+ (for frontend)
- Figma API token
- OpenAI API key
- Google Cloud credentials (for Slides integration)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd design-assistant
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

5. **Run the Application**
   ```bash
   # Terminal 1 - Backend
   cd backend
   source venv/bin/activate
   python main.py

   # Terminal 2 - Frontend
   cd frontend
   npm start
   ```

## Configuration

### Required Environment Variables

```bash
# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Figma
FIGMA_ACCESS_TOKEN=your_figma_token
FIGMA_TEAM_ID=your_team_id

# Google Slides (Optional)
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
GOOGLE_SLIDES_FOLDER_ID=your_uxr_folder_id

# ChromaDB (Vector Database)
CHROMA_PERSIST_DIRECTORY=./chroma_db
```

### Figma Setup
1. Get your Figma access token from [Figma Account Settings](https://www.figma.com/developers/api#authentication)
2. Find your Team ID in your Figma team URL
3. Update the `FIGMA_FILE_KEYS` in `backend/config.py` with your key files

### Google Slides Setup
1. Create a Google Cloud Project
2. Enable Google Slides API
3. Create a service account and download credentials
4. Share your UXR folder with the service account email

## Usage Examples

### Asset Export
```
"Export the primary logo in Lawn green"
"Download the house icon in Dusk"
"Show me the chat icon in our brand colors"
```

### File Search
```
"Find the SMB email templates"
"Show me the latest design system updates"
"What are the recent files from the design team?"
```

### Image Analysis
```
Upload any design and get:
- Brand compliance analysis
- Component comparison against Blocks 3.0
- Color and typography feedback
- Approved example references
```

### Research Insights
```
"What did we learn from the user research on neighborhood engagement?"
"Show me insights from the mobile app usability study"
"Find research on user onboarding flows"
```

## Architecture

### Backend (FastAPI)
- **`main.py`**: API endpoints and chat logic
- **`integrations/figma.py`**: Figma API integration
- **`integrations/google_slides.py`**: Google Slides integration
- **`analyzer.py`**: Image analysis and brand compliance
- **`rag/`**: Vector database and retrieval system

### Frontend (React)
- **`src/App.js`**: Main application component
- **`src/components/ChatWindow.js`**: Chat interface
- **`src/components/ChatWindow.css`**: Styling

### Key Technologies
- **FastAPI**: Backend API framework
- **React**: Frontend framework
- **ChromaDB**: Vector database for RAG
- **OpenAI GPT-4**: Language model and vision analysis
- **Figma API**: Design asset access
- **Google Slides API**: Research deck integration

## Deployment

### Option 1: Vercel (Recommended)
1. Connect your GitHub repository to Vercel
2. Configure environment variables in Vercel dashboard
3. Deploy automatically on push to main branch

### Option 2: Railway
1. Connect GitHub repository to Railway
2. Add environment variables
3. Deploy with automatic scaling

### Option 3: Docker
```bash
# Build and run with Docker
docker build -t design-assistant .
docker run -p 8000:8000 -p 3000:3000 design-assistant
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For questions or issues:
1. Check the troubleshooting guide
2. Review the API documentation
3. Open an issue on GitHub

## License

This project is proprietary to Nextdoor and intended for internal use only.