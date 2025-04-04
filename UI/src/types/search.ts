export interface SearchRequest {
    name: string;
    include_social_media: boolean;
    include_pep: boolean;
    include_adverse_media: boolean;
    output_format: string;
    save_results: boolean;
    output_path?: string;
  }
  
  export interface SearchResponse {
    request_id: string;
    name: string;
    status: string;
    risk_level: string;
    confidence_score: number;
    summary: string;
    sources_checked: string[];
    timestamp: string;
  }
  
  export interface SearchStatus {
    request_id: string;
    name: string;
    status: string;
    completion: number;
    estimated_time_remaining?: number;
  }
  
  export interface SearchSummary {
    request_id: string;
    name: string;
    status: string;
    risk_level: string;
    timestamp: string;
  }
  
  export interface SocialMediaProfile {
    platform: string;
    username: string;
    url?: string;
    display_name?: string;
    bio?: string;
    follower_count?: number;
    following_count?: number;
    post_count?: number;
    is_verified: boolean;
    profile_image_url?: string;
    location?: string;
    joined_date?: string;
    last_active_date?: string;
    relevance_score: number;
    posts: SocialMediaPost[];
    connections: SocialMediaConnection[];
  }
  
  export interface SocialMediaPost {
    text: string;
    url?: string;
    timestamp?: string;
    platform: string;
    sentiment?: string;
  }
  
  export interface SocialMediaConnection {
    username: string;
    url?: string;
    display_name?: string;
    relationship?: string;
  }
  
  export interface PEPRecord {
    source: string;
    name: string;
    url?: string;
    position?: string;
    organization?: string;
    country?: string;
    start_date?: string;
    end_date?: string;
    is_active?: boolean;
    sanctions: PEPSanction[];
    watchlists: string[];
    related_entities: RelatedEntity[];
    risk_level?: string;
    last_updated?: string;
    similarity_score: number;
  }
  
  export interface PEPSanction {
    name: string;
    date?: string;
    description?: string;
  }
  
  export interface RelatedEntity {
    name: string;
    relationship?: string;
    position?: string;
    organization?: string;
  }
  
  export interface NewsArticle {
    source: string;
    title: string;
    url: string;
    published_date?: string;
    authors: string[];
    content?: string;
    summary?: string;
    sentiment?: string;
    entities: Entity[];
    keywords: string[];
    language?: string;
    relevance_score: number;
  }
  
  export interface Entity {
    text: string;
    label: string;
    start: number;
    end: number;
  }
  
  export interface SearchResult {
    request_id: string;
    name: string;
    status: string;
    query_time: string;
    social_media_profiles: Record<string, SocialMediaProfile[]>;
    pep_records: PEPRecord[];
    news_articles: NewsArticle[];
    summary: string;
    risk_level: string;
    confidence_score: number;
    risk_justification?: string;
    sources_checked: string[];
    sources_successful: string[];
    errors: SearchError[];
    timestamp: string;
  }
  
  export interface SearchError {
    source: string;
    message: string;
    timestamp: string;
  }