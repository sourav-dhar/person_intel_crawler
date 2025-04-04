# Command-line interface
"""
Command line interface for the Person Intelligence Crawler.
"""

import os
import argparse
import logging
import sys
from typing import Dict, Any

from coordinator import PersonIntelCrawler
from models.base_models import RiskLevel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("person_intel_crawler.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Person Intelligence Crawler - Search for information about individuals"
    )
    
    parser.add_argument(
        "name",
        type=str,
        help="Name of the person to search for"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="results.json",
        help="Path to output file"
    )
    
    parser.add_argument(
        "--format",
        type=str,
        choices=["json", "markdown"],
        default="json",
        help="Output format"
    )
    
    parser.add_argument(
        "--openai-api-key",
        type=str,
        default=None,
        help="OpenAI API key"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    return parser.parse_args()

def colorize_risk_level(risk_level: RiskLevel) -> str:
    """Colorize risk level text for terminal output."""
    colors = {
        RiskLevel.LOW: "\033[32m",      # Green
        RiskLevel.MEDIUM: "\033[33m",   # Yellow
        RiskLevel.HIGH: "\033[31m",     # Red
        RiskLevel.CRITICAL: "\033[41m\033[37m",  # White on Red background
        RiskLevel.UNKNOWN: "\033[90m",  # Gray
    }
    reset = "\033[0m"
    
    return f"{colors.get(risk_level, '')}{risk_level.value.upper()}{reset}"

def main() -> None:
    """Main entry point for command line usage."""
    args = parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Set API key if provided
    if args.openai_api_key:
        os.environ["OPENAI_API_KEY"] = args.openai_api_key
    
    # Create crawler
    crawler = PersonIntelCrawler(args.config)
    
    # Set output format
    crawler.config.output_format = args.format
    
    print(f"\n🔍 Searching for information about: {args.name}\n")
    
    # Run search
    result = crawler.search_sync(args.name)
    
    # Save results
    crawler.save_results_sync(result, args.output)
    
    # Print summary
    print("\n✅ Search completed")
    print(f"Risk Level: {colorize_risk_level(result.risk_level)}")
    print(f"Confidence Score: {result.confidence_score:.2f}")
    print(f"Sources Checked: {len(result.sources_checked)}")
    print(f"Sources Successful: {len(result.sources_successful)}")
    
    # Print findings summary
    print("\n📋 Summary:")
    summary_lines = result.summary.split("\n")
    # Print first 5 lines of the summary
    for line in summary_lines[:5]:
        print(f"  {line}")
    if len(summary_lines) > 5:
        print("  ...")
    
    print(f"\n💾 Results saved to: {args.output}")
    
    # Print errors if any
    if result.errors:
        print(f"\n⚠️ Encountered {len(result.errors)} errors during search.")
        if args.verbose:
            for error in result.errors[:3]:  # Show first 3 errors
                print(f"  - {error.get('source', 'Unknown')}: {error.get('message', 'Unknown error')}")
            if len(result.errors) > 3:
                print(f"  ... and {len(result.errors) - 3} more errors (see log file for details)")

if __name__ == "__main__":
    main()