

---

```markdown
# 🧑‍🔬 AI Research Assistant (Strands Agents + Bedrock)

Build a **multi-agent research assistant** that can:
- 🔍 Search academic papers from [arXiv](https://arxiv.org)
- 📝 Summarize each paper into concise bullet points
- 🌐 Provide a simple **web interface** to ask research questions
- ⚙️ Run on **AWS Bedrock** (Anthropic Claude 3.5 Sonnet)

This project demonstrates how to use **[Strands Agents](https://github.com/aws-samples/strands-agents)** to orchestrate multiple AI agents and tools in a clean, production-minded way.

---

## ✨ Features
- **Bedrock model**: Uses `anthropic.claude-3-5-sonnet-20241022-v2:0`
- **Tooling**:
  - `arxiv_search` → fetch papers from arXiv API (returns JSON object, never list ✅)
  - `summarize_papers` → uses LLM to generate up to 5 short factual bullets per paper
- **Orchestrator Agent**: Routes requests through tools and produces final readable output
- **Web UI**:
  - Form to enter a research query
  - Options for max papers + bullets per paper
  - Results rendered directly in the browser

---

## 🗂 Project Structure
```

strands/
├── arxiv\_search.py          # Tool: fetch papers (object return ✅)
├── summarizer.py            # Tool: summarize papers into bullet points
├── config.py                # Bedrock model config
├── search\_and\_summarize.py  # Orchestrator agent (CLI entrypoint)
├── web.py                   # FastAPI server (web frontend + API)
├── templates/
│   └── index.html           # Web UI (form + JS fetch)
├── static/
│   └── style.css            # Optional CSS styling
└── README.md                # This file

````

---

## ⚙️ Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/yourname/ai-research-assistant.git
   cd ai-research-assistant
````

2. Create a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -U pip
   pip install strands-agents fastapi uvicorn jinja2 requests python-multipart
   ```

4. Configure AWS credentials with Bedrock model access:

   ```bash
   aws configure
   ```

   Make sure your account has access to **`anthropic.claude-3-5-sonnet-20241022-v2:0`** in your region (default `ap-southeast-2` in `config.py`).

---

## ▶️ Usage

### CLI (terminal)

```bash
python search_and_summarize.py
```

Output: Summaries of 3 papers on the default query (`federated learning privacy`).

### Web App

Run the FastAPI app:

```bash
uvicorn web:app --reload --port 8000
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

* Enter a research topic (e.g., *"diffusion models safety"*).
* Adjust number of papers / bullets.
* Get a clean summary of the latest arXiv results.

---

## 🛠 How It Works

1. **User query** → Orchestrator Agent
2. Orchestrator calls **`arxiv_search`**:

   * Fetches papers from arXiv (JSON object with `papers` + `count`).
   * ✅ Always returns a dict (not a raw list) to satisfy Bedrock `ConverseStream`.
3. Orchestrator feeds the result object to **`summarize_papers`**:

   * Summarizer agent generates up to 5 concise bullets per paper.
   * Returns a dict like:

     ```json
     {
       "count": 3,
       "items": [
         {"title": "...", "bullets": ["..."], "link": "..."}
       ]
     }
     ```
4. Orchestrator writes the final **human-readable summary** for CLI/Web output.

---

## 🌐 Example Output

**Query:** “federated learning privacy”
**Answer:**

* **Paper 1: Title**

  * Bullet 1
  * Bullet 2
  * …

* **Paper 2: Title**

  * Bullet 1
  * …

---

## 🚀 Roadmap

* [ ] Add **Comparer Agent** → highlight similarities/differences across papers
* [ ] Add **Report Generator** → produce full markdown/PDF “literature review”
* [ ] Add **RAG (Retrieval-Augmented Generation)** over saved papers
* [ ] Deploy with Docker + ECS/Fargate

---

## 📜 License

MIT License (or Apache 2.0 if you prefer).

---

## 🙌 Acknowledgements

* [AWS Strands Agents](https://github.com/aws-samples/strands-agents)
* [Amazon Bedrock](https://aws.amazon.com/bedrock/)
* [arXiv API](https://arxiv.org/help/api)

