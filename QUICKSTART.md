# Quick Start Guide

Get the Design Assistant running in 5 minutes!

## Prerequisites Checklist

- [ ] Python 3.9+ installed
- [ ] Node.js 16+ installed
- [ ] OpenAI API key
- [ ] Figma access token
- [ ] Google service account JSON (optional, for Slides)
- [ ] Okta app configured

## Fast Setup

### 1. Run Setup Script

```bash
./setup.sh
```

### 2. Configure API Keys

**Edit `backend/.env`:**

```bash
OPENAI_API_KEY=sk-your-key
FIGMA_ACCESS_TOKEN=figd_your-token
FIGMA_TEAM_ID=your-team-id
OKTA_DOMAIN=your-company.okta.com
OKTA_CLIENT_ID=your-client-id
OKTA_CLIENT_SECRET=your-secret
OKTA_ISSUER=https://your-company.okta.com/oauth2/default
```

**Edit `frontend/.env`:**

```bash
REACT_APP_OKTA_ISSUER=https://your-company.okta.com/oauth2/default
REACT_APP_OKTA_CLIENT_ID=your-client-id
```

### 3. Start Backend

```bash
cd backend
source venv/bin/activate
python main.py
```

Keep this terminal open.

### 4. Start Frontend (New Terminal)

```bash
cd frontend
npm start
```

Browser will open to `http://localhost:3000`

### 5. Initial Sync

1. Log in with Okta
2. Go to **Admin** tab
3. Click **Sync Figma Files**
4. Click **Sync Google Slides** (if configured)

### 6. Start Chatting!

Try asking:
- "What are our brand colors?"
- "Show me button components"

## Need More Help?

- **Detailed setup**: See [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **API configuration**: See [README.md](README.md)
- **Troubleshooting**: Check terminal logs for errors

## Common First-Time Issues

**"Invalid authentication credentials"**
- Check Okta configuration matches in both .env files
- Verify redirect URI in Okta app

**"No documents found"**
- Run the sync operations in Admin panel first
- Check Figma/Google API credentials

**"Module not found"**
- Run `pip install -r requirements.txt` in backend
- Run `npm install` in frontend

