# Person Intelligence Crawler Framework: Process Documentation

This document provides a detailed explanation of the application processes, deployment procedures, and operational guidelines.

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Deployment Process](#deployment-process)
4. [Configuration](#configuration)
5. [API Access](#api-access)
6. [Maintenance Procedures](#maintenance-procedures)
7. [Monitoring and Logging](#monitoring-and-logging)
8. [Security Considerations](#security-considerations)
9. [Troubleshooting](#troubleshooting)

## System Overview

The Person Intelligence Crawler Framework is a comprehensive system designed to gather, analyze, and report on information about individuals from various public sources. It combines web crawling, AI-powered analysis, and risk assessment to generate intelligence reports.

### Key Capabilities

- **Multi-source Intelligence Gathering**: Collects data from social media, PEP databases, and news sources
- **AI-driven Analysis**: Uses LLM agents to analyze and interpret collected data
- **Risk Assessment**: Evaluates overall risk levels based on integrated analysis
- **Flexible Output**: Provides structured data in JSON or human-readable Markdown formats
- **API Access**: Enables integration with other systems via REST API

## Architecture

The system follows a modular microservices architecture organized into the following components:

### Core Components

1. **Crawler Services**
   - Social Media Crawler
   - PEP Database Crawler
   - Adverse Media Crawler

2. **Analysis Pipeline**
   - Search Strategy Agent
   - Data Collection Coordinator
   - Analysis Agents (Social Media, PEP, Media)
   - Summary Generator
   - Risk Assessment Engine

3. **Infrastructure**
   - API Server
   - Caching System
   - Rate Limiter
   - Proxy Manager

### Data Flow

```
User Request → Search Strategy → Parallel Data Collection → Analysis → Summary → Risk Assessment → Results
```

### Component Interaction

1. User initiates search via CLI or API
2. Search strategy is generated based on the name
3. Crawlers collect data from configured sources
4. LLM agents analyze collected data independently
5. Results are synthesized into a comprehensive summary
6. Risk level is assessed based on integrated analysis
7. Structured results are returned to the user

## Deployment Process

### Prerequisites

- Docker and Docker Compose
- API keys for LLM services and data sources (see [API Access](#api-access))
- 4GB+ RAM for running the containers
- Network access to external APIs and data sources

### Deployment Options

#### Option 1: Docker-based Deployment

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/person-intel-crawler.git
   cd person-intel-crawler
   ```

2. **Configure environment variables**
   ```bash
   cp .env.template .env
   # Edit the .env file with your API keys and configuration
   ```

3. **Build and start the containers**
   ```bash
   docker-compose build
   docker-compose up -d
   ```

4. **Verify deployment**
   ```bash
   curl http://localhost:8000/health
   ```

#### Option 2: Kubernetes Deployment

1. **Build and push Docker images**
   ```bash
   docker build -t your-registry/person-intel-crawler:latest .
   docker build -t your-registry/person-intel-crawler-api:latest -f Dockerfile.api .
   docker push your-registry/person-intel-crawler:latest
   docker push your-registry/person-intel-crawler-api:latest
   ```

2. **Create Kubernetes secrets**
   ```bash
   kubectl create secret generic person-intel-crawler-env --from-file=.env
   ```

3. **Apply Kubernetes manifests**
   ```bash
   kubectl apply -f k8s/
   ```

4. **Check deployment status**
   ```bash
   kubectl get pods -l app=person-intel-crawler
   ```

### Scaling Considerations

- The API service can be scaled horizontally for higher throughput
- Consider resource allocation based on expected query volume
- Cache results to reduce API calls to external services
- Implement proper rate limiting to avoid API quota issues

## Configuration

The system is highly configurable via environment variables and configuration files.

### Environment Variables

All configuration can be set via environment variables. See `.env.template` for a complete list of available options.

Key environment variables:

- `OPENAI_API_KEY`: Required for LLM functionality
- `LOG_LEVEL`: Controls logging verbosity
- `CACHE_ENABLED`: Enables/disables result caching
- `RATE_LIMIT_REQUESTS`: Controls API rate limiting

### Configuration Files

For more detailed configuration, use JSON configuration files:

```bash
# Run with custom configuration
python -m cli "John Smith" --config custom_config.json
```

Configuration precedence (highest to lowest):
1. Command-line arguments
2. Configuration files
3. Environment variables
4. Default values

## API Access

### Required API Keys

| API | Purpose | Type | Notes |
|-----|---------|------|-------|
| OpenAI | LLM functionality | Required | Powers all analysis |
| OpenSanctions | PEP data | Optional | Free tier available |
| WorldCheck | PEP data | Optional | Paid (Refinitiv) |
| Dow Jones | Risk & Compliance | Optional | Paid (Enterprise) |
| Bing News | Media search | Optional | Microsoft Azure |
| LexisNexis | Media search | Optional | Paid (Enterprise) |
| Factiva | Media search | Optional | Paid (Dow Jones) |

### Rate Limits and Quotas

Be aware of the rate limits for each service:

- **OpenAI**: Varies by subscription tier
- **OpenSanctions**: 100 requests/hour (free tier)
- **Bing News**: 1000 requests/month (free tier)

The system implements built-in rate limiting to help manage these quotas.

## Maintenance Procedures

### Regular Maintenance

1. **Update dependencies**
   ```bash
   pip install -U -r requirements.txt
   ```

2. **Update spaCy models**
   ```bash
   python -m spacy download --upgrade en_core_web_sm
   ```

3. **Cache management**
   ```bash
   # Clear cache older than 30 days
   find .cache -type f -mtime +30 -delete
   ```

### Backup Procedures

1. **Configuration backup**
   ```bash
   cp .env .env.backup-$(date +%Y%m%d)
   cp -r config/ config-backup-$(date +%Y%m%d)
   ```

2. **Results backup**
   ```bash
   # Archive all results older than 7 days
   find data -name "*.json" -mtime +7 -exec tar -rf archive.tar {} \;
   ```

## Monitoring and Logging

### Logging System

The application uses Python's logging module with configurable levels:

- `DEBUG`: Detailed debugging information
- `INFO`: General operational information
- `WARNING`: Issues that might require attention
- `ERROR`: Error conditions
- `CRITICAL`: Critical failures

Logs are stored in the `logs/` directory and can be accessed in Docker containers at `/app/logs/`.

### Monitoring

For production deployments, consider:

1. **Health checks**
   - API endpoint: `GET /health`
   - CLI command: `python -m cli --status`

2. **Prometheus metrics**
   - API endpoint: `GET /metrics`
   - Key metrics: request counts, success rates, response times

3. **Alert configuration**
   - Set up alerts for high error rates
   - Monitor API key usage to prevent quota exhaustion

## Security Considerations

### Data Security

- The system only collects publicly available information
- No sensitive data is stored by default
- Results are stored temporarily and can be configured for automatic deletion

### API Key Management

- Never commit API keys to source control
- Use environment variables or secure vaults
- Implement key rotation policies

### Network Security

- Use HTTPS for all API communications
- Consider VPN or private network for production deployments
- Implement proper firewall rules

### Access Control

- API authentication via API keys
- Implement rate limiting per client
- Consider IP-based access restrictions

## Troubleshooting

### Common Issues

1. **API Key Issues**
   - Error: "Authentication error" or "API key invalid"
   - Solution: Verify API keys in the .env file

2. **Rate Limiting**
   - Error: "Rate limit exceeded" or "Too many requests"
   - Solution: Adjust rate limiting parameters or implement backoff

3. **Memory Issues**
   - Error: "Out of memory" or container crashes
   - Solution: Increase container memory allocation

4. **Network Issues**
   - Error: "Connection refused" or timeouts
   - Solution: Check network connectivity and proxy settings

### Diagnostic Tools

1. **Check logs**
   ```bash
   docker-compose logs -f person-intel-crawler
   ```

2. **Test connectivity**
   ```bash
   python -m utils.connectivity_test
   ```

3. **Check API quotas**
   ```bash
   python -m utils.api_quota_check
   ```

### Support Resources

- GitHub Issues: [https://github.com/yourusername/person-intel-crawler/issues](https://github.com/yourusername/person-intel-crawler/issues)
- Documentation Wiki: [https://github.com/yourusername/person-intel-crawler/wiki](https://github.com/yourusername/person-intel-crawler/wiki)