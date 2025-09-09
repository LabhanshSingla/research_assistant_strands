# 03_search_and_summarize.py
from strands import Agent
from config import MODEL
from arxiv_search import arxiv_search
from summarizer import summarize_papers

# Orchestrator-lite: a single agent that can call two tools in sequence.
orchestrator = Agent(
    model=MODEL,
    system_prompt=(
        "You are an assistant that finds and summarizes research papers.\n"
        "1) Use arxiv_search to get papers.\n"
        "2) Pass the OBJECT it returns to summarize_papers.\n"
        "Finally, render a neat, human-readable summary with titles and bullet lists."
    ),
    tools=[arxiv_search, summarize_papers],
)

if __name__ == "__main__":
    query = "federated learning privacy"
    ask = f"Find 3 papers on '{query}', then summarize each in 5 bullets."
    print(orchestrator(ask))
