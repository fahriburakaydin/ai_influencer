from langchain_openai import ChatOpenAI
from langchain.agents import Tool, initialize_agent, AgentType
from langchain_core.prompts import ChatPromptTemplate
from typing import List, Dict, Union, Optional, Type
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool
import json




# Define input schema for ContentPlanner
class ContentPlannerInput(BaseModel):
    research_data: dict = Field(
        ...,
        description="Full research data from ResearchAgent containing niche_trends and content_trends"
    )


class Orchestrator:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0.5, model="gpt-3.5-turbo")
        self.tools = self._create_tools()
        self.prompt = ChatPromptTemplate.from_template(
                """Create social content for niche: {niche}. Follow EXACTLY:
                1. Use ResearchAgent with input format: {{"input": "{niche}"}}
                2. Pass FULL output to ContentPlanner as: {{"research_data": <ResearchAgent_output>}}
                3. For each idea in content plan, use ImageGenerator"""
            )
        

    def _create_tools(self) -> list:
        return [
            StructuredTool.from_function(
                name="ResearchAgent",
                func=self._research_wrapper,
                description="Researches trends for a niche. Input: niche string",
                args_schema=None
            ),
            StructuredTool.from_function(
                name="ContentPlanner",
                func=self._planning_wrapper,
                description="Creates content plans from research data. Input: research_data dict",
                args_schema=ContentPlannerInput
            ),
            StructuredTool.from_function(
                name="ImageGenerator",
                func=self._image_wrapper,
                description="Generates an image URL for a given content idea. Input: idea string",
                args_schema=None
            ),
            StructuredTool.from_function(
                name="CaptionGenerator",
                func=self._caption_wrapper,
                description="Generates an Instagram caption for a given content idea. Input: idea string",
                args_schema=None
            )
        ]
    
    
    

    def _planning_wrapper(self, research_data: dict) -> dict:
        """Wrapper that strictly accepts research_data dict"""
        from .content_planner import content_planner
        return content_planner(research_data)


    
    def _research_wrapper(self, niche: str) -> Dict:
        from .research_agent import research_agent
        return research_agent(niche)
    
    
    def _image_wrapper(self, idea: str) -> str:
        from .image_generator import generate_image
        return generate_image(idea)
    
    def _caption_wrapper(self, idea: str) -> str:
        from .caption_generator import generate_caption
        return generate_caption(idea)
    
    from langchain_openai import ChatOpenAI
from langchain.agents import Tool, initialize_agent, AgentType
from langchain_core.prompts import ChatPromptTemplate
from typing import List, Dict, Union, Optional, Type
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool
import json




# Define input schema for ContentPlanner
class ContentPlannerInput(BaseModel):
    research_data: dict = Field(
        ...,
        description="Full research data from ResearchAgent containing niche_trends and content_trends"
    )


class Orchestrator:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0.5, model="gpt-3.5-turbo")
        self.tools = self._create_tools()
        self.prompt = ChatPromptTemplate.from_template(
                """Create social content for niche: {niche}. Follow EXACTLY:
                1. Use ResearchAgent with input format: {{"input": "{niche}"}}
                2. Pass FULL output to ContentPlanner as: {{"research_data": <ResearchAgent_output>}}
                3. For each idea in content plan, use ImageGenerator"""
            )
        

    def _create_tools(self) -> list:
        return [
            StructuredTool.from_function(
                name="ResearchAgent",
                func=self._research_wrapper,
                description="Researches trends for a niche. Input: niche string",
                args_schema=None
            ),
            StructuredTool.from_function(
                name="ContentPlanner",
                func=self._planning_wrapper,
                description="Creates content plans from research data. Input: research_data dict",
                args_schema=ContentPlannerInput
            ),
            StructuredTool.from_function(
                name="ImageGenerator",
                func=self._image_wrapper,
                description="Generates an image URL for a given content idea. Input: idea string",
                args_schema=None
            ),
            StructuredTool.from_function(
                name="CaptionGenerator",
                func=self._caption_wrapper,
                description="Generates an Instagram caption for a given content idea. Input: idea string",
                args_schema=None
            )
        ]
    
    
    

    def _planning_wrapper(self, research_data: dict) -> dict:
        """Wrapper that strictly accepts research_data dict"""
        from .content_planner import content_planner
        return content_planner(research_data)


    
    def _research_wrapper(self, niche: str) -> Dict:
        from .research_agent import research_agent
        return research_agent(niche)
    
    
    def _image_wrapper(self, idea: str) -> str:
        from .image_generator import generate_image
        return generate_image(idea)
    
    def _caption_wrapper(self, idea: str) -> str:
        from .caption_generator import generate_caption
        return generate_caption(idea)
    
    def create_workflow(self, niche: str) -> Dict:
        agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )
    
        prompt_text = (
            f"""Create social content for niche: {niche}. 
            Follow these steps: 
            1. Use ResearchAgent with input: {niche}. 
            2. Pass the output of ResearchAgent to ContentPlanner as {{'research_data': <ResearchAgent_output>}}. 
            3. For each idea in the content plan, use ImageGenerator to generate an image. 
            4. Then, use CaptionGenerator to generate an Instagram caption. 
            Finally, return the result as a JSON object with a key 'posts' that contains a list of posts. 
            Each post should be a JSON object with keys 'idea', 'image', and 'caption'."""
        )
        
        response = agent.run(prompt_text)
        
        # Check if the response is a dict or a string.
        if isinstance(response, dict):
            result = response
        elif isinstance(response, str):
            try:
                result = json.loads(response)
            except Exception as e:
                raise ValueError("Orchestrator output is not valid JSON") from e
        else:
            raise ValueError("Orchestrator output is of an unrecognized type")
        
        return result