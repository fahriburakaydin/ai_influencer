# agents/research_agent.py
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_openai import ChatOpenAI
from config import Config
from logger import logger
from testing import mock_text_generation, should_mock, mock_research
from exceptions import APIError

def parse_research(text: str) -> dict:
    """Convert raw text response to structured data"""
    sections = text.split("\n\n")
    return {
        "niche_trends": sections[0].split("\n")[1:],
        "content_strategies": sections[1].split("\n")[1:]
    }


def research_agent(niche: str) -> dict:
    logger.info(f"Starting research agent for: {niche}")
    
    if should_mock():
        logger.debug("Using mock research data")
        return mock_research(niche)  # Keep your existing mock
    
    try:
        # 1. Web Search Component
        search = DuckDuckGoSearchResults(backend="text", max_results=5)
        web_results = search.run(f"{niche} 2024 trends site:reddit.com OR site:twitter.com")
        
        # 2. AI Analysis (Modified from original)
        llm = ChatOpenAI(api_key=Config.OPENAI_API_KEY, temperature=0.7)
        
        research_prompt = f"""Analyze these web results and generate trends:
        Web Results: {web_results}
        
        Follow EXACTLY this format:
        Niche Trends:
        1. [Trend 1]
        2. [Trend 2]
        
        Content Strategies:
        1. [Strategy 1]
        2. [Strategy 2]"""
        
        response = llm.invoke(research_prompt)
        return parse_research(response.content)  # Keep your existing parser
        
    except Exception as e:
        logger.error(f"Research failed: {str(e)}")
        raise APIError("Research agent failed") from e


# Test search tool
search = WebSearchTool()
print(search.tools.run("latest fitness trends 2024"))

# Should work exactly like before but with real data
#print(research_agent("fitness")) 
#print(type(research_agent("fitness")) )