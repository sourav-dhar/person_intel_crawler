# LangGraph workflow coordinator
"""
LangGraph coordinator for the Person Intelligence Crawler.

This module orchestrates the entire workflow using LangGraph, including:
1. Search strategy generation
2. Data collection
3. Data analysis
4. Summary generation
5. Risk assessment
"""

import logging
from typing import Dict, List, Any, TypedDict, Optional, Tuple, Set
import asyncio

from langgraph.graph import StateGraph, END

from config.llm_config import LLMConfig
from models.intelligence_models import PersonIntelligence
from models.base_models import RiskLevel
from models.social_media_models import SocialMediaProfile
from models.pep_models import PEPRecord
from models.media_models import NewsArticle

from agents.search_strategy_agent import SearchStrategyAgent
from agents.analysis_agents import (
    PEPAnalysisAgent,
    SocialMediaAnalysisAgent,
    MediaAnalysisAgent,
    IntelligenceSummaryAgent,
    RiskAssessmentAgent
)

logger = logging.getLogger(__name__)

# Define the state for the overall intelligence workflow
class IntelligenceWorkflowState(TypedDict):
    name: str
    search_strategy: Optional[Dict[str, Any]]
    social_media_profiles: Optional[Dict[str, List[SocialMediaProfile]]]
    pep_records: Optional[List[PEPRecord]]
    news_articles: Optional[List[NewsArticle]]
    social_media_analysis: Optional[str]
    pep_analysis: Optional[str]
    media_analysis: Optional[str]
    intelligence_summary: Optional[str]
    risk_level: Optional[RiskLevel]
    confidence_score: Optional[float]
    risk_justification: Optional[str]
    sources_checked: Optional[Set[str]]
    sources_successful: Optional[Set[str]]
    errors: Optional[List[Dict[str, Any]]]
    result: Optional[PersonIntelligence]


class LangGraphCoordinator:
    """Coordinator for the entire intelligence gathering workflow using LangGraph."""
    
    def __init__(self, config: LLMConfig):
        """Initialize the LangGraph coordinator."""
        self.config = config
        
        # Initialize agents
        self.search_strategy_agent = SearchStrategyAgent(
            model_name=config.model_name,
            temperature=config.temperature
        )
        
        self.pep_analysis_agent = PEPAnalysisAgent(
            model_name=config.model_name,
            temperature=config.temperature
        )
        
        self.social_media_analysis_agent = SocialMediaAnalysisAgent(
            model_name=config.model_name,
            temperature=config.temperature
        )
        
        self.media_analysis_agent = MediaAnalysisAgent(
            model_name=config.model_name,
            temperature=config.temperature
        )
        
        self.intelligence_summary_agent = IntelligenceSummaryAgent(
            model_name=config.model_name,
            temperature=config.temperature
        )
        
        self.risk_assessment_agent = RiskAssessmentAgent(
            model_name=config.model_name,
            temperature=config.temperature
        )
        
        # Create and compile the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph for the intelligence workflow."""
        # Define the nodes
        async def generate_search_strategy(state: IntelligenceWorkflowState) -> IntelligenceWorkflowState:
            """Generate a search strategy for the person."""
            try:
                name = state["name"]
                
                # Generate search strategy
                search_strategy = await self.search_strategy_agent.generate_search_strategy(name)
                
                # Update state
                state["search_strategy"] = search_strategy
                
                return state
            except Exception as e:
                logger.error(f"Error generating search strategy: {str(e)}")
                if "errors" not in state:
                    state["errors"] = []
                state["errors"].append({
                    "step": "generate_search_strategy",
                    "error": str(e)
                })
                # Create a default search strategy
                state["search_strategy"] = {
                    "name": state["name"],
                    "platforms": ["twitter", "linkedin", "facebook"],
                    "search_terms": [state["name"]],
                    "name_variations": [],
                    "regions": [],
                    "time_period": "1 year"
                }
                return state
        
        # This function would normally call the crawlers to collect data
        # For this implementation, we'll assume the data is already provided
        async def collect_data(state: IntelligenceWorkflowState) -> IntelligenceWorkflowState:
            """Collect data using the crawlers (placeholder function)."""
            # In a real implementation, this would use the search strategy
            # to collect data from the various sources
            # Here we'll just pass through the data that was provided
            
            # Update sources checked
            if "sources_checked" not in state or not state["sources_checked"]:
                state["sources_checked"] = set()
                
            if "sources_successful" not in state or not state["sources_successful"]:
                state["sources_successful"] = set()
            
            # If we have social media profiles, mark those sources as checked
            if state.get("social_media_profiles"):
                for platform in state["social_media_profiles"].keys():
                    state["sources_checked"].add(f"social:{platform}")
                    state["sources_successful"].add(f"social:{platform}")
            
            # If we have PEP records, mark those sources as checked
            if state.get("pep_records"):
                pep_sources = set([f"pep:{record.source}" for record in state["pep_records"]])
                state["sources_checked"].update(pep_sources)
                state["sources_successful"].update(pep_sources)
            
            # If we have news articles, mark those sources as checked
            if state.get("news_articles"):
                media_sources = set([f"media:{article.source.split(':', 1)[0]}" for article in state["news_articles"]])
                state["sources_checked"].update(media_sources)
                state["sources_successful"].update(media_sources)
            
            return state
        
        async def analyze_social_media(state: IntelligenceWorkflowState) -> IntelligenceWorkflowState:
            """Analyze social media profiles."""
            try:
                name = state["name"]
                social_media_profiles = state.get("social_media_profiles", {})
                
                # Analyze social media data
                social_media_analysis = await self.social_media_analysis_agent.analyze_social_media_data(
                    name, social_media_profiles
                )
                
                # Update state
                state["social_media_analysis"] = social_media_analysis
                
                return state
            except Exception as e:
                logger.error(f"Error analyzing social media data: {str(e)}")
                if "errors" not in state:
                    state["errors"] = []
                state["errors"].append({
                    "step": "analyze_social_media",
                    "error": str(e)
                })
                state["social_media_analysis"] = "No relevant social media profiles were found."
                return state
        
        async def analyze_pep_data(state: IntelligenceWorkflowState) -> IntelligenceWorkflowState:
            """Analyze PEP records."""
            try:
                name = state["name"]
                pep_records = state.get("pep_records", [])
                
                # Analyze PEP data
                pep_analysis = await self.pep_analysis_agent.analyze_pep_data(
                    name, pep_records
                )
                
                # Update state
                state["pep_analysis"] = pep_analysis
                
                return state
            except Exception as e:
                logger.error(f"Error analyzing PEP data: {str(e)}")
                if "errors" not in state:
                    state["errors"] = []
                state["errors"].append({
                    "step": "analyze_pep_data",
                    "error": str(e)
                })
                state["pep_analysis"] = "No PEP (Politically Exposed Person) database matches were found."
                return state
        
        async def analyze_media_data(state: IntelligenceWorkflowState) -> IntelligenceWorkflowState:
            """Analyze news articles."""
            try:
                name = state["name"]
                news_articles = state.get("news_articles", [])
                
                # Analyze media data
                media_analysis = await self.media_analysis_agent.analyze_media_data(
                    name, news_articles
                )
                
                # Update state
                state["media_analysis"] = media_analysis
                
                return state
            except Exception as e:
                logger.error(f"Error analyzing media data: {str(e)}")
                if "errors" not in state:
                    state["errors"] = []
                state["errors"].append({
                    "step": "analyze_media_data",
                    "error": str(e)
                })
                state["media_analysis"] = "No relevant media mentions were found."
                return state
        
        async def generate_intelligence_summary(state: IntelligenceWorkflowState) -> IntelligenceWorkflowState:
            """Generate a comprehensive intelligence summary."""
            try:
                name = state["name"]
                social_media_analysis = state.get("social_media_analysis", "No relevant social media profiles were found.")
                pep_analysis = state.get("pep_analysis", "No PEP (Politically Exposed Person) database matches were found.")
                media_analysis = state.get("media_analysis", "No relevant media mentions were found.")
                
                # Generate intelligence summary
                intelligence_summary = await self.intelligence_summary_agent.generate_summary(
                    name, social_media_analysis, pep_analysis, media_analysis
                )
                
                # Update state
                state["intelligence_summary"] = intelligence_summary
                
                return state
            except Exception as e:
                logger.error(f"Error generating intelligence summary: {str(e)}")
                if "errors" not in state:
                    state["errors"] = []
                state["errors"].append({
                    "step": "generate_intelligence_summary",
                    "error": str(e)
                })
                
                # Create a simple fallback summary
                fallback_summary = f"## Summary Report for {name}\n\n"
                
                social_media_analysis = state.get("social_media_analysis", "")
                pep_analysis = state.get("pep_analysis", "")
                media_analysis = state.get("media_analysis", "")
                
                if social_media_analysis and social_media_analysis != "No relevant social media profiles were found.":
                    fallback_summary += f"### Social Media\n{social_media_analysis}\n\n"
                
                if pep_analysis and pep_analysis != "No PEP (Politically Exposed Person) database matches were found.":
                    fallback_summary += f"### Political Exposure\n{pep_analysis}\n\n"
                
                if media_analysis and media_analysis != "No relevant media mentions were found.":
                    fallback_summary += f"### Media Coverage\n{media_analysis}\n\n"
                
                state["intelligence_summary"] = fallback_summary
                return state
        
        async def assess_risk(state: IntelligenceWorkflowState) -> IntelligenceWorkflowState:
            """Assess risk based on collected intelligence."""
            try:
                name = state["name"]
                social_media_analysis = state.get("social_media_analysis", "No relevant social media profiles were found.")
                pep_analysis = state.get("pep_analysis", "No PEP (Politically Exposed Person) database matches were found.")
                media_analysis = state.get("media_analysis", "No relevant media mentions were found.")
                
                # Assess risk
                risk_level, confidence_score, risk_justification = await self.risk_assessment_agent.assess_risk(
                    name, social_media_analysis, pep_analysis, media_analysis
                )
                
                # Update state
                state["risk_level"] = risk_level
                state["confidence_score"] = confidence_score
                state["risk_justification"] = risk_justification
                
                return state
            except Exception as e:
                logger.error(f"Error assessing risk: {str(e)}")
                if "errors" not in state:
                    state["errors"] = []
                state["errors"].append({
                    "step": "assess_risk",
                    "error": str(e)
                })
                state["risk_level"] = RiskLevel.UNKNOWN
                state["confidence_score"] = 0.0
                state["risk_justification"] = "Risk assessment could not be completed."
                return state
        
        async def create_result(state: IntelligenceWorkflowState) -> IntelligenceWorkflowState:
            """Create the final PersonIntelligence result."""
            try:
                # Create PersonIntelligence object
                result = PersonIntelligence(
                    name=state["name"],
                    social_media_profiles=state.get("social_media_profiles", {}),
                    pep_records=state.get("pep_records", []),
                    news_articles=state.get("news_articles", []),
                    summary=state.get("intelligence_summary", ""),
                    risk_level=state.get("risk_level", RiskLevel.UNKNOWN),
                    confidence_score=state.get("confidence_score", 0.0),
                    sources_checked=state.get("sources_checked", set()),
                    sources_successful=state.get("sources_successful", set()),
                    errors=state.get("errors", [])
                )
                
                # Update state
                state["result"] = result
                
                return state
            except Exception as e:
                logger.error(f"Error creating result: {str(e)}")
                if "errors" not in state:
                    state["errors"] = []
                state["errors"].append({
                    "step": "create_result",
                    "error": str(e)
                })
                
                # Create a minimal result
                result = PersonIntelligence(
                    name=state["name"],
                    summary=f"Error creating intelligence report: {str(e)}",
                    risk_level=RiskLevel.UNKNOWN
                )
                state["result"] = result
                return state
        
        # Build the graph
        workflow = StateGraph(IntelligenceWorkflowState)
        
        # Add nodes
        workflow.add_node("generate_search_strategy", generate_search_strategy)
        workflow.add_node("collect_data", collect_data)
        workflow.add_node("analyze_social_media", analyze_social_media)
        workflow.add_node("analyze_pep_data", analyze_pep_data)
        workflow.add_node("analyze_media_data", analyze_media_data)
        workflow.add_node("generate_intelligence_summary", generate_intelligence_summary)
        workflow.add_node("assess_risk", assess_risk)
        workflow.add_node("create_result", create_result)
        
        # Add edges - sequential workflow
        workflow.add_edge("generate_search_strategy", "collect_data")
        
        # Parallel analysis steps
        workflow.add_edge("collect_data", "analyze_social_media")
        workflow.add_edge("collect_data", "analyze_pep_data")
        workflow.add_edge("collect_data", "analyze_media_data")
        
        # Wait for all analysis to complete before summary
        def all_analysis_complete(state: IntelligenceWorkflowState) -> str:
            """Check if all analysis steps are complete."""
            # Move to summary when all three analysis steps are done
            social_media_done = "social_media_analysis" in state
            pep_done = "pep_analysis" in state
            media_done = "media_analysis" in state
            
            if social_media_done and pep_done and media_done:
                return "generate_intelligence_summary"
            
            # Wait for more analysis to complete
            return None
        
        workflow.add_conditional_edges(
            "analyze_social_media",
            all_analysis_complete,
            {
                "generate_intelligence_summary": "generate_intelligence_summary"
            }
        )
        
        workflow.add_conditional_edges(
            "analyze_pep_data",
            all_analysis_complete,
            {
                "generate_intelligence_summary": "generate_intelligence_summary"
            }
        )
        
        workflow.add_conditional_edges(
            "analyze_media_data",
            all_analysis_complete,
            {
                "generate_intelligence_summary": "generate_intelligence_summary"
            }
        )
        
        workflow.add_edge("generate_intelligence_summary", "assess_risk")
        workflow.add_edge("assess_risk", "create_result")
        workflow.add_edge("create_result", END)
        
        # Set entry point
        workflow.set_entry_point("generate_search_strategy")
        
        # Compile the graph
        return workflow.compile()
    
    async def run_intelligence_workflow(
        self,
        name: str,
        social_media_profiles: Optional[Dict[str, List[SocialMediaProfile]]] = None,
        pep_records: Optional[List[PEPRecord]] = None,
        news_articles: Optional[List[NewsArticle]] = None
    ) -> PersonIntelligence:
        """Run the complete intelligence workflow."""
        # Initialize state
        initial_state: IntelligenceWorkflowState = {
            "name": name,
            "search_strategy": None,
            "social_media_profiles": social_media_profiles or {},
            "pep_records": pep_records or [],
            "news_articles": news_articles or [],
            "social_media_analysis": None,
            "pep_analysis": None,
            "media_analysis": None,
            "intelligence_summary": None,
            "risk_level": None,
            "confidence_score": None,
            "risk_justification": None,
            "sources_checked": set(),
            "sources_successful": set(),
            "errors": [],
            "result": None
        }
        
        # Run the graph
        result = await self.graph.ainvoke(initial_state)
        
        # Return the created PersonIntelligence object
        return result.get("result", PersonIntelligence(name=name, risk_level=RiskLevel.UNKNOWN))