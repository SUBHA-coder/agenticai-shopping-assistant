import os
import re
import requests
from typing import List, Dict
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

if not GROQ_API_KEY or not SERPER_API_KEY:
    raise ValueError("Missing GROQ_API_KEY or SERPER_API_KEY in environment")

# -------------------------
# LLM Init
# -------------------------
def get_llm(model: str = "llama3-70b-8192") -> ChatGroq:
    return ChatGroq(api_key=GROQ_API_KEY, model=model)

# -------------------------
# Product Research
# -------------------------
def research_product(llm: ChatGroq, query: str) -> str:
    prompt = ChatPromptTemplate.from_template(
        "You are a meticulous product researcher. "
        "Find structured details about: {query}\n"
        "Include: key features, build/comfort, pros, cons, who it’s best for.\n"
        "Keep it concise and factual."
    )
    res = llm.invoke(prompt.format(query=query))
    return res.content

# -------------------------
# Serper Shopping Search
# -------------------------
def search_prices_serper(query: str) -> Dict:
    url = "https://google.serper.dev/shopping"
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
    resp = requests.post(url, headers=headers, json={"q": query})
    if resp.status_code != 200:
        return {"shopping": [], "error": resp.text}
    return resp.json()

# -------------------------
# Currency Parsing + INR Conversion
# -------------------------
_CURRENCY_MAP = {
    "$": "USD",
    "US$": "USD",
    "USD": "USD",
    "€": "EUR",
    "EUR": "EUR",
    "£": "GBP",
    "GBP": "GBP",
    "₹": "INR",
    "INR": "INR",
}

def _detect_currency(price_str: str) -> str:
    if not price_str:
        return "USD"
    for sym, cur in _CURRENCY_MAP.items():
        if sym in price_str:
            return cur
    return "USD"  # fallback

def _extract_first_number(price_str: str) -> float | None:
    if not price_str:
        return None
    # Handles "from $89.99", "$89.99 - $129.99", "USD 100", etc.
    match = re.search(r"(\d{1,3}(?:,\d{3})*(?:\.\d+)?)", price_str.replace(",", ""))
    if not match:
        return None
    try:
        return float(match.group(1))
    except Exception:
        return None

def convert_to_inr(price_str: str, usd_inr: float = 83.0, eur_inr: float = 90.0, gbp_inr: float = 105.0) -> str:
    """
    Converts common currency strings to INR.
    If already INR or parsing fails, returns original string.
    """
    if not price_str:
        return "N/A"
    cur = _detect_currency(price_str)
    val = _extract_first_number(price_str)
    if val is None:
        return price_str

    if cur == "INR":
        # Already INR — normalize to ₹xx.xx if possible
        return f"₹{round(val, 2)}"
    elif cur == "USD":
        return f"₹{round(val * usd_inr, 2)}"
    elif cur == "EUR":
        return f"₹{round(val * eur_inr, 2)}"
    elif cur == "GBP":
        return f"₹{round(val * gbp_inr, 2)}"
    else:
        # Unknown currency — just return original
        return price_str

# -------------------------
# Summarize/Format Serper Results
# -------------------------
def summarize_prices_for_prompt(prices_json: Dict, top_n: int = 8, usd_inr: float = 83.0) -> str:
    items = prices_json.get("shopping", [])[:top_n]
    lines = []
    for item in items:
        title = item.get("title") or "N/A"
        price = item.get("price") or "N/A"
        link = item.get("link") or "N/A"
        price_inr = convert_to_inr(price, usd_inr=usd_inr)
        lines.append(f"- {title} | {price_inr} (orig: {price}) | {link}")
    return "\n".join(lines)

def make_price_rows(prices_json: Dict, top_n: int = 8, usd_inr: float = 83.0) -> List[Dict]:
    items = prices_json.get("shopping", [])[:top_n]
    rows = []
    for it in items:
        title = it.get("title") or "N/A"
        price = it.get("price") or "N/A"
        link = it.get("link") or "N/A"
        rows.append({
            "Title": title,
            "Price (Original)": price,
            "Price (INR)": convert_to_inr(price, usd_inr=usd_inr),
            "Link": link
        })
    return rows

# -------------------------
# Final Report
# -------------------------
def build_final_report(llm: ChatGroq, research: str, price_summary_text: str) -> str:
    prompt = ChatPromptTemplate.from_template(
        "You are a helpful shopping assistant.\n\n"
        "Product Research:\n{research}\n\n"
        "Prices (INR shown, original in brackets):\n{prices}\n\n"
        "Write a clear, well-structured final report that:\n"
        "1) Summarizes key features, pros, cons.\n"
        "2) Shows a compact comparison table.\n"
        "3) Recommends the best option with reasoning for an Indian buyer.\n"
        "Keep it concise."
    )
    res = llm.invoke(prompt.format(research=research, prices=price_summary_text))
    return res.content
