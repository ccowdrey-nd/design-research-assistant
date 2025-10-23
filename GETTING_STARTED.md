# Getting Started with Your Design Assistant

## ✅ What's Been Completed

Your Design Assistant chatbot is fully built and configured! Here's what's set up:

### Backend (FastAPI + Python)
- ✅ FastAPI server running on http://localhost:8000
- ✅ OpenAI integration (GPT-4 + GPT-4 Vision)
- ✅ Figma API integration
- ✅ ChromaDB vector database
- ✅ RAG (Retrieval-Augmented Generation) pipeline
- ✅ Image brand compliance analyzer
- ✅ Authentication bypassed for development testing

### Configured Figma Files
- ✅ **Blocks 3.0** - Your brand style kit (last updated: 2025-10-13)
- ✅ **Brand Asset Kit 2025** - Your brand assets (last updated: 2025-10-21)

### Your API Keys
- ✅ OpenAI API Key: Configured
- ✅ Figma Access Token: Configured
- ✅ Figma Team ID: 425727601495451236

---

## ⚠️ Action Required: Fix OpenAI Quota

Your OpenAI API key has **exceeded its quota**. To use the chatbot, you need to:

### Steps to Fix:

1. **Go to OpenAI Platform**: https://platform.openai.com/account/billing

2. **Add Payment Method**:
   - Click "Add payment method"
   - Enter your credit card details

3. **Add Credits** (if using prepaid):
   - Click "Add to credit balance"
   - Add at least $5-10 to start

   **OR**

4. **Enable Auto-Recharge** (recommended):
   - Set up automatic billing
   - Set a monthly limit (e.g., $20-50)

5. **Verify**: After adding billing, wait 1-2 minutes, then test:
   ```bash
   curl -X POST http://localhost:8000/api/chat-simple \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello!"}' | python3 -m json.tool
   ```

### Expected Costs
- **Typical usage**: $10-30/month for a small team
- **Per chat**: ~$0.01-0.05
- **Per image analysis**: ~$0.05-0.10
- **Embeddings**: ~$0.0001 per document

---

## 🚀 Once OpenAI Billing is Set Up

### 1. Sync Your Figma Files

The backend is already running. To sync your brand files:

```bash
# Sync both Figma files
curl -X POST http://localhost:8000/api/sync/figma \
  -H "Content-Type: application/json" \
  -d '{"force": false}'
```

This will extract all components, styles, colors, and typography from:
- Blocks 3.0
- Brand Asset Kit 2025

### 2. Test the Chat

```bash
# Simple test
curl -X POST http://localhost:8000/api/chat-simple \
  -H "Content-Type: application/json" \
  -d '{"message": "What are our brand colors?"}' \
  | python3 -m json.tool
```

### 3. Check What Was Synced

```bash
curl http://localhost:8000/api/stats | python3 -m json.tool
```

---

## 📱 Setting Up the Frontend (Optional)

If you want a web UI instead of just API:

```bash
cd /Users/chrissycowdrey/.cursor/design-assistant/frontend

# Install dependencies
npm install

# Start the React app
npm start
```

The frontend will open at http://localhost:3000

**Note**: The frontend requires Okta to be configured. For now, you can use the API directly or we can disable Okta in the frontend too.

---

## 🎯 What You Can Do Once It's Working

### 1. **Ask Questions About Your Brand**
```bash
curl -X POST http://localhost:8000/api/chat-simple \
  -H "Content-Type: application/json" \
  -d '{"message": "What typography styles do we use?"}' 
```

### 2. **Analyze Creative for Brand Compliance**
```bash
# Upload an image
curl -X POST http://localhost:8000/api/analyze-image \
  -F "file=@/path/to/your/ad.png"
```

### 3. **Search Design System**
```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "button styles", "top_k": 5}'
```

---

## 🔧 Current Server Status

Your backend server is running at: **http://localhost:8000**

To check if it's running:
```bash
curl http://localhost:8000/api/health
```

To view server logs:
```bash
tail -f /Users/chrissycowdrey/.cursor/design-assistant/backend/server.log
```

To restart the server:
```bash
cd /Users/chrissycowdrey/.cursor/design-assistant/backend
pkill -f "python main.py"
source venv/bin/activate
nohup python main.py > server.log 2>&1 &
```

---

## 📁 Project Location

Everything is installed at:
```
/Users/chrissycowdrey/.cursor/design-assistant/
```

### Key Files
- **Configuration**: `backend/.env`
- **Server logs**: `backend/server.log`
- **Vector database**: `backend/data/chromadb/`
- **Documentation**: `README.md`, `SETUP_GUIDE.md`, `API_DOCUMENTATION.md`

---

## 🐛 Troubleshooting

### OpenAI Quota Error
- Add billing at https://platform.openai.com/account/billing

### Server Not Running
```bash
cd /Users/chrissycowdrey/.cursor/design-assistant/backend
source venv/bin/activate
python main.py
```

### Port 8000 In Use
```bash
lsof -ti:8000 | xargs kill -9
```

### Sync Fails
- Check Figma token is valid
- Verify file keys are correct
- Check server logs for errors

---

## 📞 Next Steps

1. **Fix OpenAI billing** (required)
2. **Test the sync** once OpenAI is working
3. **Try asking questions** about your brand
4. **Upload an image** to test brand compliance analysis
5. **Share with your team** once it's working well

---

## 💡 Tips

- **Cost Control**: Set a monthly limit in OpenAI dashboard
- **Regular Syncs**: Run sync weekly to keep design system up to date
- **Monitoring**: Check server logs if something doesn't work
- **Questions**: The more specific, the better the answers

---

**You're almost there!** Just fix the OpenAI billing and you'll have a fully functional design assistant! 🎨✨

