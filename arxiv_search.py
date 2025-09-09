from strands import Agent, tool
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlencode

@tool(name="arxiv_search", description="Search arXiv and return JSON [{title, authors, year, link}].")
def arxiv_search(query: str, max_results: int = 5) -> dict:
    base = "http://export.arxiv.org/api/query"
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max(1, min(max_results, 25)),
        "sortBy": "relevance",
        "sortOrder": "descending",
    }
    url = f"{base}?{urlencode(params)}"
    headers = {"User-Agent": "StrandsResearchAssistant/0.1 (labhansh.singla@fifthdomain.pro)"}  # arXiv asks for a contact

    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        root = ET.fromstring(r.text)
        ns = {"a": "http://www.w3.org/2005/Atom"}

        papers = []
        for entry in root.findall("a:entry", ns):
            title = (entry.findtext("a:title", default="", namespaces=ns) or "").strip()
            authors = [a.findtext("a:name", default="", namespaces=ns).strip()
                       for a in entry.findall("a:author", ns)]
            link = ""
            for l in entry.findall("a:link", ns):
                if l.attrib.get("rel") == "alternate":
                    link = l.attrib.get("href", "")
                    break
            published = entry.findtext("a:published", default="", namespaces=ns)
            year = published[:4] if published else ""
            papers.append({"title": title, "authors": authors, "year": year, "link": link})

        # Top-level must be an OBJECT, not a LIST
        return {"query": query, "count": len(papers), "papers": papers}

    except Exception as e:
        # Also return an object
        return {"error": f"arXiv error: {e}"}

# A focused "researcher" agent that knows to use the arxiv_search tool
researcher = Agent(model="anthropic.claude-3-5-sonnet-20241022-v2:0",
    system_prompt=(
        "You are a research assistant. When the user asks for papers, "
        "USE the arxiv_search tool and present a concise JSON table: "
        "[{title, authors, year, link}]."
    ),
    tools=[arxiv_search],
)

if __name__ == "__main__":
    question = "Find 3 papers on 'federated learning privacy' and show authors+year+link."
    print(researcher(question))
