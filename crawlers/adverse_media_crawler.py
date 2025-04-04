# Adverse media crawler

class AdverseMediaCrawler(BaseCrawler):
    """Crawler for adverse media mentions."""
    
    def __init__(self, config: AdverseMediaConfig, crawler_config: CrawlerConfig):
        """Initialize adverse media crawler with configuration."""
        self.config = config
        self.crawler_config = crawler_config
        self.cache_manager = CacheManager(crawler_config.cache)
        self.rate_limiter = RateLimiter(crawler_config.rate_limit)
        self.proxy_manager = ProxyManager(crawler_config.proxy)
        self.retry_handler = RetryHandler(max_retries=crawler_config.retries)
        self.text_analyzer = TextAnalyzer()
        
        # Initialize HTTP session
        self.session = None
        
        # Set up Firecrawl for web searches
        fire_config = CrawlConfig(
            user_agent=crawler_config.user_agent,
            max_depth=2,
            request_timeout=30,
            delay_between_requests=crawler_config.request_delay
        )
        
        if crawler_config.proxy.enabled:
            fire_config.proxy = self.proxy_manager.get_proxy()
            
        self.firecrawl = FireCrawl(fire_config)
    
    def get_source_type(self) -> SourceType:
        """Get the type of source this crawler handles."""
        return SourceType.ADVERSE_MEDIA
    
    async def _init_session(self):
        """Initialize aiohttp session for API requests."""
        if self.session is None:
            proxy = self.proxy_manager.get_proxy()
            self.session = aiohttp.ClientSession(
                headers={"User-Agent": self.crawler_config.user_agent}
            )
    
    async def search(self, name: str) -> List[NewsArticle]:
        """Search for adverse media mentions of a person."""
        results = []
        
        # Initialize HTTP session
        await self._init_session()
        
        # Determine date range for search
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.config.timeframe_days)
        
        # Execute searches in parallel
        tasks = []
        for source in self.config.sources:
            if not source.enabled:
                continue
                
            task = asyncio.create_task(
                self._search_source(source, name, start_date, end_date)
            )
            tasks.append(task)
        
        # Gather results
        source_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, source in enumerate([s for s in self.config.sources if s.enabled]):
            result = source_results[i]
            
            if isinstance(result, Exception):
                logger.error(f"Error searching {source.name}: {str(result)}")
                continue
                
            if result:
                results.extend(result)
        
        # Remove duplicates (based on URL)
        seen_urls = set()
        unique_results = []
        
        for article in results:
            if str(article.url) not in seen_urls:
                seen_urls.add(str(article.url))
                unique_results.append(article)
        
        # Sort by date (newest first)
        unique_results.sort(
            key=lambda x: x.published_date if x.published_date else datetime.min, 
            reverse=True
        )
        
        # Close the session
        if self.session:
            await self.session.close()
            self.session = None
        
        return unique_results
    
    async def _search_source(self, source: NewsSourceConfig, name: str, 
                         start_date: datetime, end_date: datetime) -> List[NewsArticle]:
        """Search a specific news source."""
        source_results = []
        
        try:
            # Check cache first
            cache_key = f"{name}_{start_date.strftime('%Y-%m-%d')}_{end_date.strftime('%Y-%m-%d')}"
            cached = self.cache_manager.get(cache_key, f"media:{source.name}")
            if cached:
                return [NewsArticle(**article) for article in cached]
            
            # Apply rate limiting
            self.rate_limiter.wait_if_needed(f"media:{source.name}")
            
            # Execute the search based on the source
            if source.name == "google_news":
                source_results = await self._search_google_news(source, name, start_date, end_date)
            elif source.name == "bing_news":
                source_results = await self._search_bing_news(source, name, start_date, end_date)
            elif source.name == "lexisnexis":
                source_results = await self._search_lexisnexis(source, name, start_date, end_date)
            elif source.name == "factiva":
                source_results = await self._search_factiva(source, name, start_date, end_date)
            else:
                # Generic API-based search
                source_results = await self._search_generic_news_api(source, name, start_date, end_date)
            
            # Apply sentiment analysis if configured
            if self.config.sentiment_analysis:
                for article in source_results:
                    if article.content:
                        article.sentiment = self.text_analyzer.analyze_sentiment(article.content)
            
            # Apply entity recognition if configured
            if self.config.entity_recognition:
                for article in source_results:
                    if article.content:
                        article.entities = self.text_analyzer.extract_entities(article.content)
                        article.keywords = self.text_analyzer.extract_keywords(article.content)
            
            # Generate summaries for articles
            for article in source_results:
                if article.content and not article.summary:
                    article.summary = self.text_analyzer.summarize_text(article.content)
            
            # Cache the results
            if source_results:
                self.cache_manager.set(
                    cache_key, 
                    f"media:{source.name}", 
                    [article.dict() for article in source_results]
                )
            
            return source_results
                
        except Exception as e:
            logger.error(f"Error searching {source.name} for {name}: {str(e)}")
            return []
    
    async def _search_google_news(self, source: NewsSourceConfig, name: str, 
                              start_date: datetime, end_date: datetime) -> List[NewsArticle]:
        """Search Google News for articles."""
        results = []
        
        try:
            # Construct search query with date range
            date_range = f" after:{start_date.strftime('%Y-%m-%d')} before:{end_date.strftime('%Y-%m-%d')}"
            query = f"{name}{date_range}"
            encoded_query = quote_plus(query)
            
            # Construct search URL
            search_url = source.web_search_template.format(query=encoded_query)
            
            # Use Firecrawl to get the results
            async def crawl_search():
                return self.firecrawl.crawl(search_url)
                
            search_pages = await self.retry_handler.execute_with_retry(crawl_search)
            
            if not search_pages:
                return []
            
            # Extract article links from search results
            article_links = []
            for page in search_pages:
                # Extract links to news articles
                links = re.findall(r'<a[^>]*href="([^"]+)"[^>]*class="[^"]*DY5T1d[^"]*"', page.text)
                
                for link in links:
                    # Google News uses relative URLs, convert to absolute
                    if link.startswith('./'):
                        link = f"https://news.google.com{link[1:]}"
                    
                    article_links.append(link)
            
            # Limit the number of articles to process
            article_links = article_links[:self.config.max_results_per_source]
            
            # Process each article
            for link in article_links:
                try:
                    # Google News redirects to the actual article
                    # We need to crawl the redirection target
                    async def crawl_article():
                        return self.firecrawl.crawl(link)
                        
                    article_pages = await self.retry_handler.execute_with_retry(crawl_article)
                    
                    if not article_pages:
                        continue
                    
                    # The first page should be the article
                    article_page = article_pages[0]
                    
                    # Extract article content using common patterns
                    title = self._extract_title(article_page.text) or article_page.title
                    content = self._extract_article_content(article_page.text)
                    
                    if not title or not content:
                        continue
                    
                    # Extract date if possible
                    pub_date = self._extract_publication_date(article_page.text)
                    
                    # Extract authors if possible
                    authors = self._extract_authors(article_page.text)
                    
                    # Create article object
                    article = NewsArticle(
                        source=f"google_news:{urlparse(article_page.url).netloc}",
                        title=title,
                        url=article_page.url,
                        published_date=pub_date,
                        authors=authors,
                        content=content,
                        relevance_score=self._calculate_article_relevance(content, name)
                    )
                    
                    # Skip if the article doesn't seem relevant
                    if article.relevance_score < 0.3:
                        continue
                    
                    results.append(article)
                    
                except Exception as e:
                    logger.warning(f"Error processing article {link}: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error searching Google News for {name}: {str(e)}")
        
        return results
    
    async def _search_bing_news(self, source: NewsSourceConfig, name: str, 
                             start_date: datetime, end_date: datetime) -> List[NewsArticle]:
        """Search Bing News for articles."""
        results = []
        
        try:
            # Check for API key
            api_key = self.crawler_config.api_keys.get(source.api_key_name)
            if not api_key:
                logger.error("Bing News API key not provided")
                return []
            
            # Construct API endpoint
            endpoint = f"{source.api_url}{source.search_endpoint}"
            
            # Format dates for Bing's API
            freshness = "Week"  # Default to one week
            if (end_date - start_date).days > 30:
                freshness = "Month"
            
            # Prepare the request
            headers = {"Ocp-Apim-Subscription-Key": api_key}
            
            params = {
                "q": name,
                "count": self.config.max_results_per_source,
                "freshness": freshness,
                "mkt": "en-US",
                "safeSearch": "Moderate"
            }
            
            # Make the request with retry logic
            async def make_request():
                async with self.session.get(
                    endpoint, 
                    params=params,
                    headers=headers, 
                    timeout=source.timeout
                ) as response:
                    response.raise_for_status()
                    return await response.json()
            
            data = await self.retry_handler.execute_with_retry(make_request)
            
            # Process the results
            for article in data.get("value", []):
                pub_date = None
                if article.get("datePublished"):
                    try:
                        pub_date = datetime.fromisoformat(article["datePublished"].replace("Z", "+00:00"))
                    except (ValueError, TypeError):
                        pass
                
                # Skip if the article is outside our date range
                if pub_date and (pub_date < start_date or pub_date > end_date):
                    continue
                
                # Create article object
                news_article = NewsArticle(
                    source=f"bing_news:{article.get('provider', [{}])[0].get('name', 'Unknown')}",
                    title=article.get("name", ""),
                    url=article.get("url", ""),
                    published_date=pub_date,
                    authors=[],  # Bing doesn't typically provide author info
                    content=article.get("description", ""),
                    language=article.get("language", ""),
                    relevance_score=self._calculate_article_relevance(
                        article.get("description", ""), name
                    )
                )
                
                # Skip if the article doesn't seem relevant
                if news_article.relevance_score < 0.3:
                    continue
                
                results.append(news_article)
            
        except Exception as e:
            logger.error(f"Error searching Bing News for {name}: {str(e)}")
        
        return results
    
    async def _search_lexisnexis(self, source: NewsSourceConfig, name: str, 
                              start_date: datetime, end_date: datetime) -> List[NewsArticle]:
        """Search LexisNexis for articles."""
        # Actual implementation would depend on LexisNexis API
        # This is a placeholder based on typical API patterns
        results = []
        
        try:
            # Check for API key
            api_key = self.crawler_config.api_keys.get(source.api_key_name)
            if not api_key:
                logger.error("LexisNexis API key not provided")
                return []
            
            # Construct API endpoint
            endpoint = f"{source.api_url}{source.search_endpoint}"
            
            # Prepare the request
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "query": name,
                "from": start_date.strftime("%Y-%m-%d"),
                "to": end_date.strftime("%Y-%m-%d"),
                "limit": self.config.max_results_per_source,
                "sortBy": "date",
                "order": "desc",
                "sources": ["news", "web"],
                "languages": self.config.language_codes
            }
            
            # Make the request with retry logic
            async def make_request():
                async with self.session.post(
                    endpoint, 
                    json=payload,
                    headers=headers, 
                    timeout=source.timeout
                ) as response:
                    response.raise_for_status()
                    return await response.json()
            
            data = await self.retry_handler.execute_with_retry(make_request)
            
            # Process the results
            for article in data.get("articles", []):
                pub_date = None
                if article.get("publishedDate"):
                    try:
                        pub_date = datetime.fromisoformat(article["publishedDate"].replace("Z", "+00:00"))
                    except (ValueError, TypeError):
                        pass
                
                # Create article object
                news_article = NewsArticle(
                    source=f"lexisnexis:{article.get('source', 'Unknown')}",
                    title=article.get("title", ""),
                    url=article.get("url", ""),
                    published_date=pub_date,
                    authors=article.get("authors", []),
                    content=article.get("content", ""),
                    summary=article.get("snippet", ""),
                    language=article.get("language", ""),
                    relevance_score=article.get("relevanceScore", 0) / 100  # Normalize to 0-1
                )
                
                # Skip if the article doesn't seem relevant
                if news_article.relevance_score < 0.3:
                    continue
                
                results.append(news_article)
            
        except Exception as e:
            logger.error(f"Error searching LexisNexis for {name}: {str(e)}")
        
        return results
    
    async def _search_factiva(self, source: NewsSourceConfig, name: str, 
                          start_date: datetime, end_date: datetime) -> List[NewsArticle]:
        """Search Dow Jones Factiva for articles."""
        # Similar to LexisNexis implementation
        # Customized for Factiva's API
        return []
    
    async def _search_generic_news_api(self, source: NewsSourceConfig, name: str, 
                                    start_date: datetime, end_date: datetime) -> List[NewsArticle]:
        """Generic implementation for other news API sources."""
        results = []
        
        try:
            # Check if API requires auth
            if source.requires_auth:
                api_key = self.crawler_config.api_keys.get(source.api_key_name)
                if not api_key:
                    logger.error(f"{source.name} API key not provided")
                    return []
            
            # Construct API endpoint
            endpoint = f"{source.api_url}{source.search_endpoint}"
            
            # Prepare the request
            params = {
                "q": name,
                "from": start_date.strftime("%Y-%m-%d"),
                "to": end_date.strftime("%Y-%m-%d"),
                "limit": self.config.max_results_per_source
            }
            
            headers = {}
            if source.requires_auth and source.api_key_name in self.crawler_config.api_keys:
                headers["Authorization"] = f"Bearer {self.crawler_config.api_keys[source.api_key_name]}"
            
            # Make the request with retry logic
            async def make_request():
                async with self.session.get(
                    endpoint, 
                    params=params,
                    headers=headers, 
                    timeout=source.timeout
                ) as response:
                    response.raise_for_status()
                    return await response.json()
            
            data = await self.retry_handler.execute_with_retry(make_request)
            
            # Process the results (generic implementation)
            # Adjust based on actual API response format
            for article in data.get("articles", []):
                pub_date = None
                if article.get("publishedAt"):
                    try:
                        pub_date = datetime.fromisoformat(article["publishedAt"].replace("Z", "+00:00"))
                    except (ValueError, TypeError):
                        pass
                
                # Create article object
                news_article = NewsArticle(
                    source=f"{source.name}:{article.get('source', {}).get('name', 'Unknown')}",
                    title=article.get("title", ""),
                    url=article.get("url", ""),
                    published_date=pub_date,
                    authors=[article.get("author")] if article.get("author") else [],
                    content=article.get("content", "") or article.get("description", ""),
                    relevance_score=self._calculate_article_relevance(
                        article.get("content", "") or article.get("description", ""),
                        name
                    )
                )
                
                # Skip if the article doesn't seem relevant
                if news_article.relevance_score < 0.3:
                    continue
                
                results.append(news_article)
            
        except Exception as e:
            logger.error(f"Error searching {source.name} for {name}: {str(e)}")
        
        return results
    
    def _extract_title(self, html: str) -> Optional[str]:
        """Extract article title from HTML."""
        if not html:
            return None
            
        # Try common title tag patterns
        title_patterns = [
            r'<h1[^>]*>(.*?)</h1>',
            r'<meta property="og:title" content="([^"]+)"',
            r'<title>(.*?)</title>'
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, html, re.DOTALL)
            if match:
                # Clean up the title
                title = re.sub(r'<[^>]+>', '', match.group(1)).strip()
                return title
                
        return None
    
    def _extract_article_content(self, html: str) -> Optional[str]:
        """Extract article content from HTML."""
        if not html:
            return None
            
        # Try common content patterns
        content_patterns = [
            # Article body
            r'<article[^>]*>(.*?)</article>',
            # Main content div
            r'<div[^>]*class="[^"]*article-body[^"]*"[^>]*>(.*?)</div>',
            r'<div[^>]*class="[^"]*story-body[^"]*"[^>]*>(.*?)</div>',
            r'<div[^>]*class="[^"]*content-body[^"]*"[^>]*>(.*?)</div>',
            # Paragraphs within content area
            r'<div[^>]*class="[^"]*article[^"]*"[^>]*>.*?(<p>.*?</p>).*?</div>'
        ]
        
        for pattern in content_patterns:
            match = re.search(pattern, html, re.DOTALL)
            if match:
                # Extract all paragraphs from the matched content
                paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', match.group(1), re.DOTALL)
                
                if paragraphs:
                    # Clean up the paragraphs
                    cleaned_paragraphs = [re.sub(r'<[^>]+>', '', p).strip() for p in paragraphs]
                    # Filter out empty paragraphs
                    filtered_paragraphs = [p for p in cleaned_paragraphs if p]
                    
                    if filtered_paragraphs:
                        return ' '.join(filtered_paragraphs)
        
        # Fallback: try to extract all paragraphs
        paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', html, re.DOTALL)
        if paragraphs:
            # Clean up the paragraphs
            cleaned_paragraphs = [re.sub(r'<[^>]+>', '', p).strip() for p in paragraphs]
            # Filter out empty paragraphs
            filtered_paragraphs = [p for p in cleaned_paragraphs if p]
            
            if filtered_paragraphs:
                return ' '.join(filtered_paragraphs)
                
        return None
    
    def _extract_publication_date(self, html: str) -> Optional[datetime]:
        """Extract publication date from HTML."""
        if not html:
            return None
            
        # Try common date patterns
        date_patterns = [
            r'<meta property="article:published_time" content="([^"]+)"',
            r'<time[^>]*datetime="([^"]+)"',
            r'<span[^>]*class="[^"]*date[^"]*"[^>]*>(.*?)</span>'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, html)
            if match:
                date_str = match.group(1)
                try:
                    # Try ISO format first
                    return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    # Try more relaxed parsing for text dates
                    try:
                        from dateutil import parser
                        return parser.parse(date_str)
                    except (ValueError, ImportError):
                        pass
                        
        return None
    
    def _extract_authors(self, html: str) -> List[str]:
        """Extract authors from HTML."""
        if not html:
            return []
            
        # Try common author patterns
        author_patterns = [
            r'<meta name="author" content="([^"]+)"',
            r'<span[^>]*class="[^"]*author[^"]*"[^>]*>(.*?)</span>',
            r'<a[^>]*rel="author"[^>]*>(.*?)</a>'
        ]
        
        authors = []
        for pattern in author_patterns:
            matches = re.findall(pattern, html)
            for match in matches:
                # Clean up the author name
                author = re.sub(r'<[^>]+>', '', match).strip()
                if author and author not in authors:
                    authors.append(author)
                    
        return authors
    
    def _calculate_article_relevance(self, content: str, name: str) -> float:
        """Calculate relevance score for an article."""
        if not content:
            return 0.0
            
        # Simple relevance calculation
        name_parts = name.lower().split()
        content_lower = content.lower()
        
        # Count occurrences of name parts
        name_occurrences = sum(content_lower.count(part) for part in name_parts)
        
        # Check for exact name match (with higher weight)
        exact_matches = content_lower.count(name.lower()) * 2
        
        # Combined score
        score = min((name_occurrences + exact_matches) / (10 + len(content) / 1000), 1.0)
        
        return score"""