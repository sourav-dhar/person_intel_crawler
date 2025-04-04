"""
FastAPI server for the Person Intelligence Crawler.
"""

import os
import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Header, Query, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

from coordinator import PersonIntelCrawler
from models.base_models import RiskLevel, SourceType
from models.intelligence_models import PersonIntelligence

# Configure logging
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/api.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("api")

# API models
class SearchRequest(BaseModel):
    """Request model for person search."""
    name: str
    include_social_media: bool = True
    include_pep: bool = True
    include_adverse_media: bool = True
    output_format: str = "json"
    save_results: bool = False
    output_path: Optional[str] = None


class SearchResponse(BaseModel):
    """Response model for person search."""
    request_id: str
    name: str
    status: str
    risk_level: RiskLevel
    confidence_score: float
    summary: str
    sources_checked: List[str]
    timestamp: datetime


class SearchResultResponse(BaseModel):
    """Response model with full search results."""
    request_id: str
    name: str
    status: str
    risk_level: RiskLevel
    confidence_score: float
    summary: str
    social_media_profiles: Dict[str, List[Any]]
    pep_records: List[Any]
    news_articles: List[Any]
    sources_checked: List[str]
    sources_successful: List[str]
    errors: List[Dict[str, Any]]
    timestamp: datetime


class StatusResponse(BaseModel):
    """Response model for checking task status."""
    request_id: str
    name: str
    status: str
    completion: float
    estimated_time_remaining: Optional[int] = None


# In-memory storage for background tasks
task_storage = {}

# API key security
API_KEY_NAME = "X-API-Key"
API_KEY = os.environ.get("API_KEY", "development_key")
api_key_header = APIKeyHeader(name=API_KEY_NAME)


def get_api_key(api_key: str = Header(..., alias=API_KEY_NAME)):
    """Validate API key."""
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
    return api_key


# Initialize FastAPI app
app = FastAPI(
    title="Person Intelligence API",
    description="API for the Person Intelligence Crawler",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Specify allowed origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize crawler
crawler = PersonIntelCrawler()


async def run_search_task(request_id: str, search_request: SearchRequest):
    """Run search task in background."""
    try:
        task_storage[request_id]["status"] = "running"
        task_storage[request_id]["start_time"] = datetime.now()
        
        # Configure sources based on request
        crawler.config.social_media.platforms = [
            p for p in crawler.config.social_media.platforms 
            if p.enabled and search_request.include_social_media
        ]
        
        crawler.config.pep_database.sources = [
            s for s in crawler.config.pep_database.sources 
            if s.enabled and search_request.include_pep
        ]
        
        crawler.config.adverse_media.sources = [
            s for s in crawler.config.adverse_media.sources 
            if s.enabled and search_request.include_adverse_media
        ]
        
        # Set output format
        crawler.config.output_format = search_request.output_format
        
        # Perform search
        result = await crawler.search(search_request.name)
        
        # Save results if requested
        if search_request.save_results and search_request.output_path:
            await crawler.save_results(result, search_request.output_path)
        
        # Update task storage
        task_storage[request_id]["status"] = "completed"
        task_storage[request_id]["result"] = result
        task_storage[request_id]["completion"] = 1.0
        task_storage[request_id]["end_time"] = datetime.now()
        
    except Exception as e:
        logger.error(f"Error in search task {request_id}: {str(e)}")
        task_storage[request_id]["status"] = "failed"
        task_storage[request_id]["error"] = str(e)
        task_storage[request_id]["completion"] = 0.0
        task_storage[request_id]["end_time"] = datetime.now()


@app.post("/search", response_model=SearchResponse, dependencies=[Depends(get_api_key)])
async def search_person(search_request: SearchRequest, background_tasks: BackgroundTasks):
    """Start a search for a person."""
    request_id = f"{search_request.name.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Initialize task in storage
    task_storage[request_id] = {
        "name": search_request.name,
        "status": "pending",
        "request": search_request,
        "completion": 0.0,
        "start_time": None,
        "end_time": None,
        "result": None,
        "error": None
    }
    
    # Start the task in the background
    background_tasks.add_task(run_search_task, request_id, search_request)
    
    return SearchResponse(
        request_id=request_id,
        name=search_request.name,
        status="pending",
        risk_level=RiskLevel.UNKNOWN,
        confidence_score=0.0,
        summary="Search in progress...",
        sources_checked=[],
        timestamp=datetime.now()
    )


@app.get("/search/{request_id}/status", response_model=StatusResponse, dependencies=[Depends(get_api_key)])
async def get_search_status(request_id: str):
    """Get the status of a search task."""
    if request_id not in task_storage:
        raise HTTPException(status_code=404, detail="Search task not found")
    
    task = task_storage[request_id]
    
    # Calculate estimated time remaining
    estimated_time_remaining = None
    if task["status"] == "running" and task["start_time"]:
        elapsed_time = (datetime.now() - task["start_time"]).total_seconds()
        if task["completion"] > 0:
            estimated_time_remaining = int((elapsed_time / task["completion"]) * (1.0 - task["completion"]))
    
    return StatusResponse(
        request_id=request_id,
        name=task["name"],
        status=task["status"],
        completion=task["completion"],
        estimated_time_remaining=estimated_time_remaining
    )


@app.get("/search/{request_id}/result", response_model=SearchResultResponse, dependencies=[Depends(get_api_key)])
async def get_search_result(request_id: str):
    """Get the result of a completed search task."""
    if request_id not in task_storage:
        raise HTTPException(status_code=404, detail="Search task not found")
    
    task = task_storage[request_id]
    
    if task["status"] != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"Search task is not completed. Current status: {task['status']}"
        )
    
    result = task["result"]
    
    return SearchResultResponse(
        request_id=request_id,
        name=result.name,
        status=task["status"],
        risk_level=result.risk_level,
        confidence_score=result.confidence_score,
        summary=result.summary,
        social_media_profiles={
            platform: [profile.to_dict() for profile in profiles]
            for platform, profiles in result.social_media_profiles.items()
        },
        pep_records=[record.to_dict() for record in result.pep_records],
        news_articles=[article.to_dict() for article in result.news_articles],
        sources_checked=list(result.sources_checked),
        sources_successful=list(result.sources_successful),
        errors=result.errors,
        timestamp=datetime.now()
    )


@app.get("/search/{request_id}/summary", dependencies=[Depends(get_api_key)])
async def get_search_summary(request_id: str):
    """Get a summary of a completed search task."""
    if request_id not in task_storage:
        raise HTTPException(status_code=404, detail="Search task not found")
    
    task = task_storage[request_id]
    
    if task["status"] != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"Search task is not completed. Current status: {task['status']}"
        )
    
    result = task["result"]
    
    return SearchResponse(
        request_id=request_id,
        name=result.name,
        status=task["status"],
        risk_level=result.risk_level,
        confidence_score=result.confidence_score,
        summary=result.summary,
        sources_checked=list(result.sources_checked),
        timestamp=datetime.now()
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)