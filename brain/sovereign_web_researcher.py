"""
Jessica Brain - Sovereign Web Researcher (Phase 13.5)
100% Local Python Web Intelligence & Knowledge Scraping (Zero 3rd-Party AI / Zero Cloud API Keys).
Scrapes DuckDuckGo Instant Answers, DuckDuckGo HTML search results, and Wikipedia REST API
to provide fast, real-time grounded web context (<1.2s) for JessicaCortex-8B-v8.
"""

import os
import sys
import re
import json
import time
import urllib.parse
import urllib.request
from typing import Dict, Any, List, Optional

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9"
}


def query_duckduckgo_instant_answer(query: str, timeout: float = 2.5) -> Optional[Dict[str, Any]]:
    """
    Queries DuckDuckGo Instant Answer API for quick zero-click definitions & infoboxes.
    """
    clean_q = query.strip()
    url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(clean_q)}&format=json&no_html=1&skip_disambig=1"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            abstract = data.get("AbstractText", "").strip()
            answer = data.get("Answer", "").strip()
            source = data.get("AbstractSource", "DuckDuckGo")
            source_url = data.get("AbstractURL", "")

            content = abstract or answer
            if content and len(content) > 20:
                return {
                    "source": source,
                    "title": data.get("Heading", clean_q),
                    "summary": content,
                    "url": source_url or "https://duckduckgo.com"
                }
    except Exception as e:
        # Silently fall back to HTML search
        pass
    return None


def query_wikipedia_summary(topic: str, timeout: float = 2.5) -> Optional[Dict[str, Any]]:
    """
    Queries Wikipedia REST API for authoritative technical / encyclopedia topics.
    """
    # Clean topic for URL
    clean_topic = re.sub(r'^(?:what is|who is|explain|tell me about)\s+', '', topic, flags=re.IGNORECASE).strip(" ?.,!")
    formatted = clean_topic.replace(" ", "_")
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(formatted)}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "JessicaSovereignAI/1.0 (academic-research@jessica.local)"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            extract = data.get("extract", "").strip()
            if extract and len(extract) > 25:
                return {
                    "source": "Wikipedia",
                    "title": data.get("title", clean_topic),
                    "summary": extract,
                    "url": data.get("content_urls", {}).get("desktop", {}).get("page", f"https://en.wikipedia.org/wiki/{formatted}")
                }
    except Exception:
        pass
    return None


def query_duckduckgo_html(query: str, max_results: int = 3, timeout: float = 3.0) -> List[Dict[str, str]]:
    """
    Scrapes DuckDuckGo HTML search results for real-time web search snippets.
    """
    clean_q = query.strip()
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(clean_q)}"
    results = []
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            html = resp.read().decode("utf-8", errors="ignore")

            # Extract snippets using regex patterns on DuckDuckGo HTML
            snippets = re.findall(r'<a class="result__snippet[^>]*>(.*?)</a>', html, re.DOTALL)
            titles = re.findall(r'<a class="result__url[^>]*>(.*?)</a>', html, re.DOTALL)
            links = re.findall(r'<a class="result__url"[^>]*href="([^"]*)"', html)

            for i in range(min(len(snippets), max_results)):
                raw_snip = re.sub(r'<[^>]+>', '', snippets[i]).strip()
                # Clean html entities
                raw_snip = raw_snip.replace("&quot;", '"').replace("&amp;", '&').replace("&#x27;", "'").replace("&lt;", '<').replace("&gt;", '>')
                if len(raw_snip) > 20:
                    results.append({
                        "snippet": raw_snip,
                        "url": links[i] if i < len(links) else ""
                    })
    except Exception as e:
        pass
    return results


def search_live_web(query: str) -> Dict[str, Any]:
    """
    Executes multi-source sovereign web research:
    1. Checks DuckDuckGo Instant Answer (<0.4s)
    2. Checks Wikipedia REST Summary (<0.5s)
    3. Checks DuckDuckGo HTML snippets (<0.8s)
    Returns consolidated findings and clean 1-2 sentence spoken summary.
    """
    t0 = time.perf_counter()
    findings = []
    best_summary = ""
    source_name = "Web"
    source_url = ""

    # 1. DuckDuckGo Instant Answer
    ddg_ia = query_duckduckgo_instant_answer(query)
    if ddg_ia:
        findings.append(ddg_ia["summary"])
        best_summary = ddg_ia["summary"]
        source_name = ddg_ia["source"]
        source_url = ddg_ia["url"]

    # 2. Wikipedia Summary
    if not best_summary or len(best_summary) < 50:
        wiki = query_wikipedia_summary(query)
        if wiki:
            findings.append(wiki["summary"])
            best_summary = wiki["summary"]
            source_name = "Wikipedia"
            source_url = wiki["url"]

    # 3. DuckDuckGo HTML snippets
    if not best_summary or len(best_summary) < 50:
        html_results = query_duckduckgo_html(query, max_results=3)
        if html_results:
            snips = [r["snippet"] for r in html_results]
            findings.extend(snips)
            best_summary = " ".join(snips[:2])
            source_name = "DuckDuckGo Web"
            source_url = html_results[0].get("url", "")

    # Clean summary down to 2 concise spoken sentences
    clean_summary = ""
    if best_summary:
        # Split sentences cleanly
        sents = re.split(r'(?<=[.!?])\s+', best_summary.strip())
        clean_summary = " ".join(sents[:2]).strip()

    elapsed = round(time.perf_counter() - t0, 3)

    return {
        "query": query,
        "summary": clean_summary or f"I searched the web for '{query}' but found limited immediate snippets.",
        "findings": findings,
        "source": source_name,
        "url": source_url,
        "elapsed_sec": elapsed
    }


if __name__ == "__main__":
    test_q = "RTX 4060 specifications"
    print(f"[*] Testing sovereign web search for: '{test_q}'...")
    res = search_live_web(test_q)
    print(f"[+] Result in {res['elapsed_sec']}s ({res['source']}):")
    print(f"    Summary: {res['summary']}")
    print(f"    URL: {res['url']}")

