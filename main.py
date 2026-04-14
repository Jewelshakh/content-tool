from fastapi import FastAPI
from content_repurposer import (
    fetch_content,
    extract_pull_quotes,
    generate_social_posts,
    generate_email_blurb,
    extract_key_takeaways
)

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Content Repurposer API running 🚀"}

@app.get("/api/generate")
def generate(url: str):
    data = fetch_content(url)

    return {
        "title": data["title"],
        "quotes": extract_pull_quotes(data["paragraphs"]),
        "social": generate_social_posts(
            data["title"], data["headings"], data["paragraphs"]
        ),
        "email": generate_email_blurb(data["title"], data["paragraphs"]),
        "takeaways": extract_key_takeaways(
            data["paragraphs"], data["headings"]
        )
    }