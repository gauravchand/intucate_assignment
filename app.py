import os, asyncio
from flask import Flask, request, jsonify
from pymongo import MongoClient
from openai import OpenAI, AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Setup DB & Groq Clients
key, url = os.getenv("GROQ_API_KEY"), "https://api.groq.com/openai/v1"
db = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))["chatgpt_flask_project"]
sync_ai, async_ai = OpenAI(api_key=key, base_url=url), AsyncOpenAI(api_key=key, base_url=url)

# Seed DB if template doesn't exist
if not db.prompts.find_one({"_id": "Education_Prompt"}):
    db.prompts.insert_one({"_id": "Education_Prompt", "template": "You are an expert in education domain. Answer the following: {{userInput}}"})

@app.route('/ask', methods=['POST'])
def ask_single():
    ui = request.json.get("userInput")
    if not ui: return jsonify({"error": "Missing 'userInput'"}), 400
    
    prompt = db.prompts.find_one({"_id": "Education_Prompt"})["template"].replace("{{userInput}}", ui)
    res = sync_ai.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}]).choices[0].message.content
    
    db.history.insert_one({"request": ui, "response": res})
    return jsonify({"response": res})

async def fetch_ai(ui, tmpl):
    """Helper for async route. Returns a formatted dictionary ready for MongoDB."""
    res = await async_ai.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": tmpl.replace("{{userInput}}", ui)}])
    return {"request": ui, "response": res.choices[0].message.content}

@app.route('/ask-batch', methods=['POST'])
async def ask_batch():
    uis = request.json.get("userInputs", [])
    if not uis or not isinstance(uis, list): return jsonify({"error": "Need list in 'userInputs'"}), 400
    
    tmpl = db.prompts.find_one({"_id": "Education_Prompt"})["template"]
    
    # Fire all API calls at once and wait for results
    results = await asyncio.gather(*(fetch_ai(ui, tmpl) for ui in uis))
    
    if results: db.history.insert_many(results) # Insert all at once
    return jsonify({"responses": [r["response"] for r in results]})

if __name__ == '__main__':
    app.run(debug=True, port=5000)