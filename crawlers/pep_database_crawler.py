# PEP database crawler
"""
Usage examples for the Person Intelligence Crawler.

These examples demonstrate how to use the framework in different scenarios:
1. Basic usage with default configuration
2. Custom configuration
3. API integration
4. Handling edge cases
5. Extended analysis
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional

from coordinator import PersonIntelCrawler
from config.base_config import CrawlerConfig, CacheConfig, RateLimitConfig, ProxyConfig
from config.social_media_config import SocialMediaConfig, PlatformConfig
from config.pep_config import PEPDatabaseConfig, PEPSourceConfig
from config.media_config import AdverseMediaConfig, NewsSourceConfig
from config.llm_config import LLMConfig, PromptConfig
from models.base_models import RiskLevel
from models.intelligence_models import PersonIntelligence

# Example 5: Error handling
async def example_error_handling():
    """Example of handling errors in the search process."""
    # Create crawler
    crawler = PersonIntelCrawler()
    
    # 1. Handle API key errors
    try:
        # Intentionally use invalid API key
        os.environ["OPENAI_API_KEY"] = "invalid_key"
        result = await crawler.search("Error Test")
        
    except Exception as e:
        print(f"\nCaught exception during search: {e}")
    
    # 2. Check for errors in results
    os.environ["OPENAI_API_KEY"] = "your_valid_key_here"  # Reset to valid key
    result = await crawler.search("Partial Error Test")
    
    if result.errors:
        print(f"\nEncountered {len(result.errors)} errors during search:")
        for error in result.errors:
            print(f"  - Source: {error.get('source')}")
            print(f"    Message: {error.get('message')}")
            print(f"    Timestamp: {error.get('timestamp')}")
    
    # 3. Check sources that were checked vs. successful
    print(f"\nSources checked: {len(result.sources_checked)}")
    print(f"Sources successful: {len(result.sources_successful)}")
    failed_sources = result.sources_checked - result.sources_successful
    if failed_sources:
        print(f"Failed sources: {failed_sources}")


# Example 6: Batch processing
async def example_batch_processing():
    """Example of processing multiple names in batch."""
    # Create crawler
    crawler = PersonIntelCrawler()
    
    # List of names to search
    names = ["John Smith", "Jane Doe", "Michael Johnson"]
    
    print("\nStarting batch processing example...")
    results = []
    
    # Process each name
    for name in names:
        print(f"Searching for: {name}")
        try:
            result = await crawler.search(name)
            results.append(result)
            print(f"  Risk Level: {result.risk_level.value.upper()}")
            print(f"  Confidence: {result.confidence_score:.2f}")
        except Exception as e:
            print(f"  Error processing {name}: {e}")
    
    # Generate summary of batch results
    print("\nBatch Processing Summary:")
    print(f"Total processed: {len(results)}")
    
    risk_levels = {}
    for result in results:
        level = result.risk_level.value
        risk_levels[level] = risk_levels.get(level, 0) + 1
    
    print("Risk level distribution:")
    for level, count in risk_levels.items():
        print(f"  {level.upper()}: {count}")


# Example 7: Custom output formatting
async def example_custom_output():
    """Example of custom output formatting."""
    # Create crawler
    crawler = PersonIntelCrawler()
    
    # Search for a person
    print("\nStarting custom output example...")
    result = await crawler.search("Custom Output Test")
    
    # 1. JSON output (default)
    json_output = result.to_json()
    
    # 2. Markdown output
    markdown_output = result.to_markdown()
    
    # 3. Custom CSV output
    def to_csv(result):
        """Convert basic result info to CSV."""
        header = "Name,Risk Level,Confidence,Sources Checked,PEP Records,News Articles\n"
        row = f"{result.name},{result.risk_level.value},{result.confidence_score:.2f},"
        row += f"{len(result.sources_checked)},{len(result.pep_records)},{len(result.news_articles)}\n"
        return header + row
    
    csv_output = to_csv(result)
    
    # 4. Custom HTML output
    def to_html(result):
        """Convert result to simple HTML."""
        html = f"<html><head><title>Report: {result.name}</title></head><body>\n"
        html += f"<h1>Intelligence Report: {result.name}</h1>\n"
        html += f"<p><strong>Risk Level:</strong> {result.risk_level.value.upper()}</p>\n"
        html += f"<p><strong>Confidence:</strong> {result.confidence_score:.2f}</p>\n"
        html += f"<h2>Summary</h2>\n<p>{result.summary}</p>\n"
        html += "</body></html>"
        return html
    
    html_output = to_html(result)
    
    # Save all formats
    os.makedirs("examples", exist_ok=True)
    with open("examples/output.json", "w") as f:
        f.write(json_output)
    with open("examples/output.md", "w") as f:
        f.write(markdown_output)
    with open("examples/output.csv", "w") as f:
        f.write(csv_output)
    with open("examples/output.html", "w") as f:
        f.write(html_output)
    
    print("Saved outputs in multiple formats to the examples directory")


# Run all examples
async def run_all_examples():
    """Run all examples."""
    try:
        await example_basic_usage()
        await example_custom_configuration()
        await example_save_load_configuration()
        await example_processing_results()
        await example_error_handling()
        await example_batch_processing()
        await example_custom_output()
    except Exception as e:
        print(f"Error running examples: {e}")


if __name__ == "__main__":
    # Check for OpenAI API key
    if "OPENAI_API_KEY" not in os.environ:
        print("Warning: OPENAI_API_KEY environment variable not set.")
        print("Examples will use a placeholder value and may not work correctly.")
        print("Set this environment variable before running the examples.")
        print("Example: export OPENAI_API_KEY=your_api_key_here")
        
    # Create examples directory
    os.makedirs("examples", exist_ok=True)
    
    # Run examples
    asyncio.run(run_all_examples()) 1: Basic usage with default configuration
async def example_basic_usage():
    """Basic usage example with default configuration."""
    # Create crawler with default configuration
    crawler = PersonIntelCrawler()
    
    # Set API key (normally would be in .env file)
    os.environ["OPENAI_API_KEY"] = "your_openai_api_key_here"
    
    # Search for a person
    print("Starting basic search...")
    result = await crawler.search("John Smith")
    
    # Print summary
    print(f"\nSearch completed for: {result.name}")
    print(f"Risk Level: {result.risk_level.value.upper()}")
    print(f"Confidence Score: {result.confidence_score:.2f}")
    print(f"Sources Checked: {len(result.sources_checked)}")
    
    # Save results
    await crawler.save_results(result, "examples/john_smith_results.json")
    print(f"Results saved to: examples/john_smith_results.json")


# Example 2: Custom configuration
async def example_custom_configuration():
    """Example with custom configuration."""
    # Create custom configuration
    social_media_config = SocialMediaConfig(
        platforms=[
            PlatformConfig(
                name="twitter",
                search_url_template="https://twitter.com/search?q={query}&f=user",
                profile_url_template="https://twitter.com/{username}",
                search_depth=3,
                max_posts=100
            ),
            PlatformConfig(
                name="linkedin",
                search_url_template="https://www.linkedin.com/search/results/people/?keywords={query}",
                profile_url_template="https://www.linkedin.com/in/{username}",
                search_depth=2,
                max_posts=50
            )
        ],
        timeout_per_platform=45
    )
    
    pep_database_config = PEPDatabaseConfig(
        sources=[
            PEPSourceConfig(
                name="opensanctions",
                api_url="https://api.opensanctions.org",
                search_endpoint="/search/person",
                requires_auth=True
            )
        ],
        similarity_threshold=0.75
    )
    
    adverse_media_config = AdverseMediaConfig(
        sources=[
            NewsSourceConfig(
                name="google_news",
                web_search_template="https://news.google.com/search?q={query}",
                requires_auth=False
            )
        ],
        timeframe_days=730,  # 2 years
        max_results_per_source=100
    )
    
    llm_config = LLMConfig(
        model_name="gpt-4-turbo",
        temperature=0.1,
        max_tokens=8000,
        prompts=PromptConfig(
            system_message="Custom system message...",
            search_strategy_prompt="Custom search strategy prompt...",
            pep_analysis_prompt="Custom PEP analysis prompt...",
            media_analysis_prompt="Custom media analysis prompt...",
            social_media_analysis_prompt="Custom social media analysis prompt...",
            summary_prompt="Custom summary prompt...",
            risk_assessment_prompt="Custom risk assessment prompt..."
        )
    )
    
    # Create overall configuration
    config = CrawlerConfig(
        social_media=social_media_config,
        pep_database=pep_database_config,
        adverse_media=adverse_media_config,
        llm=llm_config,
        max_concurrent_requests=20,
        request_delay=0.3,
        cache=CacheConfig(
            enabled=True,
            ttl=3600,  # 1 hour
            cache_dir=".custom_cache"
        ),
        rate_limit=RateLimitConfig(
            requests_per_period=200,
            period_seconds=60
        ),
        user_agent="CustomCrawler/1.0",
        output_format="markdown",
        retries=5,
        timeout=120,
        api_keys={
            "openai_api_key": os.environ.get("OPENAI_API_KEY", ""),
            "opensanctions": os.environ.get("OPENSANCTIONS_API_KEY", ""),
            "bing_api_key": os.environ.get("BING_API_KEY", "")
        },
        proxy=ProxyConfig(
            enabled=False,
            url=os.environ.get("PROXY_URL", "")
        ),
        thread_pool_size=30
    )
    
    # Create crawler with custom configuration
    crawler = PersonIntelCrawler()
    crawler.config = config
    
    # Search for a person
    print("\nStarting custom configuration search...")
    result = await crawler.search("Jane Doe")
    
    # Save results in markdown format
    await crawler.save_results(result, "examples/jane_doe_results.md")
    print(f"Results saved to: examples/jane_doe_results.md")


# Example 3: Save and load configuration
async def example_save_load_configuration():
    """Example of saving and loading configuration."""
    # Create custom configuration
    config = CrawlerConfig(
        social_media=SocialMediaConfig(
            platforms=[
                PlatformConfig(
                    name="twitter",
                    search_url_template="https://twitter.com/search?q={query}&f=user"
                ),
                PlatformConfig(
                    name="linkedin",
                    search_url_template="https://www.linkedin.com/search/results/people/?keywords={query}"
                )
            ]
        ),
        llm=LLMConfig(
            model_name="gpt-4-turbo",
            temperature=0.1,
            prompts=PromptConfig(
                system_message="Custom system message...",
                search_strategy_prompt="Custom search strategy prompt...",
                pep_analysis_prompt="Custom PEP analysis prompt...",
                media_analysis_prompt="Custom media analysis prompt...",
                social_media_analysis_prompt="Custom social media analysis prompt...",
                summary_prompt="Custom summary prompt...",
                risk_assessment_prompt="Custom risk assessment prompt..."
            )
        )
    )
    
    # Save configuration to file
    os.makedirs("examples", exist_ok=True)
    config_path = "examples/custom_config.json"
    with open(config_path, 'w') as f:
        json.dump(config.dict(), f, indent=2)
    
    print(f"\nSaved configuration to: {config_path}")
    
    # Create crawler with loaded configuration
    crawler = PersonIntelCrawler(config_path)
    
    # Verify configuration loaded correctly
    print(f"Loaded configuration with {len(crawler.config.social_media.platforms)} social media platforms")
    print(f"LLM model: {crawler.config.llm.model_name}")


# Example 4: Processing results
async def example_processing_results():
    """Example of processing and analyzing results."""
    # Create crawler
    crawler = PersonIntelCrawler()
    
    # Search for a person
    print("\nStarting search for result processing example...")
    result = await crawler.search("Alex Johnson")
    
    # Access the risk assessment
    print(f"\nRisk Level: {result.risk_level}")
    print(f"Confidence: {result.confidence_score}")
    
    # Access social media profiles
    print("\nSocial Media Profiles:")
    for platform, profiles in result.social_media_profiles.items():
        print(f"  {platform.upper()}: {len(profiles)} profiles found")
        for i, profile in enumerate(profiles, 1):
            print(f"    Profile {i}:")
            print(f"      Username: {profile.username}")
            print(f"      URL: {profile.url}")
            print(f"      Followers: {profile.follower_count or 'Unknown'}")
            print(f"      Verified: {'Yes' if profile.is_verified else 'No'}")
    
    # Access PEP records
    print("\nPEP Records:")
    for i, record in enumerate(result.pep_records, 1):
        print(f"  Record {i}:")
        print(f"    Source: {record.source}")
        print(f"    Position: {record.position or 'Unknown'}")
        print(f"    Country: {record.country or 'Unknown'}")
        print(f"    Risk Level: {record.risk_level.value if record.risk_level else 'Unknown'}")
    
    # Access news articles
    print("\nNews Articles:")
    for i, article in enumerate(result.news_articles, 1):
        print(f"  Article {i}:")
        print(f"    Title: {article.title}")
        print(f"    Source: {article.source}")
        print(f"    Date: {article.published_date}")
        print(f"    Sentiment: {article.sentiment.value if article.sentiment else 'Unknown'}")
    
    # Custom analysis example: count negative articles
    negative_articles = [
        a for a in result.news_articles 
        if a.sentiment in (Sentiment.NEGATIVE, Sentiment.VERY_NEGATIVE)
    ]
    print(f"\nNegative Articles: {len(negative_articles)} out of {len(result.news_articles)}")


# Example