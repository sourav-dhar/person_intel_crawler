# LLM configuration
"""
Configuration models for LLM-based agents.
"""

from typing import Dict, Any
from pydantic import BaseModel, Field, validator

class PromptConfig(BaseModel):
    """Configuration for LLM prompts."""
    system_message: str
    search_strategy_prompt: str
    pep_analysis_prompt: str
    media_analysis_prompt: str
    social_media_analysis_prompt: str
    summary_prompt: str
    risk_assessment_prompt: str
    
    temperature_by_task: Dict[str, float] = Field(
        default_factory=lambda: {
            "search_strategy": 0.3,
            "pep_analysis": 0.1,
            "media_analysis": 0.2,
            "social_media_analysis": 0.2,
            "summary": 0.2,
            "risk_assessment": 0.1
        }
    )
    
    max_tokens_by_task: Dict[str, int] = Field(
        default_factory=lambda: {
            "search_strategy": 1000,
            "pep_analysis": 2000,
            "media_analysis": 2000,
            "social_media_analysis": 2000,
            "summary": 3000,
            "risk_assessment": 2000
        }
    )


class LLMConfig(BaseModel):
    """Configuration for the LLM agent."""
    model_name: str = "gpt-4-turbo"
    temperature: float = Field(default=0.2, ge=0.0, le=1.0)
    max_tokens: int = Field(default=4000, ge=1, le=16000)
    prompts: PromptConfig = Field(...)
    tools_config: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('prompts', pre=True)
    def set_default_prompts(cls, v):
        if isinstance(v, PromptConfig):
            return v
            
        # Default system prompts
        return PromptConfig(
            system_message="""
            You are an investigative assistant tasked with gathering and analyzing information about a person.
            Your goal is to find relevant information across social media, PEP databases, and news sources.
            Focus on factual information and avoid speculation. Maintain privacy and ethical standards.
            For each finding, cite the source clearly.
            """,
            
            search_strategy_prompt="""
            Based on the name {name}, create a search strategy to gather information.
            1. What social media platforms might be most relevant for someone with this name?
            2. What specific search terms should be used for optimal results?
            3. Are there any alternative spellings or variations of this name to consider?
            4. What geographical regions would be most relevant to check?
            5. What time period would be most relevant for adverse media searches?
            
            Output your response as a structured search plan.
            """,
            
            pep_analysis_prompt="""
            Analyze the following PEP (Politically Exposed Person) database results for {name}:
            
            {pep_results}
            
            1. Identify any matches that appear to be the same individual
            2. Assess the credibility and significance of each match
            3. Note any sanctions, watchlists, or investigations mentioned
            4. Summarize the political exposure level and associated territories
            5. Highlight any red flags or concerning issues
            
            Provide a concise analysis of the PEP status and associated risks.
            """,
            
            media_analysis_prompt="""
            Analyze the following adverse media results for {name}:
            
            {media_results}
            
            1. Identify the key allegations or issues mentioned
            2. Assess the credibility of each source
            3. Note the timeframe of the mentions
            4. Determine if the mentions are related to the same individual
            5. Evaluate the severity of the issues mentioned
            
            Provide a concise summary of adverse media findings and their significance.
            """,
            
            social_media_analysis_prompt="""
            Analyze the following social media results for {name}:
            
            {social_media_results}
            
            1. Assess which profiles likely belong to the same individual
            2. Note key biographical information found
            3. Identify any professional roles, affiliations, or connections
            4. Evaluate the public image and online presence
            5. Highlight any potential concerns or red flags
            
            Provide a concise summary of the social media presence and key insights.
            """,
            
            summary_prompt="""
            Create a comprehensive summary report for {name} based on all collected information:
            
            Social Media Analysis:
            {social_media_summary}
            
            PEP Database Analysis:
            {pep_summary}
            
            Adverse Media Analysis:
            {media_summary}
            
            Provide a clear, concise summary that:
            1. Identifies confirmed facts about the individual
            2. Notes potential areas of concern or risk
            3. Highlights missing or conflicting information
            4. Ranks the confidence level of the findings
            5. Suggests any additional research that might be valuable
            
            The summary should be objective, evidence-based, and cite sources.
            """,
            
            risk_assessment_prompt="""
            Based on all collected information about {name}, assess the overall risk level.
            
            Social Media Information:
            {social_media_summary}
            
            PEP Database Information:
            {pep_summary}
            
            Adverse Media Information:
            {media_summary}
            
            Determine a risk level (Low, Medium, High, Critical) and provide a justification.
            Consider factors such as:
            1. Political exposure and position
            2. Regulatory or legal issues
            3. Financial crimes or misconduct allegations
            4. Sanctions or watchlist presence
            5. Negative media coverage and its severity
            6. Associations with other high-risk individuals or entities
            
            Format your response as:
            
            Risk Level: [Level]
            Confidence: [0-100%]
            
            [Detailed justification with specific evidence]
            """
        )