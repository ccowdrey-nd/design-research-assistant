# Design Assistant - Complete Setup Guide

This guide walks you through setting up the Design Assistant chatbot from scratch.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Getting API Keys](#getting-api-keys)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Running the Application](#running-the-application)
6. [First-time Setup](#first-time-setup)

---

## Prerequisites

Before you begin, ensure you have:

- **Python 3.9+** installed ([Download](https://www.python.org/downloads/))
- **Node.js 16+** installed ([Download](https://nodejs.org/))
- **Git** installed
- Admin access to your company's Okta account
- Access to your company's Figma team
- Access to Google Drive folder with design presentations

---

## Getting API Keys

### 1. OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com)
2. Sign in or create an account
3. Navigate to **API Keys** section
4. Click **Create new secret key**
5. Copy the key (starts with `sk-...`)
6. **Important**: Save this key securely - you won't be able to see it again

**Cost**: GPT-4 and embeddings are pay-per-use. Estimate ~$0.50-2.00 per day for a small team.

### 2. Figma Access Token

1. Sign in to [Figma](https://www.figma.com)
2. Go to **Settings** → **Account**
3. Scroll to **Personal Access Tokens**
4. Click **Generate new token**
5. Give it a descriptive name (e.g., "Design Assistant Bot")
6. Copy the token (starts with `figd_...`)

**Permissions**: The token will have access to all files you can access.

### 3. Figma Team ID or File Keys

**Option A - Using Team ID (recommended):**

1. Go to your Figma team page
2. The URL looks like: `https://www.figma.com/files/team/1234567890/TeamName`
3. Your Team ID is: `1234567890`

**Option B - Using specific file keys:**

1. Open each Figma file you want to include
2. The URL looks like: `https://www.figma.com/file/AbCdEfGhIj/FileName`
3. The file key is: `AbCdEfGhIj`
4. Create a comma-separated list: `file1,file2,file3`

### 4. Google Slides API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing one
3. Enable **Google Slides API**:
   - Navigate to **APIs & Services** → **Library**
   - Search for "Google Slides API"
   - Click **Enable**
4. Enable **Google Drive API** (same process)
5. Create **Service Account**:
   - Go to **APIs & Services** → **Credentials**
   - Click **Create Credentials** → **Service Account**
   - Name: "design-assistant-bot"
   - Click **Create and Continue**
   - Skip optional steps
6. Download JSON key:
   - Click on the created service account
   - Go to **Keys** tab
   - Click **Add Key** → **Create new key**
   - Choose **JSON**
   - Save the downloaded file securely

### 5. Share Google Drive Folder with Service Account

1. Open the downloaded service account JSON file
2. Copy the `client_email` value (looks like: `design-assistant-bot@project-id.iam.gserviceaccount.com`)
3. Open your Google Drive folder containing design presentations
4. Click **Share**
5. Paste the service account email
6. Give **Viewer** access
7. Copy the folder ID from the URL:
   - URL: `https://drive.google.com/drive/folders/1AbCdEfGhIjKlMnOpQrStUvWxYz`
   - Folder ID: `1AbCdEfGhIjKlMnOpQrStUvWxYz`

### 6. Okta Configuration

**Step 1: Create Application**

1. Sign in to **Okta Admin Console**
2. Go to **Applications** → **Applications**
3. Click **Create App Integration**
4. Select:
   - **Sign-in method**: OIDC - OpenID Connect
   - **Application type**: Single-Page Application
5. Click **Next**

**Step 2: Configure Application**

- **App integration name**: Design Assistant
- **Grant type**: Authorization Code (should be checked)
- **Sign-in redirect URIs**: 
  - `http://localhost:3000/login/callback` (for development)
  - `https://your-domain.com/login/callback` (for production)
- **Sign-out redirect URIs**:
  - `http://localhost:3000` (for development)
  - `https://your-domain.com` (for production)
- **Controlled access**: Choose who can use this app (e.g., specific groups)

**Step 3: Get Configuration Details**

After creating the app:
- Copy **Client ID**
- Note your **Okta domain** (e.g., `your-company.okta.com`)
- The **Issuer** is usually: `https://your-company.okta.com/oauth2/default`

---

## Installation

### Automated Setup (Recommended)

```bash
# Clone or navigate to the project
cd design-assistant

# Run setup script
./setup.sh
```

The script will:
- Create Python virtual environment
- Install backend dependencies
- Install frontend dependencies
- Create .env files from templates

### Manual Setup

If the automated script doesn't work:

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp env.example .env
```

**Frontend:**
```bash
cd frontend
npm install
cp env.example .env
```

---

## Configuration

### Backend Configuration

Edit `backend/.env`:

```bash
# OpenAI
OPENAI_API_KEY=sk-your-actual-openai-key

# Figma
FIGMA_ACCESS_TOKEN=figd_your-actual-figma-token
FIGMA_TEAM_ID=1234567890
# OR use specific files:
# FIGMA_FILE_KEYS=file1,file2,file3

# Google Slides
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/service-account.json
GOOGLE_DRIVE_FOLDER_ID=your-actual-folder-id

# Okta
OKTA_DOMAIN=your-company.okta.com
OKTA_CLIENT_ID=your-actual-client-id
OKTA_CLIENT_SECRET=your-actual-client-secret
OKTA_ISSUER=https://your-company.okta.com/oauth2/default
OKTA_REDIRECT_URI=http://localhost:3000/callback

# Application Settings
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
DEBUG=False
```

**Important**: 
- Use absolute paths for `GOOGLE_APPLICATION_CREDENTIALS`
- Don't commit this file to git (it's in .gitignore)

### Frontend Configuration

Edit `frontend/.env`:

```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_OKTA_ISSUER=https://your-company.okta.com/oauth2/default
REACT_APP_OKTA_CLIENT_ID=your-actual-client-id
```

---

## Running the Application

### Start Backend

```bash
# Navigate to backend
cd backend

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the server
python main.py
```

The backend will start at `http://localhost:8000`

### Start Frontend (in a new terminal)

```bash
# Navigate to frontend
cd frontend

# Start development server
npm start
```

The frontend will open automatically at `http://localhost:3000`

---

## First-time Setup

### 1. Log In

1. Open `http://localhost:3000`
2. Click **Sign in with Okta**
3. Enter your Okta credentials
4. You'll be redirected back to the app

### 2. Sync Data Sources

1. Click the **Admin** tab
2. Click **Sync Figma Files**
   - Wait for the sync to complete
   - You should see a list of synced files
3. Click **Sync Google Slides**
   - Wait for the sync to complete
   - You should see a list of synced presentations

This populates the vector database with your design system content.

### 3. Test the Chat

1. Click the **Chat** tab
2. Try asking:
   - "What are our brand colors?"
   - "Show me button components"
   - "What typography styles do we have?"

### 4. Test Image Analysis

1. Click the **Image Analysis** tab
2. Upload an image (email, ad, etc.)
3. Click **Analyze Brand Compliance**
4. Review the feedback

---

## Troubleshooting

### "Module not found" errors (Backend)

```bash
# Make sure virtual environment is activated
source backend/venv/bin/activate

# Reinstall dependencies
pip install -r backend/requirements.txt
```

### "Cannot find module" errors (Frontend)

```bash
# Delete node_modules and reinstall
cd frontend
rm -rf node_modules
npm install
```

### Okta redirect loop

- Check that redirect URIs in Okta app match exactly
- Ensure you're using the correct Client ID
- Clear browser cache and cookies

### Figma sync returns no data

- Verify your access token is valid
- Check that you have access to the team/files
- Make sure Team ID or File Keys are correct

### Google Slides sync fails

- Check that the service account email is shared on the folder
- Verify the JSON credentials file path is correct and absolute
- Ensure both Slides API and Drive API are enabled

### OpenAI API errors

- Check your API key is valid
- Ensure you have credits/billing set up
- Verify you have access to GPT-4 (may require payment)

---

## Next Steps

- **Customize system prompts** in `backend/main.py` for your company's tone
- **Add more data sources** by creating new integrations
- **Schedule automatic syncs** using cron jobs or similar
- **Deploy to production** following the README deployment guide
- **Integrate with Slack/Teams** for easier access

---

## Support

For issues or questions:
1. Check the main README.md
2. Review error messages in browser console and terminal
3. Contact your internal development team

## Security Notes

- Never commit `.env` files or API keys to git
- Keep the Google service account JSON secure
- Regularly rotate API tokens
- Use Okta groups to control access
- Enable HTTPS in production (required for Okta)

