# Intucate Assignment — Flask + MongoDB + Groq (OpenAI-compatible) Chat API

A small Flask service that exposes:
- `POST /ask` — ask a single question (stored in MongoDB)
- `POST /ask-batch` — ask multiple questions concurrently using async calls (also stored in MongoDB)

It uses Groq’s OpenAI-compatible API endpoint and stores:
- a prompt template in `prompts` (seeded on first run)
- request/response history in `history`

## Tech Stack
- Python (Flask)
- MongoDB (`pymongo`)
- Groq API via OpenAI SDK (`openai` + `base_url=https://api.groq.com/openai/v1`)
- `python-dotenv` for environment variables
- Async batch requests with `asyncio`

## Project Structure
- `app.py` — Flask API (single + batch endpoints, MongoDB integration, prompt seeding)
- `.env` — environment variables (API key + Mongo URI)
- `output.png` — sample output/screenshot
- `LICENSE` — MIT

## Prerequisites
- Python 3.9+ (recommended)
- A running MongoDB instance (local or hosted)
- A Groq API key

## Setup

### 1) Clone
```bash
git clone https://github.com/gauravchand/intucate_assignment.git
cd intucate_assignment
```

### 2) Create and activate a virtual environment
```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

### 3) Install dependencies
This repo does not include a `requirements.txt`, so install the needed packages directly:
```bash
pip install flask pymongo openai python-dotenv
```

### 4) Configure environment variables
Update `.env` (do not commit real secrets):
```env
GROQ_API_KEY=your_api_key_here
MONGO_URI=mongodb://localhost:27017/
```

Notes:
- `MONGO_URI` defaults to `mongodb://localhost:27017/` if not provided.
- The app uses database name: `chatgpt_flask_project`.

## Run the server
```bash
python app.py
```

Server starts at:
- `http://localhost:5000`

## API Usage

### 1) Ask a single question
**Endpoint:** `POST /ask`

**Request body:**
```json
{
  "userInput": "Explain Bloom's taxonomy in simple terms."
}
```

**cURL:**
```bash
curl -X POST http://localhost:5000/ask \
  -H "Content-Type: application/json" \
  -d '{"userInput":"Explain Bloom'\''s taxonomy in simple terms."}'
```

**Response:**
```json
{
  "response": "..."
}
```

### 2) Ask a batch of questions (async)
**Endpoint:** `POST /ask-batch`

**Request body:**
```json
{
  "userInputs": [
    "What is formative assessment?",
    "Give examples of active learning strategies."
  ]
}
```

**cURL:**
```bash
curl -X POST http://localhost:5000/ask-batch \
  -H "Content-Type: application/json" \
  -d '{"userInputs":["What is formative assessment?","Give examples of active learning strategies."]}'
```

**Response:**
```json
{
  "responses": ["...", "..."]
}
```

## Data Stored in MongoDB

### `prompts` collection
On startup, the app seeds a prompt (only if it doesn’t exist):
- `_id`: `Education_Prompt`
- `template`: `You are an expert in education domain. Answer the following: {{userInput}}`

### `history` collection
Each request/response pair is stored as:
```json
{
  "request": "...",
  "response": "..."
}
```

## Model Used
The app calls:
- `model="llama-3.1-8b-instant"`

(Invoked via Groq’s OpenAI-compatible `/chat/completions` endpoint.)

## Troubleshooting
- **`Missing 'userInput'`**: Ensure `/ask` payload includes `"userInput"`.
- **`Need list in 'userInputs'`**: Ensure `/ask-batch` payload includes `"userInputs"` as a JSON array.
- **Mongo connection issues**: Verify `MONGO_URI` and that MongoDB is running/reachable.
- **Auth errors from Groq**: Verify `GROQ_API_KEY`.

## License
MIT (see `LICENSE`).
