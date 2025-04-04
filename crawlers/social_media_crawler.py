# Social media crawler
class PEPDatabaseCrawler(BaseCrawler):
    """Crawler for PEP (Politically Exposed Person) databases."""
    
    def __init__(self, config: PEPDatabaseConfig, crawler_config: CrawlerConfig):
        """Initialize PEP database crawler with configuration."""
        self.config = config
        self.crawler_config = crawler_config
        self.cache_manager = CacheManager(crawler_config.cache)
        self.rate_limiter = RateLimiter(crawler_config.rate_limit)
        self.proxy_manager = ProxyManager(crawler_config.proxy)
        self.retry_handler = RetryHandler(max_retries=crawler_config.retries)
        self.text_analyzer = TextAnalyzer()
        
        # Initialize HTTP session
        self.session = None
    
    def get_source_type(self) -> SourceType:
        """Get the type of source this crawler handles."""
        return SourceType.PEP_DATABASE
    
    async def _init_session(self):
        """Initialize aiohttp session for API requests."""
        if self.session is None:
            proxy = self.proxy_manager.get_proxy()
            self.session = aiohttp.ClientSession(
                headers={"User-Agent": self.crawler_config.user_agent}
            )
    
    async def search(self, name: str) -> List[PEPRecord]:
        """Search for a person across configured PEP databases."""
        results = []
        
        # Initialize HTTP session
        await self._init_session()
        
        # Execute searches in parallel
        tasks = []
        for source in self.config.sources:
            if not source.enabled:
                continue
                
            task = asyncio.create_task(self._search_source(source, name))
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
        
        # Sort by similarity score
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        
        # Close the session
        if self.session:
            await self.session.close()
            self.session = None
        
        return results
    
    async def _search_source(self, source: PEPSourceConfig, name: str) -> List[PEPRecord]:
        """Search a specific PEP database."""
        source_results = []
        
        try:
            # Check cache first
            cached = self.cache_manager.get(name, f"pep:{source.name}")
            if cached:
                return [PEPRecord(**record) for record in cached]
            
            # Apply rate limiting
            self.rate_limiter.wait_if_needed(f"pep:{source.name}")
            
            # Execute the search based on the source
            if source.name == "opensanctions":
                source_results = await self._search_opensanctions(source, name)
            elif source.name in ["ofac", "un_sanctions", "eu_sanctions"]:
                source_results = await self._search_sanction_list(source, name)
            elif source.name == "worldcheck":
                source_results = await self._search_worldcheck(source, name)
            elif source.name == "dowjones":
                source_results = await self._search_dowjones(source, name)
            else:
                # Generic API-based search
                source_results = await self._search_generic_api(source, name)
            
            # Cache the results
            if source_results:
                self.cache_manager.set(
                    name, 
                    f"pep:{source.name}", 
                    [record.dict() for record in source_results]
                )
            
            return source_results
                
        except Exception as e:
            logger.error(f"Error searching {source.name} for {name}: {str(e)}")
            return []
    
    async def _search_opensanctions(self, source: PEPSourceConfig, name: str) -> List[PEPRecord]:
        """Search the OpenSanctions database."""
        results = []
        
        try:
            # OpenSanctions API endpoint
            endpoint = f"{source.api_url}{source.search_endpoint}"
            
            # Prepare the request
            params = {
                "q": name,
                "limit": 20
            }
            
            # Add API key if available
            api_key = self.crawler_config.api_keys.get("opensanctions")
            headers = {"Authorization": f"ApiKey {api_key}"} if api_key else {}
            
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
            for entity in data.get("results", []):
                # Calculate name similarity
                entity_name = entity.get("name", "")
                similarity = self.text_analyzer.calculate_name_similarity(entity_name, name)
                
                # Skip if similarity is below threshold
                if similarity < self.config.similarity_threshold:
                    continue
                
                # Create PEP record
                record = PEPRecord(
                    source="opensanctions",
                    name=entity_name,
                    url=entity.get("url") or f"https://opensanctions.org/entities/{entity.get('id')}",
                    position=entity.get("position"),
                    organization=entity.get("organization"),
                    country=entity.get("country"),
                    sanctions=[{"name": s} for s in entity.get("sanctions", [])],
                    watchlists=entity.get("datasets", []),
                    related_entities=[{"name": r.get("name"), "relationship": r.get("relationship")} 
                                    for r in entity.get("related", [])],
                    similarity_score=similarity
                )
                
                # Set risk level based on sanctions
                if entity.get("sanctions"):
                    record.risk_level = RiskLevel.HIGH
                elif entity.get("position") or entity.get("political"):
                    record.risk_level = RiskLevel.MEDIUM
                else:
                    record.risk_level = RiskLevel.LOW
                
                results.append(record)
            
        except Exception as e:
            logger.error(f"Error searching OpenSanctions for {name}: {str(e)}")
        
        return results
    
    async def _search_sanction_list(self, source: PEPSourceConfig, name: str) -> List[PEPRecord]:
        """Search various sanction lists (OFAC, UN, EU)."""
        results = []
        
        try:
            # Construct API endpoint
            endpoint = f"{source.api_url}{source.search_endpoint}"
            
            # Prepare request parameters based on the specific list
            params = {"name": name}
            
            if source.name == "ofac":
                params = {"name": name, "type": "individual"}
            elif source.name == "un_sanctions":
                params = {"nameSearch": name}
            elif source.name == "eu_sanctions":
                params = {"name": name, "type": "person"}
            
            # Make the request with retry logic
            async def make_request():
                async with self.session.get(
                    endpoint, 
                    params=params, 
                    timeout=source.timeout
                ) as response:
                    response.raise_for_status()
                    return await response.json()
            
            data = await self.retry_handler.execute_with_retry(make_request)
            
            # Process results (specifics depend on the API response format)
            # This is a generic implementation that would need customization
            entities = data.get("results", [])
            
            for entity in entities:
                # Extract relevant fields (adjust based on actual API response)
                entity_name = entity.get("name", "")
                similarity = self.text_analyzer.calculate_name_similarity(entity_name, name)
                
                # Skip if similarity is below threshold
                if similarity < self.config.similarity_threshold:
                    continue
                
                # Create PEP record
                record = PEPRecord(
                    source=source.name,
                    name=entity_name,
                    url=entity.get("url"),
                    position=entity.get("title"),
                    organization=entity.get("organization"),
                    country=entity.get("nationality") or entity.get("country"),
                    sanctions=[{"name": entity.get("program"), "date": entity.get("listingDate")}] 
                            if entity.get("program") else [],
                    watchlists=[source.name],
                    similarity_score=similarity,
                    risk_level=RiskLevel.HIGH  # Being on a sanctions list is high risk
                )
                
                results.append(record)
            
        except Exception as e:
            logger.error(f"Error searching {source.name} for {name}: {str(e)}")
        
        return results
    
    async def _search_worldcheck(self, source: PEPSourceConfig, name: str) -> List[PEPRecord]:
        """Search the Refinitiv World-Check database."""
        # The actual implementation would depend on Refinitiv's API
        # This is a placeholder based on general API patterns
        results = []
        
        try:
            # Check for API key
            api_key = self.crawler_config.api_keys.get("worldcheck")
            if not api_key:
                logger.error("WorldCheck API key not provided")
                return []
            
            # Construct API endpoint
            endpoint = f"{source.api_url}{source.search_endpoint}"
            
            # Prepare the request
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "name": name,
                "match_type": "fuzzy" if not self.config.require_exact_match else "exact",
                "categories": ["PEP", "SANCTION", "ENFORCEMENT", "ADVERSE_MEDIA"],
                "date_type": "current"
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
            for entity in data.get("hits", []):
                # Calculate name similarity
                entity_name = entity.get("name", "")
                similarity = self.text_analyzer.calculate_name_similarity(entity_name, name)
                
                # Skip if similarity is below threshold
                if similarity < self.config.similarity_threshold:
                    continue
                
                # Create PEP record
                record = PEPRecord(
                    source="worldcheck",
                    name=entity_name,
                    url=None,  # WorldCheck typically doesn't provide public URLs
                    position=entity.get("position"),
                    organization=entity.get("primary_category"),
                    country=entity.get("country_names", [None])[0],
                    sanctions=[{"name": s.get("name"), "date": s.get("date")} 
                              for s in entity.get("sanctions", [])],
                    watchlists=entity.get("watchlists", []),
                    related_entities=[{"name": r.get("name"), "relationship": r.get("relationship")} 
                                    for r in entity.get("associates", [])],
                    similarity_score=similarity,
                    last_updated=datetime.fromisoformat(entity.get("update_date", "")) 
                                if entity.get("update_date") else None
                )
                
                # Set risk level based on categories
                categories = entity.get("categories", [])
                if "SANCTION" in categories:
                    record.risk_level = RiskLevel.HIGH
                elif "PEP" in categories:
                    record.risk_level = RiskLevel.MEDIUM
                elif "ADVERSE_MEDIA" in categories:
                    record.risk_level = RiskLevel.MEDIUM
                else:
                    record.risk_level = RiskLevel.LOW
                
                results.append(record)
            
        except Exception as e:
            logger.error(f"Error searching WorldCheck for {name}: {str(e)}")
        
        return results
    
    async def _search_dowjones(self, source: PEPSourceConfig, name: str) -> List[PEPRecord]:
        """Search the Dow Jones Risk & Compliance database."""
        # Similar to the WorldCheck implementation
        # Customized for Dow Jones' API
        return []
    
    async def _search_generic_api(self, source: PEPSourceConfig, name: str) -> List[PEPRecord]:
        """Generic implementation for other API-based sources."""
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
            params = {"name": name, "limit": 20}
            
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
            for entity in data.get("results", []):
                # Calculate name similarity
                entity_name = entity.get("name", "")
                similarity = self.text_analyzer.calculate_name_similarity(entity_name, name)
                
                # Skip if similarity is below threshold
                if similarity < self.config.similarity_threshold:
                    continue
                
                # Create PEP record with available fields
                record = PEPRecord(
                    source=source.name,
                    name=entity_name,
                    url=entity.get("url"),
                    position=entity.get("position") or entity.get("title"),
                    organization=entity.get("organization") or entity.get("entity"),
                    country=entity.get("country") or entity.get("nationality"),
                    similarity_score=similarity
                )
                
                # Add any available sanctions
                if "sanctions" in entity:
                    record.sanctions = entity["sanctions"]
                    record.risk_level = RiskLevel.HIGH
                elif "pep" in entity and entity["pep"]:
                    record.risk_level = RiskLevel.MEDIUM
                else:
                    record.risk_level = RiskLevel.LOW
                
                results.append(record)
            
        except Exception as e:
            logger.error(f"Error searching {source.name} for {name}: {str(e)}")
        
        return results