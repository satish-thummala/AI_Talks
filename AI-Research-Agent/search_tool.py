
from ddgs import DDGS
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


def search_web(query, max_results=5):
    """
    Search the web and return relevant search results.
    """
    try:
        with DDGS() as ddgs:
            results = list(
                ddgs.text(
                    query,
                    max_results=max_results
                )
            )

        return results

    except Exception as e:
        print(f"Web search failed: {e}")
        return []


def extract_page_content(url, max_chars=5000):
    """
    Retrieve a web page and extract readable text.
    """
    try:
        parsed_url = urlparse(url)

        # Only retrieve ordinary HTTP/HTTPS pages.
        if parsed_url.scheme not in ("http", "https"):
            return ""

        if not parsed_url.hostname:
            return ""

        # Avoid requests to local or private network addresses.
        hostname = parsed_url.hostname.lower()

        if (
            hostname == "localhost"
            or hostname.endswith(".localhost")
            or hostname.endswith(".local")
        ):
            return ""

        response = requests.get(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(compatible; AIResearchAgent/1.0)"
                )
            },
            timeout=10
        )

        response.raise_for_status()

        content_type = response.headers.get(
            "Content-Type", ""
        ).lower()

        if "text/html" not in content_type:
            return ""

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove elements that generally aren't useful as research.
        for element in soup(
            ["script", "style", "nav", "footer", "header",
             "noscript", "svg", "form"]
        ):
            element.decompose()

        # Prefer the article or main content when available.
        main_content = soup.find("article") or soup.find("main")

        if main_content:
            text = main_content.get_text(
                separator=" ",
                strip=True
            )
        else:
            text = soup.get_text(
                separator=" ",
                strip=True
            )

        return text[:max_chars]

    except requests.RequestException as e:
        print(f"Could not retrieve {url}: {e}")
        return ""

    except Exception as e:
        print(f"Could not extract page content: {e}")
        return ""


def research_search(query, max_results=5):
    """
    Search the web and collect page content with source URLs.
    """
    search_results = search_web(query, max_results)
    research_data = []

    for result in search_results:
        url = result.get("href", "")
        title = result.get("title", "")
        snippet = result.get("body", "")

        if not url:
            continue

        content = extract_page_content(url)

        # Keep the search snippet if page extraction fails.
        if not content:
            content = snippet

        research_data.append({
            "title": title,
            "url": url,
            "snippet": snippet,
            "content": content
        })

    return research_data


if __name__ == "__main__":
    query = (
        "How are AI agents being used "
        "in customer support?"
    )

    print(f"\nResearch question: {query}\n")

    sources = research_search(query, max_results=3)

    if not sources:
        print("No search results were returned.")
    else:
        for index, source in enumerate(sources, start=1):
            print(f"\n{'=' * 60}")
            print(f"Source {index}: {source['title']}")
            print(f"URL: {source['url']}")
            print(f"\nContent preview:\n")
            print(source["content"][:700])
