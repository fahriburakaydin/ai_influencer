import json
from testing import should_mock, mock_research
from crewai import Agent, Task, Crew
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.tools import Tool
from exceptions import APIError
from logger import logger
from pydantic import BaseModel, Field, ValidationError
from typing import Union, Any, Dict, Optional, List

# Define a Pydantic model for the Web Search input
class WebSearchInput(BaseModel):
    query: Union[str, Dict[str, Any]] = Field(
        ..., 
        description="The search query or parameters for the search"
    )
    timeframe: Optional[str] = Field(
        None, 
        description="Optional timeframe for the search"
    )

# Rebuild the model to resolve forward references
WebSearchInput.model_rebuild()

# Define a Pydantic model for the research data output
class ResearchData(BaseModel):
    niche_trends: List[str]
    content_strategies: List[str]

# Create CrewAI-compatible tool wrapper with a wrapper function
class WebSearchTool:
    def __init__(self):
        self.search = DuckDuckGoSearchRun()
    
    def _run(self, **kwargs):
        query = kwargs.get("query")
        timeframe = kwargs.get("timeframe")
        if timeframe:
            query = f"{query} ({timeframe})"
        return self.search.run(query)
        
    @property
    def tools(self):
        return Tool(
            name="Web Search",
            func=self._run,
            description="Searches the web for current trends",
            args_schema=WebSearchInput
        )

def research_agent(niche: str) -> dict:
    logger.info(f"Starting research agent for: {niche}")
    
    if should_mock():
        logger.debug("Using mock research data")
        return mock_research(niche)

    try:
        search_tool = WebSearchTool().tools

        researcher = Agent(
            role="Senior Social Media Analyst",
            goal=f"Find viral trends in {niche}",
            backstory="Expert in spotting emerging trends",
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
            max_iter=3  # Limit to 3 reasoning steps
        )

        analyst = Agent(
            role="Content Strategy Expert",
            goal="Convert trends into actionable strategies",
            backstory="Former social media manager for top influencers",
            verbose=True,
            allow_delegation=False,
            max_iter=2  # Limit to 2 reasoning steps
        )

        research_task = Task(
            description=f"""Use the 'Web Search' tool to find current {niche} trends on social media platforms.
Focus your search on recent discussions (last 3 months) related to '{niche} trends on social media'.
Return 5-7 raw trending topics in bullet points.""",
            agent=researcher,
            expected_output="Bullet point list of trends:\n- Trend 1\n- Trend 2"
        )
        
        analysis_task = Task(
            description=f"""Convert these trends into content strategies for Instagram.
Use this format:
            
Niche Trends:
1. [Formatted trend 1]
2. [Formatted trend 2]
            
Content Strategies:
1. [Actionable strategy 1]
2. [Actionable strategy 2]""",
            agent=analyst,
            # Expected output is strict JSON.
            expected_output=('{"niche_trends": ["1. Trend_1", "2. Trend_2"], '
'"content_strategies": ["1. Strategy_1", "2. Strategy_2"]}'),
            context=[research_task]
        )

        crew = Crew(
            agents=[researcher, analyst],
            tasks=[research_task, analysis_task],
            verbose=True,
            memory=False
        )
        
        result = crew.kickoff()
        result_dict = result.dict()
        tasks_output = result_dict.get("tasks_output", [])
        
        analysis_output_str = None
        for task in tasks_output:
            if task.get("agent") == "Content Strategy Expert":
                analysis_output_str = task.get("raw")
                break
        if not analysis_output_str:
            raise APIError("Content Strategy Expert output not found.")
        
        # Try to parse the output as JSON. If it fails due to single quotes, convert them.
        try:
            research_data_obj = ResearchData.parse_raw(analysis_output_str)
        except ValidationError as e:
            logger.error("Initial JSON parsing failed, attempting to replace single quotes with double quotes.")
            json_ready = analysis_output_str.replace("'", '"')
            try:
                research_data_obj = ResearchData.parse_raw(json_ready)
            except ValidationError as e2:
                raise APIError("Parsed research data does not match expected schema.") from e2
        
        return research_data_obj.dict()
        
    except Exception as e:
        logger.error(f"Crew failed: {str(e)}")
        raise APIError("Research agent failed") from e

if __name__ == "__main__":
    print(research_agent("fitness"))
