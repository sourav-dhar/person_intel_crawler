# Person Intelligence Crawler Framework: Code Documentation

This document provides detailed technical documentation for the code structure, module interactions, and implementation details.

## Table of Contents

1. [Project Structure](#project-structure)
2. [Module Descriptions](#module-descriptions)
3. [Key Classes and Functions](#key-classes-and-functions)
4. [Workflow Execution](#workflow-execution)
5. [Data Models](#data-models)
6. [Extension Points](#extension-points)
7. [API Reference](#api-reference)
8. [Testing Guidelines](#testing-guidelines)

## Project Structure

```
person_intel_crawler/
│
├── __init__.py                    # Package initialization
├── config/                        # Configuration models
│   ├── __init__.py
│   ├── base_config.py             # Base configuration classes
│   ├── social_media_config.py     # Social media configuration
│   ├── pep_config.py              # PEP database configuration
│   ├── media_config.py            # Adverse media configuration
│   └── llm_config.py              # LLM configuration
│
├── models/                        # Data models
│   ├── __init__.py
│   ├── base_models.py             # Enums and base models
│   ├── social_media_models.py     # Social media data models
│   ├── pep_models.py              # PEP data models
│   ├── media_models.py            # Media data models
│   └── intelligence_models.py     # Intelligence result models
│
├── utils/                         # Utilities
│   ├── __init__.py
│   ├── cache.py                   # Caching utilities
│   ├── rate_limiter.py            # Rate limiting utilities
│   ├── proxy.py                   # Proxy management utilities
│   ├── retry.py                   # Retry handling utilities
│   └── text_analyzer.py           # Text analysis utilities
│
├── crawlers/                      # Crawler implementations
│   ├── __init__.py
│   ├── base_crawler.py            # Base crawler interface
│   ├── social_media_crawler.py    # Social media crawler
│   ├── pep_database_crawler.py    # PEP database crawler
│   └── adverse_media_crawler.py   # Adverse media crawler
│
├── agents/                        # LangGraph agents
│   ├── __init__.py
│   ├── agent_tools.py             # Agent tools
│   ├── agent_prompts.py           # Agent prompts
│   ├── search_strategy_agent.py   # Search strategy agent
│   ├── analysis_agents.py         # Data analysis agents
│   └── langraph_coordinator.py    # LangGraph workflow coordinator
│
├── coordinator.py                 # Main crawler coordinator
├── cli.py                         # Command-line interface
├── api.py                         # API server implementation
└── examples.py                    # Usage examples
```

## Module Descriptions

### Configuration (`config/`)

Contains Pydantic models for all configuration aspects. These models provide validation, default values, and documentation for configuration parameters.

- **base_config.py**: Core configuration models:
  - `CacheConfig`: Caching settings
  - `RateLimitConfig`: Rate limiting parameters
  - `ProxyConfig`: Proxy settings
  - `CrawlerConfig`: Main configuration container

- **social_media_config.py**: Configuration for social media crawling:
  - `PlatformConfig`: Settings for a specific platform
  - `SocialMediaConfig`: Collection of platform configurations

- **pep_config.py**: Configuration for PEP database access:
  - `PEPSourceConfig`: Settings for a specific PEP data source
  - `PEPDatabaseConfig`: Collection of PEP source configurations

- **media_config.py**: Configuration for media sources:
  - `NewsSourceConfig`: Settings for a specific news source
  - `AdverseMediaConfig`: Collection of news source configurations

- **llm_config.py**: Configuration for LLM-based agents:
  - `PromptConfig`: LLM prompt templates
  - `LLMConfig`: LLM model settings and prompt configuration

### Data Models (`models/`)

Contains Pydantic models for data structures used throughout the application.

- **base_models.py**: Base classes and enums:
  - `Sentiment`: Enumeration of sentiment values
  - `SourceType`: Enumeration of source types
  - `RiskLevel`: Enumeration of risk levels
  - `BaseCrawler`: Abstract base class for crawlers

- **social_media_models.py**:
  - `SocialMediaProfile`: Model for social media profile data

- **pep_models.py**:
  - `PEPRecord`: Model for PEP database records

- **media_models.py**:
  - `NewsArticle`: Model for news articles

- **intelligence_models.py**:
  - `SearchResult`: Generic search result model
  - `PersonIntelligence`: Container for all gathered intelligence

### Utilities (`utils/`)

Contains utility classes for common functionality.

- **cache.py**:
  - `CacheManager`: Manages caching of search results

- **rate_limiter.py**:
  - `RateLimiter`: Implements rate limiting across different sources

- **proxy.py**:
  - `ProxyManager`: Manages proxy selection and rotation

- **retry.py**:
  - `RetryHandler`: Implements retry logic with exponential backoff

- **text_analyzer.py**:
  - `TextAnalyzer`: Performs text analysis operations (sentiment, entities, etc.)

### Crawlers (`crawlers/`)

Contains implementations of different crawler types.

- **base_crawler.py**:
  - `BaseCrawler`: Abstract interface for all crawlers

- **social_media_crawler.py**:
  - `SocialMediaCrawler`: Crawls social media platforms

- **pep_database_crawler.py**:
  - `PEPDatabaseCrawler`: Searches PEP databases

- **adverse_media_crawler.py**:
  - `AdverseMediaCrawler`: Searches for adverse media mentions

### LangGraph Agents (`agents/`)

Contains LangGraph-based agent implementations.

- **agent_tools.py**:
  - Utilities for LangGraph agents
  - `SearchStrategyTools`: Tools for search strategy generation
  - `RiskAssessmentTools`: Tools for risk assessment
  - `EntityExtractionTools`: Tools for extracting entities from text
  - `SourceAssessmentTools`: Tools for assessing source credibility

- **agent_prompts.py**:
  - Prompt templates for LLM-based agents
  - Contains structured prompts for different analysis tasks

- **search_strategy_agent.py**:
  - `SearchStrategyAgent`: Generates search strategies

- **analysis_agents.py**:
  - `PEPAnalysisAgent`: Analyzes PEP data
  - `SocialMediaAnalysisAgent`: Analyzes social media profiles
  - `MediaAnalysisAgent`: Analyzes news articles
  - `IntelligenceSummaryAgent`: Generates comprehensive summaries
  - `RiskAssessmentAgent`: Assesses risk levels

- **langraph_coordinator.py**:
  - `LangGraphCoordinator`: Orchestrates the entire workflow

### Core Modules

- **coordinator.py**:
  - `PersonIntelCrawler`: Main class that coordinates the entire process

- **cli.py**:
  - Command-line interface for the application

- **api.py**:
  - FastAPI implementation for REST API access

- **examples.py**:
  - Usage examples for the framework

## Key Classes and Functions

### `PersonIntelCrawler` (coordinator.py)

This is the main entry point for the application. It coordinates all the components and manages the overall workflow.

```python
class PersonIntelCrawler:
    """Main coordinator for the Person Intelligence Crawler framework."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the crawler with configuration."""
        # Load config and initialize components
        
    async def search(self, name: str) -> PersonIntelligence:
        """Search for information about a person across all sources."""
        # Orchestrate the search process
        
    def search_sync(self, name: str) -> PersonIntelligence:
        """Synchronous version of the search method."""
        # Run search in a new event loop
        
    async def save_results(self, result: PersonIntelligence, output_path: str) -> None:
        """Save search results to a file."""
        # Save results in the specified format
```

#### Key Methods:

- `__init__(config_path)`: Initializes the crawler with the specified configuration
- `search(name)`: Searches for information about a person (async)
- `search_sync(name)`: Synchronous wrapper for the search method
- `save_results(result, output_path)`: Saves results to a file

### `LangGraphCoordinator` (agents/langraph_coordinator.py)

Orchestrates the LangGraph-based workflow for intelligent analysis.

```python
class LangGraphCoordinator:
    """Coordinator for the entire intelligence gathering workflow using LangGraph."""
    
    def __init__(self, config: LLMConfig):
        """Initialize the LangGraph coordinator."""
        # Initialize agents and build workflow graph
        
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph for the intelligence workflow."""
        # Define nodes, edges, and conditional paths
        
    async def run_intelligence_workflow(self, name: str, ...) -> PersonIntelligence:
        """Run the complete intelligence workflow."""
        # Execute the LangGraph workflow
```

#### Key Methods:

- `__init__(config)`: Initializes the coordinator with LLM configuration
- `_build_graph()`: Constructs the LangGraph workflow
- `run_intelligence_workflow(name, ...)`: Executes the workflow with input data

### Base Crawler Interface (crawlers/base_crawler.py)

```python
class BaseCrawler(ABC):
    """Base class for all crawlers."""
    
    @abstractmethod
    async def search(self, name: str) -> Any:
        """Search for information about a person."""
        pass
    
    @abstractmethod
    def get_source_type(self) -> SourceType:
        """Get the type of source this crawler handles."""
        pass
```

All crawler implementations must implement these methods.

## Workflow Execution

The system follows a sequential workflow with parallel processing for independent tasks:

1. **Configuration Loading**:
   - Load configuration from file or environment
   - Validate configuration using Pydantic models

2. **Search Strategy Generation**:
   - `SearchStrategyAgent` analyzes the name
   - Generates optimal search parameters

3. **Data Collection** (parallel execution):
   - `SocialMediaCrawler` collects social media profiles
   - `PEPDatabaseCrawler` searches PEP databases
   - `AdverseMediaCrawler` searches for news articles

4. **Data Analysis** (parallel execution):
   - `SocialMediaAnalysisAgent` analyzes social profiles
   - `PEPAnalysisAgent` analyzes PEP records
   - `MediaAnalysisAgent` analyzes news articles

5. **Result Integration**:
   - `IntelligenceSummaryAgent` combines all analyses
   - `RiskAssessmentAgent` evaluates overall risk

6. **Result Processing**:
   - Format results according to user preferences
   - Save to file or return via API

## Data Models

The system uses Pydantic models for all data structures, providing validation and serialization.

### Key Data Models:

#### `PersonIntelligence` (models/intelligence_models.py)

This is the main container for all gathered intelligence.

```python
class PersonIntelligence(BaseModel):
    """Container for all gathered intelligence about a person."""
    name: str
    query_time: datetime = Field(default_factory=datetime.now)
    social_media_profiles: Dict[str, List[SocialMediaProfile]] = Field(default_factory=dict)
    pep_records: List[PEPRecord] = Field(default_factory=list)
    news_articles: List[NewsArticle] = Field(default_factory=list)
    summary: str = ""
    risk_level: RiskLevel = RiskLevel.UNKNOWN
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    sources_checked: Set[str] = Field(default_factory=set)
    sources_successful: Set[str] = Field(default_factory=set)
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the results to a dictionary."""
        # ...
    
    def to_json(self) -> str:
        """Convert the results to a JSON string."""
        # ...
    
    def to_markdown(self) -> str:
        """Generate a markdown report of the findings."""
        # ...
```

#### LangGraph State Models (agents/langraph_coordinator.py)

The LangGraph workflow uses TypedDict models to represent state:

```python
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
```

## Extension Points

The framework is designed for extensibility at several points:

### 1. Adding New Data Sources

Create a new crawler by implementing the `BaseCrawler` interface:

```python
class CustomCrawler(BaseCrawler):
    """Custom crawler implementation."""
    
    def __init__(self, config, crawler_config):
        """Initialize the crawler."""
        # ...
    
    async def search(self, name: str) -> Any:
        """Search for information about a person."""
        # Implement your search logic
        
    def get_source_type(self) -> SourceType:
        """Get the type of source this crawler handles."""
        return SourceType.OTHER  # Or a custom type
```

### 2. Customizing Analysis

Modify the prompts in `agent_prompts.py` to customize analysis behavior:

```python
CUSTOM_ANALYSIS_PROMPT = """
Analyze the following information for {name}:

{data}

Focus on these specific aspects:
1. ...
2. ...
3. ...

Provide a structured analysis with these sections:
...
"""
```

### 3. Adding New Analysis Agents

Create a new agent in the agents directory:

```python
class CustomAnalysisAgent:
    """Custom analysis agent."""
    
    def __init__(self, model_name: str = "gpt-4-turbo", temperature: float = 0.2):
        """Initialize the agent."""
        # ...
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph for the analysis."""
        # ...
    
    async def analyze(self, name: str, data: Any) -> str:
        """Analyze the provided data."""
        # ...
```

### 4. Extending the API

Add new endpoints to `api.py`:

```python
@app.post("/custom_search", response_model=CustomResponse)
async def custom_search(request: CustomRequest, background_tasks: BackgroundTasks):
    """Custom search endpoint."""
    # Implement custom search logic
```

## API Reference

### Command-Line Interface

The CLI provides the following options:

```
python -m cli [NAME] [OPTIONS]

Arguments:
  NAME                Name of the person to search for

Options:
  --config TEXT       Path to configuration file
  --output TEXT       Path to output file
  --format [json|markdown]
                      Output format
  --openai-api-key TEXT
                      OpenAI API key
  --verbose           Enable verbose logging
  --help              Show this message and exit
```

### REST API

The REST API provides the following endpoints:

#### `POST /search`

Start a search for a person.

Request:
```json
{
  "name": "John Smith",
  "include_social_media": true,
  "include_pep": true,
  "include_adverse_media": true,
  "output_format": "json",
  "save_results": false
}
```

Response:
```json
{
  "request_id": "john_smith_20250101120000",
  "name": "John Smith",
  "status": "pending",
  "risk_level": "unknown",
  "confidence_score": 0.0,
  "summary": "Search in progress...",
  "sources_checked": [],
  "timestamp": "2025-01-01T12:00:00Z"
}
```

#### `GET /search/{request_id}/status`

Check the status of a search task.

Response:
```json
{
  "request_id": "john_smith_20250101120000",
  "name": "John Smith",
  "status": "running",
  "completion": 0.5,
  "estimated_time_remaining": 30
}
```

#### `GET /search/{request_id}/result`

Get the full results of a completed search.

Response: (Abbreviated)
```json
{
  "request_id": "john_smith_20250101120000",
  "name": "John Smith",
  "status": "completed",
  "risk_level": "low",
  "confidence_score": 0.85,
  "summary": "...",
  "social_media_profiles": { ... },
  "pep_records": [ ... ],
  "news_articles": [ ... ],
  "sources_checked": [ ... ],
  "sources_successful": [ ... ],
  "errors": [],
  "timestamp": "2025-01-01T12:05:00Z"
}
```

## Testing Guidelines

The project follows these testing guidelines:

### Unit Tests

Unit tests focus on testing individual components in isolation:

```python
# Example unit test for CacheManager
def test_cache_manager_get_set():
    """Test CacheManager get and set operations."""
    config = CacheConfig(enabled=True, ttl=60, cache_dir=".test_cache")
    cache = CacheManager(config)
    
    # Test setting a value
    cache.set("test_query", "test_source", {"result": "data"})
    
    # Test getting the value
    result = cache.get("test_query", "test_source")
    assert result == {"result": "data"}
```

### Integration Tests

Integration tests verify interactions between components:

```python
# Example integration test for crawler and analysis
async def test_crawler_with_analysis():
    """Test crawler integration with analysis agent."""
    crawler = SocialMediaCrawler(social_media_config, crawler_config)
    analyzer = SocialMediaAnalysisAgent()
    
    # Get profiles from crawler
    profiles = await crawler.search("John Smith")
    
    # Analyze the profiles
    analysis = await analyzer.analyze_social_media_data("John Smith", profiles)
    
    # Verify analysis contains expected elements
    assert "John Smith" in analysis
    assert len(analysis) > 100  # Expect substantial content
```

### End-to-End Tests

End-to-end tests verify the complete workflow:

```python
# Example end-to-end test
async def test_full_workflow():
    """Test the entire workflow from request to results."""
    crawler = PersonIntelCrawler()
    
    # Execute search
    result = await crawler.search("John Smith")
    
    # Verify result structure
    assert result.name == "John Smith"
    assert isinstance(result.risk_level, RiskLevel)
    assert len(result.summary) > 0
```

### Mocking External APIs

Use mocks for external API dependencies:

```python
# Example test with mocked API
@patch("openai.Completion.create")
async def test_analysis_with_mocked_llm(mock_create):
    """Test analysis with mocked LLM responses."""
    # Configure the mock
    mock_create.return_value = {
        "choices": [{"text": "Analysis result..."}]
    }
    
    # Run the analysis
    agent = SocialMediaAnalysisAgent()
    analysis = await agent.analyze_social_media_data("John Smith", {})
    
    # Verify the mock was called
    mock_create.assert_called_once()
    
    # Verify the result
    assert "Analysis result" in analysis
```

### Test Commands

Run tests using pytest:

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/

# Run integration tests only
pytest tests/integration/

# Run with coverage report
pytest --cov=person_intel_crawler
```