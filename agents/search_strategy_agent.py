# Search strategy agent
"""
Search strategy agent using LangGraph framework.
"""

import logging
from typing import Dict, List, Any, TypedDict, Optional, cast

from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END

from agents.agent_prompts import SEARCH_STRATEGY_PROMPT
from agents.agent_tools import SearchStrategyTools

logger = logging.getLogger(__name__)

# Define the state for the search strategy graph
class SearchStrategyState(TypedDict):
    name: str
    strategy_text: Optional[str]
    platforms: Optional[List[str]]
    search_terms: Optional[List[str]]
    name_variations: Optional[List[str]]
    regions: Optional[List[str]]
    time_period: Optional[str]
    errors: Optional[List[Dict[str, Any]]]


class SearchStrategyAgent:
    """Agent for generating search strategies for a person."""
    
    def __init__(self, model_name: str = "gpt-4-turbo", temperature: float = 0.2):
        """Initialize the search strategy agent."""
        self.tools = SearchStrategyTools()
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)
        self.prompt = ChatPromptTemplate.from_template(SEARCH_STRATEGY_PROMPT)
        self.output_parser = StrOutputParser()
        
        # Create and compile the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph for search strategy generation."""
        # Define the nodes
        def generate_strategy(state: SearchStrategyState) -> SearchStrategyState:
            """Generate a search strategy based on the name."""
            try:
                name = state["name"]
                
                # Create the prompt
                chain = self.prompt | self.llm | self.output_parser
                
                # Generate strategy
                strategy_text = chain.invoke({"name": name})
                
                # Update state
                state["strategy_text"] = strategy_text
                
                return state
            except Exception as e:
                logger.error(f"Error generating search strategy: {str(e)}")
                if "errors" not in state:
                    state["errors"] = []
                state["errors"].append({
                    "step": "generate_strategy",
                    "error": str(e)
                })
                return state
        
        def extract_strategy_components(state: SearchStrategyState) -> SearchStrategyState:
            """Extract components from the strategy text."""
            try:
                strategy_text = state.get("strategy_text", "")
                if not strategy_text:
                    return state
                
                # Extract components
                platforms = self.tools.extract_platforms(strategy_text)
                search_terms = self.tools.extract_search_terms(strategy_text)
                name_variations = self.tools.extract_name_variations(strategy_text)
                regions = self.tools.extract_regions(strategy_text)
                time_period = self.tools.extract_time_period(strategy_text)
                
                # Update state
                state["platforms"] = platforms
                state["search_terms"] = search_terms
                state["name_variations"] = name_variations
                state["regions"] = regions
                state["time_period"] = time_period
                
                return state
            except Exception as e:
                logger.error(f"Error extracting strategy components: {str(e)}")
                if "errors" not in state:
                    state["errors"] = []
                state["errors"].append({
                    "step": "extract_strategy_components",
                    "error": str(e)
                })
                return state
        
        # Build the graph
        workflow = StateGraph(SearchStrategyState)
        
        # Add nodes
        workflow.add_node("generate_strategy", generate_strategy)
        workflow.add_node("extract_strategy_components", extract_strategy_components)
        
        # Add edges
        workflow.add_edge("generate_strategy", "extract_strategy_components")
        workflow.add_edge("extract_strategy_components", END)
        
        # Set entry point
        workflow.set_entry_point("generate_strategy")
        
        # Compile the graph
        return workflow.compile()
    
    async def generate_search_strategy(self, name: str) -> Dict[str, Any]:
        """Generate a search strategy for a person."""
        # Initialize state
        initial_state: SearchStrategyState = {
            "name": name,
            "strategy_text": None,
            "platforms": None,
            "search_terms": None,
            "name_variations": None,
            "regions": None,
            "time_period": None,
            "errors": None
        }
        
        # Run the graph
        result = await self.graph.ainvoke(initial_state)
        
        # Create a clean result
        clean_result = {
            "name": name,
            "platforms": result.get("platforms", []),
            "search_terms": result.get("search_terms", [name]),
            "name_variations": result.get("name_variations", []),
            "regions": result.get("regions", []),
            "time_period": result.get("time_period", "1 year")
        }
        
        if not clean_result["search_terms"]:
            clean_result["search_terms"] = [name]
        
        return clean_result