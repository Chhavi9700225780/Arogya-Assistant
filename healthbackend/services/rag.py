import json
import os

# Path to the local knowledge base file used for simple RAG-style lookup
KB_PATH = "data/knowledge.json"


def retrieve_context(query: str, top_k: int = 2) -> str:
    """
    Very lightweight keyword-based retriever over a local JSON knowledge base.

    Args:
        query: User symptom / question text used to find relevant snippets.
        top_k: Maximum number of matching snippets to return.

    Returns:
        A single string containing up to `top_k` snippets joined with newlines.
        Returns an empty string if the knowledge base file does not exist
        or no snippets match.
    """
    # If the knowledge base file is missing, just return empty context
    if not os.path.exists(KB_PATH):
        return ""

    # Load the JSON file: expected format is a list of objects,
    # each with at least a "content" field containing text.
    with open(KB_PATH, "r", encoding="utf-8") as f:
        docs = json.load(f)

    # Lowercase version of the query for case-insensitive matching
    query_l = query.lower()
    hits = []

    # Naive keyword search:
    # - Split the query into individual words
    # - For each document, check if ANY word appears in its content
    for doc in docs:
        if any(word in doc["content"].lower() for word in query_l.split()):
            hits.append(doc["content"])

    # Return at most `top_k` matching snippets, joined by newlines
    return "\n".join(hits[:top_k])
