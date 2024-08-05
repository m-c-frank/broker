# URL_EMBEDDING_MODEL="http://localhost:11434/v1/embeddings"
# curl http://localhost:11434/v1/embeddings \
#   -H "Content-Type: application/json" \
#   -H "Authorization: Bearer $OPENAI_API_KEY" \
#   -d '{
#     "input": "Your text string goes here",
#     "model": "all-minilm"
#   }'

import httpx

# URL_EMBEDDING_MODEL="http://localhost:11434/v1/embeddings"
def embed_text(text: str, model: str) -> dict:
    url = "http://localhost:11434/v1/embeddings"
    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "input": text,
        "model": model,
    }
    response = httpx.post(url, headers=headers, json=data)
    response.raise_for_status()

    return response.json()["data"][0]["embedding"]

embedder = embed_text

if __name__ == "__main__":
    text = "Your text string goes here"
    model = "all-minilm"
    result = embed_text(text, model)
    print(result)