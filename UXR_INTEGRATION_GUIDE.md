# UXR Integration Guide - Complete Workflow

## 🎯 Overview

Your design assistant will search through ALL your UXR decks (root folder + all subfolders), synthesize findings, and provide insights with links back to the source slides.

---

## 📁 Folder Structure Support

**Your Google Drive structure:**
```
📁 UXR Research (root folder)
├── 📁 2025 Q1 Research
│   ├── 📄 Onboarding Study January.pptx
│   └── 📄 Feed Navigation Research.pptx
├── 📁 2025 Q2 Research
│   ├── 📄 SMB User Needs Study.pptx
│   └── 📄 Mobile App Usability.pptx
├── 📁 2024 Archive
│   ├── 📁 Q4 Studies
│   │   └── 📄 Year End Summary.pptx
│   └── 📁 Q3 Studies
└── 📁 Ad Hoc Research
    └── 📄 Quick User Feedback Sessions.pptx
```

**The assistant will:**
- ✅ Search the root folder
- ✅ Search ALL subfolders recursively
- ✅ Index every presentation found
- ✅ Extract text from all slides
- ✅ Extract speaker notes (where insights live!)

---

## 🔧 Configuration (One-Time Setup)

### Step 1: Get Service Account Credentials

Follow the detailed guide in `GOOGLE_SLIDES_SETUP.md` (15 minutes)

### Step 2: Share Your UXR Root Folder

1. Find your main UXR folder in Google Drive
2. Share it with the service account email
3. Set to **Viewer** permission
4. **Important**: Subfolders automatically inherit permissions!

### Step 3: Get Root Folder ID

1. Open your UXR root folder
2. URL looks like: `https://drive.google.com/drive/folders/1AbCdEfGhIjKlMnOpQrStUvWxYz`
3. Copy the ID: `1AbCdEfGhIjKlMnOpQrStUvWxYz`

### Step 4: Configure

```bash
# Put service account JSON here
mkdir -p /Users/chrissycowdrey/.cursor/design-assistant/credentials
mv ~/Downloads/service-account.json \
   /Users/chrissycowdrey/.cursor/design-assistant/credentials/google-service-account.json

# Update .env
cd /Users/chrissycowdrey/.cursor/design-assistant/backend
```

Add to `.env`:
```bash
GOOGLE_APPLICATION_CREDENTIALS=/Users/chrissycowdrey/.cursor/design-assistant/credentials/google-service-account.json
GOOGLE_DRIVE_FOLDER_ID=1AbCdEfGhIjKlMnOpQrStUvWxYz
```

### Step 5: Sync

Go to http://localhost:3000 → Admin tab → Click **"Sync Google Slides"**

**What happens:**
```
Searching 12 folders (root + subfolders)...
Found 47 total presentations
Syncing: Onboarding Study January...
Syncing: Feed Navigation Research...
Syncing: SMB User Needs Study...
...
✅ Synced 47 presentations with 423 slides
```

---

## 💬 How Users Will Search & Get Insights

### Example 1: General Topic Search

**User asks:**
```
"What research do we have about onboarding?"
```

**Bot searches:**
- All presentations in root + subfolders
- Finds relevant slides with "onboarding"
- Retrieves text + speaker notes

**Bot responds:**
```
Based on our UXR research, here are the key insights about onboarding:

**From "Onboarding Study January 2025" (Slide 8):**
- 65% of new users dropped off at the profile setup step
- Users wanted clearer guidance on privacy settings
- Average time to complete: 4.2 minutes (target: 2 minutes)

**From "Mobile App Usability Q2" (Slide 15):**
- Users confused by neighborhood selection interface
- Recommendation: Add map view to onboarding
- 78% preferred visual selection over search

**Key Themes:**
1. Privacy concerns (multiple studies)
2. Navigation complexity
3. Time to value too long

**Sources:**
- Onboarding Study January 2025 [Google Slides link]
- Mobile App Usability Q2 [Google Slides link]
```

### Example 2: Specific Feature Feedback

**User asks:**
```
"What did users say about the feed?"
```

**Bot searches & synthesizes:**
```
User feedback about the feed from our research:

**From "Feed Navigation Research Q1 2025" (Slide 3):**
- Users want more control over content types
- 82% said "too much noise"
- Top request: Better filtering options

**From "SMB User Needs Study" (Slide 12):**
- Business owners want separate feed for business content
- Current feed mixes personal and business posts
- Recommendation: Tabbed interface

**Pain Points Identified:**
1. Content relevance (mentioned in 3 studies)
2. Filtering capabilities
3. Algorithm transparency

**Opportunities:**
- Personalization controls
- Content categories
- Feed preferences

**Sources:**
- Feed Navigation Research Q1 2025, Slide 3 [link]
- SMB User Needs Study, Slide 12 [link]
- Quick User Feedback Sessions, Slide 7 [link]
```

### Example 3: Find Specific Research

**User asks:**
```
"Link to the SMB user research deck"
```

**Bot responds:**
```
Here's the SMB User Needs Study: [Google Slides link]

This deck contains insights about SMB users including:
- Business owner pain points
- Feature requests
- Usage patterns
- Competitive analysis

Last updated: May 2025
```

### Example 4: Cross-Study Synthesis

**User asks:**
```
"What are the top user pain points across all research?"
```

**Bot analyzes multiple decks:**
```
Top user pain points identified across our research studies:

**1. Navigation Complexity (5 studies)**
- Mentioned in: Onboarding Study, Feed Research, Mobile Usability, Q4 Summary, Ad Hoc Sessions
- Common quote: "I don't know where to find things"
- Impact: High drop-off rates

**2. Privacy Concerns (4 studies)**
- Users unclear about who sees their posts
- Privacy settings too complex
- Need: Simpler privacy controls

**3. Content Relevance (4 studies)**
- "Too much irrelevant content in feed"
- Want better personalization
- Algorithm perceived as random

**4. Mobile Performance (3 studies)**
- App perceived as slow
- Loading times frustrate users
- Need: Performance improvements

**Recommendations synthesized from research:**
- Simplify navigation structure (high priority)
- Add privacy clarity at point of posting
- Improve feed algorithm transparency
- Optimize mobile performance

**Sources:**
[Lists all 12+ studies referenced with links]
```

---

## 🎯 What Gets Indexed

**From each presentation:**
- ✅ Presentation title
- ✅ All slide text content
- ✅ **Speaker notes** (critical for UXR insights!)
- ✅ Slide numbers
- ✅ Last modified date
- ✅ Folder path/organization
- ✅ Direct link to presentation

**From each slide:**
- Text boxes
- Tables (cell content)
- Headers and bullets
- Charts (text labels)
- Speaker notes section

---

## 🔍 Search Capabilities

**The assistant can:**

### Find by Topic:
- "Research about navigation"
- "User feedback on ads"
- "SMB insights"

### Find by Type:
- "Show me all onboarding research"
- "What UXR do we have from Q1?"
- "Recent user studies?"

### Synthesize Across Studies:
- "What did we learn about [topic]?"
- "Common pain points?"
- "User needs for [feature]?"

### Get Specific Decks:
- "Link to [deck name]"
- "Find the [topic] research"
- "Where's the [study] presentation?"

---

## 📊 After Configuration

**Database will include:**
- Current: 1,955 documents
- After sync: 1,955 + [number of UXR slides]

**Example if you have 50 decks with avg 20 slides:**
- +1,000 documents from UXR
- Total: ~2,950+ documents
- All searchable by content

---

## 💡 Advanced Features

### Trend Analysis
```
"What themes appear in our 2025 research?"
→ Analyzes across all 2025 folders
→ Identifies recurring themes
→ Cites multiple studies
```

### Competitive Insights
```
"What did users say about competitors?"
→ Searches all decks for competitive mentions
→ Synthesizes competitive insights
→ Links to source slides
```

### Feature Validation
```
"Do we have research supporting [feature idea]?"
→ Searches all UXR
→ Finds relevant studies
→ Quotes supporting/contradicting evidence
```

---

## 🚀 Configuration Commands

**Once you have the credentials:**

```bash
# Test connection
cd /Users/chrissycowdrey/.cursor/design-assistant/backend
source venv/bin/activate

python3 << 'EOF'
from integrations.google_slides import google_slides_client

# Test listing presentations
presentations = google_slides_client.list_presentations_in_folder()
print(f"Found {len(presentations)} presentations")

# Show first 5
for pres in presentations[:5]:
    print(f"  - {pres['name']}")
EOF

# If that works, sync via API
curl -X POST http://localhost:8000/api/sync/slides \
  -H "Content-Type: application/json" \
  -d '{"force": false}'
```

**Or via web interface:**
1. Go to http://localhost:3000
2. Admin tab
3. Click "Sync Google Slides"

---

## 📈 Expected Sync Time

**Depends on number of presentations:**
- 10 decks: ~30 seconds
- 50 decks: ~2-3 minutes
- 100 decks: ~5 minutes

The system shows progress and handles large volumes efficiently.

---

## 🎯 Real-World Use Case

**PM asks:**
```
"What do users think about our notification system?"
```

**Bot searches:**
- Root folder: "UXR Research"
- All subfolders: Q1, Q2, Q3, Q4, Ad Hoc, etc.
- Finds 8 decks mentioning notifications
- Extracts relevant slides + speaker notes

**Bot synthesizes:**
```
Notification insights from 8 research studies:

**Pain Points:**
- Too many notifications (mentioned in 6 studies)
- Not relevant enough (4 studies)
- Hard to control settings (3 studies)

**From "Mobile Push Notification Study Q2" (Slide 9):**
"Users receive average 12 notifications/day. 
Only 3 are considered valuable. Users want granular control."
[Link to slide]

**From "Retention Research Q3" (Slide 15):**
"Users who customize notifications have 40% higher retention.
Recommendation: Make settings more discoverable."
[Link to slide]

**Recommendations across studies:**
1. Reduce default notification frequency (high priority)
2. Add notification categories
3. Improve settings discoverability
4. Add smart bundling

**Referenced Studies:**
- Mobile Push Notification Study Q2 [link]
- Retention Research Q3 [link]
- User Preferences Survey Q1 [link]
[... 5 more]
```

---

## ✨ Benefits

### For Designers:
- Instant access to past research
- No digging through Drive
- Synthesized insights, not raw dumps

### For PMs:
- Validate feature ideas with research
- Find supporting data quickly
- Cross-study insights

### For UX Researchers:
- Institutional knowledge preserved
- Research findings surfaced when relevant
- Easy to reference past studies

### For Leadership:
- Data-driven decision making
- See research trends
- Validate investments

---

## 🔒 Privacy & Security

- Service account has **read-only** access
- Only accesses shared folder
- No write permissions
- Credentials stored securely
- No data leaves your systems

---

## 🚀 Ready to Configure?

**Follow these steps:**

1. **Read**: GOOGLE_SLIDES_SETUP.md (detailed instructions)
2. **Create**: Google Cloud service account (15 min)
3. **Share**: Your UXR folder with the service account
4. **Configure**: Add credentials and folder ID to .env
5. **Sync**: Click "Sync Google Slides" in Admin panel
6. **Ask**: "What research do we have about [topic]?"

---

## 💬 Example Queries After Setup

- "What did we learn about SMB users?"
- "User feedback on advertising experience?"
- "Research insights about feed algorithm?"
- "What pain points did users mention in 2025?"
- "Link to the onboarding research deck"
- "Synthesize findings about mobile app"

---

**The system is ready - just needs your Google credentials!** 📊✨

Let me know when you're ready to configure it, or if you'd like me to walk you through the Google Cloud setup step-by-step!

