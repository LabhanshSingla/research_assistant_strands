# config.py
from strands.models import BedrockModel

BEDROCK_REGION = "ap-southeast-2"  # or your preferred region

MODEL = BedrockModel(
    model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
    region_name=BEDROCK_REGION,
    temperature=0.2,
    max_tokens=2000,
)

# 02_summarizer_tool.py
from strands import Agent, tool
from config import MODEL
import json

# LLM-only agent that writes short, factual bullet summaries.
summarizer = Agent(
    model=MODEL,
    system_prompt=(
        "You are a precise research summarizer. For each paper, produce 5 short, "
        "factual bullets (no fluff). Avoid speculation. If info is missing, say 'Not stated'. "
        "Return ONLY valid JSON matching the schema you are instructed to use."
    ),
)

@tool(
    name="summarize_papers",
    description=(
        "Summarize a list of papers into concise bullets. "
        "Input: object with key 'papers': [{title, authors, year, link}]. "
        "Returns object: {'count': N, 'items': [{'title', 'bullets': [...], 'link'}]}."
    ),
)
def summarize_papers(papers_obj: dict, max_per_paper: int = 5) -> dict:
    """
    Args:
        papers_obj: {'papers': [{title, authors, year, link}], ...}
        max_per_paper: bullets per paper (default 5)
    Returns:
        OBJECT (not list):
            {
              "count": N,
              "items": [
                {"title": str, "bullets": [str, ... up to N], "link": str}
              ]
            }
    """
    try:
        if not isinstance(papers_obj, dict) or "papers" not in papers_obj:
            return {"error": "Expected object with key 'papers'."}

        papers = papers_obj.get("papers", [])[:10]  # keep it reasonable
        # Ask the LLM to emit strict JSON we can load
        schema = {
            "type": "object",
            "properties": {
                "count": {"type": "number"},
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "bullets": {
                                "type": "array",
                                "items": {"type": "string"},
                                "maxItems": max_per_paper,
                            },
                            "link": {"type": "string"},
                        },
                        "required": ["title", "bullets", "link"],
                    },
                },
            },
            "required": ["count", "items"],
        }

        prompt = {
            "instruction": (
                "Summarize each paper in up to "
                f"{max_per_paper} bullets. Use ONLY information inferable from title/authors/year "
                "and avoid claims you cannot verify."
            ),
            "schema_hint": schema,
            "papers": papers,
            "output_must_be_valid_json_object": True,
            "output_shape": {
                "count": len(papers),
                "items": [{"title": "<string>", "bullets": ["<string>"], "link": "<string>"}],
            },
        }

        # Call the summarizer agent
        raw = summarizer(
            "Return ONLY JSON.\n"
            "Schema: {count:number, items:[{title:string, bullets:string[], link:string}]}\n"
            f"Here are the papers:\n{json.dumps(papers, ensure_ascii=False)}"
        )

        # Try to parse JSON; if it fails, wrap a fallback object
        try:
            obj = json.loads(str(raw))
            if not isinstance(obj, dict):
                raise ValueError("LLM returned non-object JSON.")
            # Optionally normalize/truncate bullets length
            for it in obj.get("items", []):
                if isinstance(it.get("bullets"), list) and len(it["bullets"]) > max_per_paper:
                    it["bullets"] = it["bullets"][:max_per_paper]
            # ensure count is present/accurate
            obj["count"] = len(obj.get("items", []))
            return obj
        except Exception as parse_err:
            # Fallback: very light, still an OBJECT
            items = [
                {
                    "title": p.get("title", ""),
                    "bullets": ["Summary unavailable (parse error)."],
                    "link": p.get("link", ""),
                }
                for p in papers
            ]
            return {
                "count": len(items),
                "items": items,
                "error": f"JSON parse error: {parse_err}",
            }
    except Exception as e:
        return {"count": 0, "items": [], "error": f"summarize_papers error: {e}"}
