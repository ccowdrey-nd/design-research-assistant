# Google Slides Integration Setup

## 🎯 Overview

Enable your design assistant to read UXR decks, insights, and documentation from Google Slides.

---

## 📝 Step 1: Create Google Cloud Service Account

### 1.1 Go to Google Cloud Console
Visit: https://console.cloud.google.com

### 1.2 Create or Select Project
- If you have an existing project, select it
- Or click **"New Project"**
  - Name: "Nextdoor Design Assistant"
  - Click **Create**

### 1.3 Enable APIs
1. In the search bar, type **"Google Slides API"**
2. Click **Enable**
3. Search for **"Google Drive API"**
4. Click **Enable**

### 1.4 Create Service Account
1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **Service Account**
3. Fill in:
   - Service account name: `design-assistant-bot`
   - Service account ID: `design-assistant-bot` (auto-filled)
   - Description: "Reads UXR decks and design documentation"
4. Click **Create and Continue**
5. Skip "Grant access" (click Continue)
6. Skip "Grant users access" (click Done)

### 1.5 Download JSON Key
1. Click on your new service account email
2. Go to the **Keys** tab
3. Click **Add Key** → **Create new key**
4. Choose **JSON**
5. Click **Create**
6. **Save the downloaded file** - you'll need it!

---

## 📁 Step 2: Share Google Drive Folder

### 2.1 Open the Downloaded JSON File
- Find the file you just downloaded (something like `nextdoor-design-assistant-xxxxx.json`)
- Open it in a text editor
- Find the `client_email` field
- Copy the email (looks like: `design-assistant-bot@project-id.iam.gserviceaccount.com`)

### 2.2 Share Your UXR Folder
1. Open Google Drive
2. Navigate to the folder containing your UXR decks
3. Right-click → **Share**
4. Paste the service account email
5. Set permission to **Viewer**
6. Uncheck "Notify people"
7. Click **Share**

### 2.3 Get Folder ID
1. Open the shared folder in Google Drive
2. Look at the URL: `https://drive.google.com/drive/folders/1AbCdEfGhIjKlMnOpQrStUvWxYz`
3. Copy the folder ID: `1AbCdEfGhIjKlMnOpQrStUvWxYz`

---

## ⚙️ Step 3: Configure Design Assistant

### 3.1 Move Service Account JSON
```bash
# Create credentials directory
mkdir -p /Users/chrissycowdrey/.cursor/design-assistant/credentials

# Move the downloaded JSON file there
mv ~/Downloads/nextdoor-design-assistant-*.json \
   /Users/chrissycowdrey/.cursor/design-assistant/credentials/google-service-account.json
```

### 3.2 Update Backend .env
Add these lines to `/Users/chrissycowdrey/.cursor/design-assistant/backend/.env`:

```bash
# Google Slides Configuration
GOOGLE_APPLICATION_CREDENTIALS=/Users/chrissycowdrey/.cursor/design-assistant/credentials/google-service-account.json
GOOGLE_DRIVE_FOLDER_ID=YOUR_FOLDER_ID_HERE
```

Replace `YOUR_FOLDER_ID_HERE` with the folder ID from step 2.3

---

## 🔄 Step 4: Sync Google Slides

### Via API:
```bash
curl -X POST http://localhost:8000/api/sync/slides \
  -H "Content-Type: application/json" \
  -d '{"force": false}'
```

### Or Via Web Interface:
1. Go to http://localhost:3000
2. Click **Admin** tab
3. Click **"Sync Google Slides"**
4. Wait for sync to complete

---

## 🎯 What Gets Indexed

**From each presentation:**
- ✅ Slide text content
- ✅ Speaker notes (often contains research insights!)
- ✅ Slide numbers
- ✅ Presentation metadata
- ✅ Last modified dates
- ✅ Links back to original slides

**Perfect for UXR decks:**
- Research findings
- User quotes
- Insights and recommendations
- Design implications
- Data and statistics

---

## 💬 What You Can Ask After Setup

### UXR Insights:
- "What did we learn from recent user research?"
- "Show me insights about [feature]"
- "What do users say about [topic]?"
- "Recent UXR findings?"

### Find Presentations:
- "Link to the [research name] deck"
- "What UXR presentations do we have?"
- "Find slides about [topic]"

### Specific Findings:
- "User feedback on navigation?"
- "Research insights about ads?"
- "What pain points did we discover?"

---

## 🧪 Test After Setup

```bash
# Test the Google Slides client
cd /Users/chrissycowdrey/.cursor/design-assistant/backend
source venv/bin/activate

python3 << 'EOF'
from integrations.google_slides import google_slides_client

# List presentations
presentations = google_slides_client.list_presentations_in_folder()
print(f"Found {len(presentations)} presentations")

for pres in presentations[:5]:
    print(f"  - {pres['name']}")
EOF
```

---

## 📊 Expected Results

After sync, your database will include:
- All text from UXR presentations
- Speaker notes with insights
- Searchable research findings
- Linked back to original slides

**Example query after sync:**
```
User: "What did we learn about user onboarding?"

Bot: "Based on the UXR deck 'Onboarding Research Q3 2025':
     
     - 65% of users struggled with [specific step]
     - Users wanted [specific feature]
     - Key insight: [finding from speaker notes]
     
     Source: Onboarding Research Q3 2025, Slide 12 [link]"
```

---

## 🔒 Security Notes

- Service account has read-only access
- No write permissions needed
- Credentials stored locally (in .gitignore)
- Only accesses shared folder

---

## 💡 Tips

**Folder organization:**
- Put all UXR decks in one folder
- Subfolders are included
- Tag presentations consistently
- Use descriptive names

**Speaker notes:**
- Add detailed insights in speaker notes
- These get indexed and are searchable
- Great for context that's not on slides

---

## 🚀 Next Steps

1. **Complete Step 1-3** above (15 minutes total)
2. **Sync slides** via Admin panel
3. **Ask UXR questions** in chat
4. **Get instant insights!**

---

Let me know if you want me to help with any of these steps!

