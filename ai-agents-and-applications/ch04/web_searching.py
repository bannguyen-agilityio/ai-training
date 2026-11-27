from langchain_community.utilities import DuckDuckGoSearchAPIWrapper


def web_search(web_query: str, num_results: int) -> list[str]:
    return [
        r["link"] for r in DuckDuckGoSearchAPIWrapper().results(web_query, num_results)
    ]
