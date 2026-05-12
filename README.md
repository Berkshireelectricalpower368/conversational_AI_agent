# 🗂️ Google Drive File Discovery Assistant

An AI-powered conversational assistant that helps you search, filter, and discover files inside Google Drive using natural language queries.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat-square&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-0.3+-1C3C3C?style=flat-square&logo=langchain&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-2.0_Flash-4285F4?style=flat-square&logo=google&logoColor=white)

---

## ✨ Features

- **Natural Language Search** — Ask questions like "Find finance PDFs from last week" and get results instantly
- **AI-Powered Query Generation** — Gemini LLM converts your words into precise Google Drive API queries
- **Conversational Memory** — Follow up on previous searches with context ("show only the Excel files")
- **Rich File Cards** — See file names, types, dates, sizes, and clickable Drive links
- **Modern Chat UI** — Dark theme with glassmorphism, animations, and responsive design
- **Search History** — Track and re-run previous searches from the sidebar
- **Smart Filtering** — Supports MIME types, date ranges, file names, and content search

## 🎯 Example Queries

| Query | What It Does |
|---|---|
| "Find finance PDFs from last week" | Searches PDFs with "finance" in the name, modified last week |
| "Show all images related to logo" | Finds JPEG/PNG/GIF/SVG files with "logo" in the name |
| "Find documents containing invoice" | Full-text content search for "invoice" across all documents |
| "Show spreadsheets uploaded this month" | Google Sheets + Excel files modified this month |
| "Find files named project report" | Name-based search for "project report" |

---

## 🏗️ Architecture

```
┌─────────────────┐       ┌──────────────────────────┐       ┌──────────────┐
│   Streamlit UI  │──────▶│     FastAPI Backend      │──────▶│  Google Drive │
│  (Frontend)     │◀──────│  ┌──────────────────┐    │◀──────│    API v3     │
│                 │       │  │  LangChain Agent  │    │       │              │
│  • Chat bubbles │       │  │  ┌──────────────┐ │   │       │  • files.list│
│  • File cards   │       │  │  │ DriveSearch  │ │   │       │  • q param   │
│  • Search hist. │       │  │  │    Tool       │ │   │       │              │
│  • Loading UI   │       │  │  └──────────────┘ │   │       └──────────────┘
└─────────────────┘       │  └──────────────────┘    │
                          │         ▲                 │       ┌──────────────┐
                          │         │                 │──────▶│   Gemini AI  │
                          │    Conversation           │◀──────│  (LLM)       │
                          │      Memory               │       └──────────────┘
                          └──────────────────────────┘
```

**Tech Stack:**
- **Frontend:** Streamlit with custom CSS
- **Backend:** FastAPI with async endpoints
- **AI Framework:** LangChain with tool calling
- **LLM:** Gemini 2.0 Flash (via `langchain-google-genai`)
- **Drive API:** Google Drive API v3 with Service Account auth

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Google Cloud Project** with Drive API enabled
- **Service Account** with Drive read access
- **Gemini API Key** from [Google AI Studio](https://aistudio.google.com/apikey)

### 1. Clone & Install

```bash
git clone https://github.com/your-username/drive-discovery-assistant.git
cd drive-discovery-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy the example env file
cp .env.example .env
```

Edit `.env` with your credentials:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
GOOGLE_SERVICE_ACCOUNT_FILE=path/to/service-account.json
GOOGLE_DRIVE_FOLDER_ID=your_folder_id_here  # Optional
```

### 3. Google Cloud Setup

<details>
<summary>📋 Step-by-step Google Cloud setup</summary>

1. **Go to [Google Cloud Console](https://console.cloud.google.com/)**

2. **Create a new project** (or select an existing one)

3. **Enable Google Drive API:**
   - Go to "APIs & Services" → "Enable APIs and Services"
   - Search for "Google Drive API"
   - Click "Enable"

4. **Create a Service Account:**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "Service Account"
   - Give it a name (e.g., "drive-discovery")
   - Click "Done"

5. **Create a JSON key:**
   - Click on the service account you just created
   - Go to "Keys" tab
   - Click "Add Key" → "Create new key" → "JSON"
   - Download the JSON file and save it in your project directory

6. **Share your Drive folder:**
   - Open Google Drive
   - Right-click the folder you want to search
   - Click "Share"
   - Add the service account email (e.g., `drive-discovery@your-project.iam.gserviceaccount.com`)
   - Give it "Viewer" access

7. **Get the folder ID** (optional):
   - Open the folder in Google Drive
   - Copy the ID from the URL: `https://drive.google.com/drive/folders/FOLDER_ID_HERE`
   - Add it to `.env` as `GOOGLE_DRIVE_FOLDER_ID`

</details>

### 4. Run Locally

Open **two terminals** from the project root:

**Terminal 1 — Backend:**
```bash
# Linux/Mac (with venv activated)
source venv/bin/activate
uvicorn backend.main:app --reload

# Windows (without activating venv)
.\venv\Scripts\uvicorn.exe backend.main:app --reload

# Windows (with venv activated)
venv\Scripts\activate
uvicorn backend.main:app --reload
```

**Terminal 2 — Frontend:**
```bash
# Linux/Mac (with venv activated)
source venv/bin/activate
streamlit run frontend/app.py

# Windows (without activating venv)
.\venv\Scripts\streamlit.exe run frontend/app.py

# Windows (with venv activated)
venv\Scripts\activate
streamlit run frontend/app.py
```

Open your browser at **http://localhost:8501** and start searching! 🎉

---

## 📁 Project Structure

```
conversational_AI_agent/
├── backend/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app with endpoints
│   ├── config.py                  # Environment variable handling
│   ├── models/
│   │   └── schemas.py             # Pydantic request/response models
│   ├── services/
│   │   ├── drive_service.py       # Google Drive API wrapper
│   │   └── agent_service.py       # LangChain agent orchestration
│   ├── tools/
│   │   └── drive_search_tool.py   # Custom LangChain DriveSearchTool
│   ├── prompts/
│   │   └── system_prompts.py      # AI system prompts
│   └── utils/
│       ├── logger.py              # Structured logging
│       ├── mime_types.py          # MIME type mappings
│       └── date_utils.py         # Date utility functions
├── frontend/
│   ├── app.py                     # Streamlit main app
│   ├── components/
│   │   ├── chat_ui.py             # Chat interface components
│   │   ├── file_card.py           # File result card component
│   │   └── sidebar.py            # Sidebar with search history
│   ├── styles/
│   │   └── custom.css             # Custom CSS (dark theme)
│   └── utils/
│       └── api_client.py          # FastAPI HTTP client
├── .env.example
├── .gitignore
├── requirements.txt
├── Procfile
├── Dockerfile.backend
├── Dockerfile.frontend
├── docker-compose.yml
├── render.yaml
├── railway.toml
└── README.md
```

---

## 🔌 API Documentation

Once the backend is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/chat` | Process a natural language query |
| `GET` | `/api/history/{session_id}` | Get search history |
| `DELETE` | `/api/session/{session_id}` | Clear session memory |

### Chat Request Example

```json
POST /api/chat
{
    "query": "Find finance PDFs from last week",
    "session_id": "abc-123"
}
```

### Chat Response Example

```json
{
    "message": "I found 3 finance PDFs from last week!",
    "files": [
        {
            "id": "1BxiMVs...",
            "name": "Q4 Finance Report.pdf",
            "mime_type": "application/pdf",
            "modified_time": "2026-05-10T14:30:00.000Z",
            "web_view_link": "https://drive.google.com/file/d/1BxiMVs.../view",
            "size": "2048576"
        }
    ],
    "query_used": "name contains 'finance' and mimeType='application/pdf' and modifiedTime > '2026-05-04T00:00:00Z' and trashed = false",
    "session_id": "abc-123"
}
```

---

## 🚢 Deployment

### Option 1: Railway

1. Push your code to GitHub
2. Go to [Railway](https://railway.app) and create a new project
3. Connect your GitHub repo
4. **Deploy Backend:** Create a service with start command:
   ```
   uvicorn backend.main:app --host 0.0.0.0 --port $PORT
   ```
5. **Deploy Frontend:** Create another service with start command:
   ```
   streamlit run frontend/app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
   ```
6. Set environment variables in Railway's dashboard
7. Set `BACKEND_URL` in the frontend service to your backend service URL

### Option 2: Render

1. Push your code to GitHub
2. Go to [Render](https://render.com) and use the `render.yaml` blueprint:
   ```bash
   render blueprint deploy
   ```
3. Or manually create two web services (backend + frontend)
4. Set environment variables in the Render dashboard

### Option 3: Docker Compose

```bash
# Build and run both services
docker compose up --build

# Backend: http://localhost:8000
# Frontend: http://localhost:8501
```

### Option 4: Streamlit Cloud (Frontend Only)

1. Deploy the backend on Railway/Render
2. Deploy the frontend on [Streamlit Cloud](https://streamlit.io/cloud)
3. Set `BACKEND_URL` to your deployed backend URL in Streamlit Cloud secrets

---

## 🛠️ Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_API_KEY` | ✅ | — | Gemini API key from Google AI Studio |
| `GOOGLE_SERVICE_ACCOUNT_FILE` | ✅ | — | Path to service account JSON (or JSON string) |
| `GOOGLE_DRIVE_FOLDER_ID` | ❌ | — | Restrict search to a specific folder |
| `GEMINI_MODEL` | ❌ | `gemini-2.0-flash` | Gemini model name |
| `BACKEND_URL` | ❌ | `http://localhost:8000` | Backend API URL (for frontend) |
| `BACKEND_HOST` | ❌ | `0.0.0.0` | Backend bind host |
| `BACKEND_PORT` | ❌ | `8000` | Backend bind port |
| `LOG_LEVEL` | ❌ | `INFO` | Logging level |

---

## 🧰 How It Works

1. **User sends a query** via the Streamlit chat interface
2. **Frontend sends HTTP POST** to FastAPI backend `/api/chat`
3. **FastAPI passes the query** to the LangChain agent
4. **Gemini LLM interprets** the natural language query
5. **LLM generates a Drive API `q` parameter** and calls `DriveSearchTool`
6. **DriveSearchTool executes** `files.list` against Google Drive API v3
7. **Results flow back** through the agent to FastAPI to Streamlit
8. **Streamlit renders** file cards with metadata and Drive links

The LangChain agent maintains **conversational memory per session**, so follow-up queries like "show only the PDFs" work naturally.

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Cannot connect to backend" | Make sure the backend is running (`uvicorn backend.main:app --reload`) |
| "Agent not initialized" | Check your `.env` file — `GOOGLE_API_KEY` and `GOOGLE_SERVICE_ACCOUNT_FILE` are required |
| "Invalid service account" | Verify your service account JSON file path is correct |
| "No files found" | Make sure you've shared the Drive folder with your service account email |
| "Rate limit errors" | The backend has built-in retry logic, but consider reducing query frequency |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

Built with ❤️ using FastAPI, LangChain, Gemini, and Streamlit.
