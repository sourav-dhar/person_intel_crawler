"""
Analysis agents using LangGraph framework.
"""

import logging
from typing import Dict, List, Any, TypedDict, Optional, cast, Tuple

from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END

from models.pep_models import PEPRecord
from models.social_media_models import SocialMediaProfile
from models.media_models import NewsArticle
from models.base_models import RiskLevel
from agents.agent_prompts import (
    PEP_ANALYSIS_PROMPT,
    SOCIAL_MEDIA_ANALYSIS_PROMPT,
    MEDIA_ANALYSIS_PROMPT,
    INTELLIGENCE_SUMMARY_PROMPT,
    RISK_ASSESSMENT_PROMPT
)
from agents.agent_tools import (
    RiskAssessmentTools,
    EntityExtractionTools,
    SourceAssessmentTools
)

logger = logging.getLogger(__name__)

# Define the state for the PEP analysis graph
class PEPAnalysisState(TypedDict):
    name: str
    pep_records: List[PEPRecord]
    pep_results_str: Optional[str]
    pep_analysis: Optional[str]
    errors: Optional[List[Dict[str, Any]]]

# Define the state for the social media analysis graph
class SocialMediaAnalysisState(TypedDict):
    name: str
    social_media_profiles: Dict[str, List[SocialMediaProfile]]
    social_media_results_str: Optional[str]
    social_media_analysis: Optional[str]
    errors: Optional[List[Dict[str, Any]]]

# Define the state for the media analysis graph
class MediaAnalysisState(TypedDict):
    name: str
    news_articles: List[NewsArticle]
    media_results_str: Optional[str]
    media_analysis: Optional[str]
    errors: Optional[List[Dict[str, Any]]]

# Define the state for the intelligence summary graph
class IntelligenceSummaryState(TypedDict):
    name: str
    social_media_summary: str
    pep_summary: str
    media_summary: str
    intelligence_summary: Optional[str]
    errors: Optional[List[Dict[str, Any]]]

# Define the state for the risk assessment graph
class RiskAssessmentState(TypedDict):
    name: str
    social_media_summary: str
    pep_summary: str
    media_summary: str
    risk_assessment: Optional[str]
    risk_level: Optional[RiskLevel]
    confidence_score: Optional[float]
    risk_justification: Optional[str]
    errors: Optional[List[Dict[str, Any]]]


class PEPAnalysisAgent:
    """Agent for analyzing PEP data."""
    
    def __init__(self, model_name: str = "gpt-4-turbo", temperature: float = 0.2):
        """Initialize the PEP analysis agent."""
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)
        self.prompt = ChatPromptTemplate.from_template(PEP_ANALYSIS_PROMPT)
        self.output_parser = StrOutputParser()
        
        # Create and compile the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph for PEP analysis."""
        # Define the nodes
        def format_pep_records(state: PEPAnalysisState) -> PEPAnalysisState:
            """Format PEP records for analysis."""
            try:
                name = state["name"]
                pep_records = state["pep_records"]
                
                # Format PEP records as text
                pep_results_str = "\n\n".join([
                    f"Source: {record.source}\n"
                    f"Name: {record.name}\n"
                    f"Position: {record.position or 'Not specified'}\n"
                    f"Organization: {record.organization or 'Not specified'}\n"
                    f"Country: {record.country or 'Not specified'}\n"
                    f"Sanctions: {', '.join([s.get('name', 'Unknown') for s in record.sanctions]) if record.sanctions else 'None'}\n"
                    f"Watchlists: {', '.join(record.watchlists) if record.watchlists else 'None'}\n"
                    f"URL: {record.url or 'Not available'}\n"
                    f"Match Score: {record.similarity_score:.2f}"
                    for record in pep_records
                ])
                
                # Update state
                state["pep_results_str"] = pep_results_str
                
                return state
            except Exception as e:
                logger.error(f"Error formatting PEP records: {str(e)}")
                if "errors" not in state:
                    state["errors"] = []
                state["errors"].append({
                    "step": "format_pep_records",
                    "error": str(e)
                })
                return state
        
        def analyze_pep_data(state: PEPAnalysisState) -> PEPAnalysisState:
            """Analyze PEP data."""
            try:
                name = state["name"]
                pep_results_str = state.get("pep_results_str", "No PEP data available.")
                
                if not pep_results_str or pep_results_str == "No PEP data available.":
                    state["pep_analysis"] = "No PEP (Politically Exposed Person) database matches were found."
                    return state
                
                # Create the prompt
                chain = self.prompt | self.llm | self.output_parser
                
                # Generate analysis
                pep_analysis = chain.invoke({
                    "name": name,
                    "pep_results": pep_results_str
                })
                
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
                state["pep_analysis"] = f"Error analyzing PEP data: {str(e)}"
                return state
        
        # Build the graph
        workflow = StateGraph(PEPAnalysisState)
        
        # Add nodes
        workflow.add_node("format_pep_records", format_pep_records)
        workflow.add_node("analyze_pep_data", analyze_pep_data)
        
        # Add edges
        workflow.add_edge("format_pep_records", "analyze_pep_data")
        workflow.add_edge("analyze_pep_data", END)
        
        # Set entry point
        workflow.set_entry_point("format_pep_records")
        
        # Compile the graph
        return workflow.compile()
    
    async def analyze_pep_data(self, name: str, pep_records: List[PEPRecord]) -> str:
        """Analyze PEP records for a person."""
        # Initialize state
        initial_state: PEPAnalysisState = {
            "name": name,
            "pep_records": pep_records,
            "pep_results_str": None,
            "pep_analysis": None,
            "errors": None
        }
        
        # Run the graph
        result = await self.graph.ainvoke(initial_state)
        
        # Return the analysis
        return result.get("pep_analysis", "No PEP analysis available.")


class SocialMediaAnalysisAgent:
    """Agent for analyzing social media data."""
    
    def __init__(self, model_name: str = "gpt-4-turbo", temperature: float = 0.2):
        """Initialize the social media analysis agent."""
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)
        self.prompt = ChatPromptTemplate.from_template(SOCIAL_MEDIA_ANALYSIS_PROMPT)
        self.output_parser = StrOutputParser()
        
        # Create and compile the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph for social media analysis."""
        # Define the nodes
        def format_social_media_profiles(state: SocialMediaAnalysisState) -> SocialMediaAnalysisState:
            """Format social media profiles for analysis."""
            try:
                name = state["name"]
                profiles = state["social_media_profiles"]
                
                # Format profiles as text
                platform_profiles = []
                
                for platform, platform_profiles in profiles.items():
                    for profile in platform_profiles:
                        profile_text = f"Platform: {platform}\n" \
                                     f"Username: {profile.username}\n" \
                                     f"Display Name: {profile.display_name or 'Not available'}\n" \
                                     f"URL: {profile.url or 'Not available'}\n" \
                                     f"Bio: {profile.bio or 'Not available'}\n" \
                                     f"Followers: {profile.follower_count or 'Unknown'}\n" \
                                     f"Location: {profile.location or 'Not specified'}\n" \
                                     f"Verified: {'Yes' if profile.is_verified else 'No'}\n" \
                                     f"Relevance Score: {profile.relevance_score:.2f}"
                        
                        # Add recent posts if available
                        if profile.posts:
                            post_samples = [f"- {post.get('text', '')[:100]}..." for post in profile.posts[:3]]
                            profile_text += f"\n\nRecent posts:\n" + "\n".join(post_samples)
                        
                        platform_profiles.append(profile_text)
                
                social_media_results_str = "\n\n".join(platform_profiles)
                
                # Update state
                state["social_media_results_str"] = social_media_results_str if platform_profiles else "No social media profiles found."
                
                return state
            except Exception as e:
                logger.error(f"Error formatting social media profiles: {str(e)}")
                if "errors" not in state:
                    state["errors"] = []
                state["errors"].append({
                    "step": "format_social_media_profiles",
                    "error": str(e)
                })
                return state
        
        def analyze_social_media_data(state: SocialMediaAnalysisState) -> SocialMediaAnalysisState:
            """Analyze social media data."""
            try:
                name = state["name"]
                social_media_results_str = state.get("social_media_results_str", "No social media profiles found.")
                
                if not social_media_results_str or social_media_results_str == "No social media profiles found.":
                    state["social_media_analysis"] = "No relevant social media profiles were found."
                    return state
                
                # Create the prompt
                chain = self.prompt | self.llm | self.output_parser
                
                # Generate analysis
                social_media_analysis = chain.invoke({
                    "name": name,
                    "social_media_results": social_media_results_str
                })
                
                # Update state
                state["social_media_analysis"] = social_media_analysis
                
                return state
            except Exception as e:
                logger.error(f"Error analyzing social media data: {str(e)}")
                if "errors" not in state:
                    state["errors"] = []
                state["errors"].append({
                    "step": "analyze_social_media_data",
                    "error": str(e)
                })
                state["social_media_analysis"] = f"Error analyzing social media data: {str(e)}"
                return state
        
        # Build the graph
        workflow = StateGraph(SocialMediaAnalysisState)
        
        # Add nodes
        workflow.add_node("format_social_media_profiles", format_social_media_profiles)
        workflow.add_node("analyze_social_media_data", analyze_social_media_data)
        
        # Add edges
        workflow.add_edge("format_social_media_profiles", "analyze_social_media_data")
        workflow.add_edge("analyze_social_media_data", END)
        
        # Set entry point
        workflow.set_entry_point("format_social_media_profiles")
        
        # Compile the graph
        return workflow.compile()
    
    async def analyze_social_media_data(self, name: str, profiles: Dict[str, List[SocialMediaProfile]]) -> str:
        """Analyze social media profiles for a person."""
        # Initialize state
        initial_state: SocialMediaAnalysisState = {
            "name": name,
            "social_media_profiles": profiles,
            "social_media_results_str": None,
            "social_media_analysis": None,
            "errors": None
        }
        
        # Run the graph
        result = await self.graph.ainvoke(initial_state)
        
        # Return the analysis
        return result.get("social_media_analysis", "No social media analysis available.")


class MediaAnalysisAgent:
    """Agent for analyzing adverse media data."""
    
    def __init__(self, model_name: str = "gpt-4-turbo", temperature: float = 0.2):
        """Initialize the media analysis agent."""
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)
        self.prompt = ChatPromptTemplate.from_template(MEDIA_ANALYSIS_PROMPT)
        self.output_parser = StrOutputParser()
        
        # Create and compile the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph for media analysis."""
        # Define the nodes
        def format_news_articles(state: MediaAnalysisState) -> MediaAnalysisState:
            """Format news articles for analysis."""
            try:
                name = state["name"]
                articles = state["news_articles"]
                
                # Format articles as text
                media_results = "\n\n".join([
                    f"Source: {article.source}\n"
                    f"Title: {article.title}\n"
                    f"Date: {article.published_date.strftime('%Y-%m-%d') if article.published_date else 'Unknown'}\n"
                    f"URL: {article.url}\n"
                    f"Sentiment: {article.sentiment.value if article.sentiment else 'Not analyzed'}\n"
                    f"Relevance: {article.relevance_score:.2f}\n"
                    f"Summary: {article.summary or article.content[:200] + '...' if article.content and len(article.content) > 200 else article.content or 'No content available'}"
                    for article in articles
                ])
                
                # Update state
                state["media_results_str"] = media_results if media_results else "No media articles found."
                
                return state
            except Exception as e:
                logger.error(f"Error formatting news articles: {str(e)}")
                if "errors" not in state:
                    state["errors"] = []
                state["errors"].append({
                    "step": "format_news_articles",
                    "error": str(e)
                })
                return state
        
        def analyze_media_data(state: MediaAnalysisState) -> MediaAnalysisState:
            """Analyze media data."""
            try:
                name = state["name"]
                media_results_str = state.get("media_results_str", "No media articles found.")
                
                if not media_results_str or media_results_str == "No media articles found.":
                    state["media_analysis"] = "No relevant media mentions were found."
                    return state
                
                # Create the prompt
                chain = self.prompt | self.llm | self.output_parser
                
                # Generate analysis
                media_analysis = chain.invoke({
                    "name": name,
                    "media_results": media_results_str
                })
                
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
                state["media_analysis"] = f"Error analyzing media data: {str(e)}"
                return state
        
        # Build the graph
        workflow = StateGraph(MediaAnalysisState)
        
        # Add nodes
        workflow.add_node("format_news_articles", format_news_articles)
        workflow.add_node("analyze_media_data", analyze_media_data)
        
        # Add edges
        workflow.add_edge("format_news_articles", "analyze_media_data")
        workflow.add_edge("analyze_media_data", END)
        
        # Set entry point
        workflow.set_entry_point("format_news_articles")
        
        # Compile the graph
        return workflow.compile()
    
    async def analyze_media_data(self, name: str, news_articles: List[NewsArticle]) -> str:
        """Analyze news articles for a person."""
        # Initialize state
        initial_state: MediaAnalysisState = {
            "name": name,
            "news_articles": news_articles,
            "media_results_str": None,
            "media_analysis": None,
            "errors": None
        }
        
        # Run the graph
        result = await self.graph.ainvoke(initial_state)
        
        # Return the analysis
        return result.get("media_analysis", "No media analysis available.")


class IntelligenceSummaryAgent:
    """Agent for generating a comprehensive intelligence summary."""
    
    def __init__(self, model_name: str = "gpt-4-turbo", temperature: float = 0.2):
        """Initialize the intelligence summary agent."""
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)
        self.prompt = ChatPromptTemplate.from_template(INTELLIGENCE_SUMMARY_PROMPT)
        self.output_parser = StrOutputParser()
        
        # Create and compile the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph for intelligence summary generation."""
        # Define the nodes
        def generate_summary(state: IntelligenceSummaryState) -> IntelligenceSummaryState:
            """Generate a comprehensive intelligence summary."""
            try:
                name = state["name"]
                social_media_summary = state["social_media_summary"]
                pep_summary = state["pep_summary"]
                media_summary = state["media_summary"]
                
                # Create the prompt
                chain = self.prompt | self.llm | self.output_parser
                
                # Generate summary
                intelligence_summary = chain.invoke({
                    "name": name,
                    "social_media_summary": social_media_summary,
                    "pep_summary": pep_summary,
                    "media_summary": media_summary
                })
                
                # Update state
                state["intelligence_summary"] = intelligence_summary
                
                return state
            except Exception as e:
                logger.error(f"Error generating intelligence summary: {str(e)}")
                if "errors" not in state:
                    state["errors"] = []
                state["errors"].append({
                    "step": "generate_summary",
                    "error": str(e)
                })
                
                # Create a simple fallback summary
                fallback_summary = f"## Summary Report for {name}\n\n"
                
                if social_media_summary and social_media_summary != "No relevant social media profiles were found.":
                    fallback_summary += f"### Social Media\n{social_media_summary}\n\n"
                
                if pep_summary and pep_summary != "No PEP (Politically Exposed Person) database matches were found.":
                    fallback_summary += f"### Political Exposure\n{pep_summary}\n\n"
                
                if media_summary and media_summary != "No relevant media mentions were found.":
                    fallback_summary += f"### Media Coverage\n{media_summary}\n\n"
                
                state["intelligence_summary"] = fallback_summary
                return state
        
        # Build the graph
        workflow = StateGraph(IntelligenceSummaryState)
        
        # Add nodes
        workflow.add_node("generate_summary", generate_summary)
        
        # Add edges
        workflow.add_edge("generate_summary", END)
        
        # Set entry point
        workflow.set_entry_point("generate_summary")
        
        # Compile the graph
        return workflow.compile()
    
    async def generate_summary(self, name: str, social_media_summary: str, 
                           pep_summary: str, media_summary: str) -> str:
        """Generate a comprehensive intelligence summary."""
        # Initialize state
        initial_state: IntelligenceSummaryState = {
            "name": name,
            "social_media_summary": social_media_summary,
            "pep_summary": pep_summary,
            "media_summary": media_summary,
            "intelligence_summary": None,
            "errors": None
        }
        
        # Run the graph
        result = await self.graph.ainvoke(initial_state)
        
        # Return the summary
        return result.get("intelligence_summary", "No intelligence summary available.")


class RiskAssessmentAgent:
    """Agent for assessing risk based on collected intelligence."""
    
    def __init__(self, model_name: str = "gpt-4-turbo", temperature: float = 0.2):
        """Initialize the risk assessment agent."""
        self.tools = RiskAssessmentTools()
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)
        self.prompt = ChatPromptTemplate.from_template(RISK_ASSESSMENT_PROMPT)
        self.output_parser = StrOutputParser()
        
        # Create and compile the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph for risk assessment."""
        # Define the nodes
        def generate_risk_assessment(state: RiskAssessmentState) -> RiskAssessmentState:
            """Generate a risk assessment."""
            try:
                name = state["name"]
                social_media_summary = state["social_media_summary"]
                pep_summary = state["pep_summary"]
                media_summary = state["media_summary"]
                
                # Create the prompt
                chain = self.prompt | self.llm | self.output_parser
                
                # Generate risk assessment
                risk_assessment = chain.invoke({
                    "name": name,
                    "social_media_summary": social_media_summary,
                    "pep_summary": pep_summary,
                    "media_summary": media_summary
                })
                
                # Update state
                state["risk_assessment"] = risk_assessment
                
                return state
            except Exception as e:
                logger.error(f"Error generating risk assessment: {str(e)}")
                if "errors" not in state:
                    state["errors"] = []
                state["errors"].append({
                    "step": "generate_risk_assessment",
                    "error": str(e)
                })
                state["risk_assessment"] = f"Error generating risk assessment: {str(e)}"
                return state
        
        def extract_risk_components(state: RiskAssessmentState) -> RiskAssessmentState:
            """Extract risk level, confidence, and justification from the assessment."""
            try:
                risk_assessment = state.get("risk_assessment", "")
                if not risk_assessment:
                    state["risk_level"] = RiskLevel.UNKNOWN
                    state["confidence_score"] = 0.0
                    state["risk_justification"] = "No risk assessment available."
                    return state
                
                # Extract components
                risk_level, confidence_score, risk_justification = self.tools.extract_risk_level(risk_assessment)
                
                # Update state
                state["risk_level"] = risk_level
                state["confidence_score"] = confidence_score
                state["risk_justification"] = risk_justification
                
                return state
            except Exception as e:
                logger.error(f"Error extracting risk components: {str(e)}")
                if "errors" not in state:
                    state["errors"] = []
                state["errors"].append({
                    "step": "extract_risk_components",
                    "error": str(e)
                })
                state["risk_level"] = RiskLevel.UNKNOWN
                state["confidence_score"] = 0.0
                state["risk_justification"] = f"Error extracting risk components: {str(e)}"
                return state
        
        # Build the graph
        workflow = StateGraph(RiskAssessmentState)
        
        # Add nodes
        workflow.add_node("generate_risk_assessment", generate_risk_assessment)
        workflow.add_node("extract_risk_components", extract_risk_components)
        
        # Add edges
        workflow.add_edge("generate_risk_assessment", "extract_risk_components")
        workflow.add_edge("extract_risk_components", END)
        
        # Set entry point
        workflow.set_entry_point("generate_risk_assessment")
        
        # Compile the graph
        return workflow.compile()
    
    async def assess_risk(self, name: str, social_media_summary: str, 
                       pep_summary: str, media_summary: str) -> Tuple[RiskLevel, float, str]:
        """Assess risk based on collected intelligence."""
        # Initialize state
        initial_state: RiskAssessmentState = {
            "name": name,
            "social_media_summary": social_media_summary,
            "pep_summary": pep_summary,
            "media_summary": media_summary,
            "risk_assessment": None,
            "risk_level": None,
            "confidence_score": None,
            "risk_justification": None,
            "errors": None
        }
        
        # Run the graph
        result = await self.graph.ainvoke(initial_state)
        
        # Return the risk assessment components
        return (
            result.get("risk_level", RiskLevel.UNKNOWN),
            result.get("confidence_score", 0.0),
            result.get("risk_justification", "No risk assessment available.")
        )