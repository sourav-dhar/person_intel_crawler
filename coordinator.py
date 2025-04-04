# Main crawler coordinator
"""
Main coordinator for the Person Intelligence Crawler.

This module orchestrates the entire workflow, including configuration loading,
crawler initialization, data collection, analysis, and result handling.
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

from config.base_config import CrawlerConfig, CacheConfig, RateLimitConfig, ProxyConfig
from config.social_media_config import SocialMediaConfig
from config.pep_config import PEPDatabaseConfig
from config.media_config import AdverseMediaConfig
from config.llm_config import LLMConfig, PromptConfig

from models.intelligence_models import PersonIntelligence
from models.base_models import RiskLevel, SourceType
from models.social_media_models import SocialMediaProfile
from models.pep_models import PEPRecord
from models.media_models import NewsArticle

from crawlers.social_media_crawler import SocialMediaCrawler
from crawlers.pep_database_crawler import PEPDatabaseCrawler
from crawlers.adverse_media_crawler import AdverseMediaCrawler

from agents.langraph_coordinator import LangGraphCoordinator

logger = logging.getLogger(__name__)

class PersonIntelCrawler:
    """Main coordinator for the Person Intelligence Crawler framework."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the crawler with configuration."""
        self.config = self._load_config(config_path)
        
        # Initialize component crawlers
        self.social_media_crawler = SocialMediaCrawler(
            self.config.social_media, 
            self.config
        )
        
        self.pep_database_crawler = PEPDatabaseCrawler(
            self.config.pep_database, 
            self.config
        )
        
        self.adverse_media_crawler = AdverseMediaCrawler(
            self.config.adverse_media, 
            self.config
        )
        
        # Initialize LangGraph coordinator
        self.langraph_coordinator = LangGraphCoordinator(self.config.llm)
    
    def _load_config(self, config_path: Optional[str]) -> CrawlerConfig:
        """Load configuration from a file or use defaults."""
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                
                return CrawlerConfig(**config_data)
            except Exception as e:
                logger.error(f"Error loading configuration from {config_path}: {str(e)}")
                logger.info("Using default configuration")
        
        # Create default LLM config with prompts
        llm_config = LLMConfig(
            model_name="gpt-4-turbo",
            temperature=0.2,
            max_tokens=4000,
            prompts=PromptConfig(
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
        )
        
        # Create default configuration
        return CrawlerConfig(
            social_media=SocialMediaConfig(),
            pep_database=PEPDatabaseConfig(),
            adverse_media=AdverseMediaConfig(),
            llm=llm_config,
            api_keys={}
        )
    
    async def search(self, name: str) -> PersonIntelligence:
        """Search for information about a person across all sources."""
        logger.info(f"Starting search for: {name}")
        
        # Initialize result container
        result = PersonIntelligence(name=name)
        
        try:
            # Step 1: Generate search strategy using LangGraph
            strategy = await self.langraph_coordinator.run_intelligence_workflow(name)
            # The strategy would normally be used to guide the crawlers
            # Fully implementing this would require integrating the strategy into the crawlers
            logger.info(f"Search strategy created for: {name}")
            
            # Step 2: Execute searches in parallel
            social_media_task = asyncio.create_task(
                self.social_media_crawler.search(name)
            )
            
            pep_database_task = asyncio.create_task(
                self.pep_database_crawler.search(name)
            )
            
            adverse_media_task = asyncio.create_task(
                self.adverse_media_crawler.search(name)
            )
            
            # Wait for all searches to complete
            social_media_profiles = await social_media_task
            pep_records = await pep_database_task
            news_articles = await adverse_media_task
            
            # Run the full LangGraph workflow with the collected data
            result = await self.langraph_coordinator.run_intelligence_workflow(
                name, 
                social_media_profiles, 
                pep_records, 
                news_articles
            )
            
        except Exception as e:
            logger.error(f"Error during search for {name}: {str(e)}")
            result.errors.append({
                "source": "main",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            })
        
        logger.info(f"Search completed for: {name}")
        return result
    
    def search_sync(self, name: str) -> PersonIntelligence:
        """Synchronous version of the search method."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.search(name))
        finally:
            loop.close()
    
    async def save_results(self, result: PersonIntelligence, output_path: str) -> None:
        """Save search results to a file."""
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        
        # Determine output format
        if self.config.output_format == "json":
            with open(output_path, 'w') as f:
                f.write(result.to_json())
        elif self.config.output_format == "markdown":
            with open(output_path, 'w') as f:
                f.write(result.to_markdown())
        else:
            # Default to JSON
            with open(output_path, 'w') as f:
                f.write(result.to_json())
        
        logger.info(f"Results saved to: {output_path}")
    
    def save_results_sync(self, result: PersonIntelligence, output_path: str) -> None:
        """Synchronous version of the save_results method."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.save_results(result, output_path))
        finally:
            loop.close()