import re
import requests
from bs4 import BeautifulSoup


def fetch_content(url):
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    soup = BeautifulSoup(resp.text, "html.parser")

    title = soup.title.get_text(strip=True) if soup.title else ""
    h1 = soup.find("h1").get_text(strip=True) if soup.find("h1") else title

    for t in soup(["script", "style", "nav", "footer"]):
        t.decompose()

    headings = [
        (h.name, h.get_text(strip=True))
        for h in soup.find_all(re.compile(r"^h[2-3]$"))
    ]

    paragraphs = [
        p.get_text(strip=True)
        for p in soup.find_all("p")
        if len(p.get_text(strip=True)) > 40
    ]

    return {
        "title": title,
        "h1": h1,
        "headings": headings,
        "paragraphs": paragraphs,
    }


def extract_pull_quotes(paragraphs, max_quotes=5):
    quotes = []

    for para in paragraphs:
        sentences = re.split(r"(?<=[.!])\s+", para)

        for s in sentences:
            s = s.strip()

            if 60 <= len(s) <= 200:
                score = 0

                if any(w in s.lower() for w in ["important", "key", "essential", "best"]):
                    score += 2

                if re.search(r"\d+%|\d+ (times|percent)", s):
                    score += 2

                if score >= 2:
                    quotes.append({"text": s, "score": score})

    quotes.sort(key=lambda x: -x["score"])

    return [q["text"] for q in quotes[:max_quotes]]


def generate_social_posts(title, headings, paragraphs):
    posts = []

    posts.append({
        "platform": "Twitter/X",
        "text": f"🧵 {title}\n\nHere’s what you need to know 👇"
    })

    for tag, text in headings[:5]:
        if len(text) < 100:
            posts.append({
                "platform": "Twitter/X",
                "text": f"💡 {text}"
            })

    if paragraphs:
        posts.append({
            "platform": "LinkedIn",
            "text": f"I just published: {title}\n\n{paragraphs[0][:200]}..."
        })

    return posts[:5]


def generate_email_blurb(title, paragraphs):
    intro = paragraphs[0][:200] if paragraphs else ""
    return f"📝 New Post: {title}\n\n{intro}...\n\nRead more →"


def extract_key_takeaways(paragraphs, headings):
    takeaways = []

    for tag, text in headings:
        if len(text) < 80:
            takeaways.append(text)

    for para in paragraphs[-3:]:
        sentences = re.split(r"(?<=[.!])\s+", para)
        for s in sentences:
            if "key" in s.lower() or "important" in s.lower():
                takeaways.append(s[:100])

    return list(dict.fromkeys(takeaways))[:7]