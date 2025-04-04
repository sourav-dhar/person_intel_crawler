import { useState } from 'react';
import { NewsArticle } from '../../types/search';
import { format } from 'date-fns';

interface MediaSectionProps {
  articles: NewsArticle[];
}

// Sort options
type SortOption = 'relevance' | 'date' | 'sentiment';

const MediaSection = ({ articles }: MediaSectionProps) => {
  const [sortBy, setSortBy] = useState<SortOption>('relevance');
  const [filterSentiment, setFilterSentiment] = useState<string | null>(null);
  const [expandedArticleIndex, setExpandedArticleIndex] = useState<number | null>(null);
  
  if (articles.length === 0) {
    return (
      <div className="p-4 text-center text-gray-500">
        <p>No media mentions found.</p>
      </div>
    );
  }
  
  // Sort articles based on selection
  const sortedArticles = [...articles].sort((a, b) => {
    if (sortBy === 'relevance') {
      return b.relevance_score - a.relevance_score;
    } else if (sortBy === 'date') {
      const dateA = a.published_date ? new Date(a.published_date).getTime() : 0;
      const dateB = b.published_date ? new Date(b.published_date).getTime() : 0;
      return dateB - dateA;
    } else if (sortBy === 'sentiment') {
      const sentimentOrder = { 'very_negative': 0, 'negative': 1, 'neutral': 2, 'positive': 3 };
      const sentA = a.sentiment ? sentimentOrder[a.sentiment as keyof typeof sentimentOrder] : 2;
      const sentB = b.sentiment ? sentimentOrder[b.sentiment as keyof typeof sentimentOrder] : 2;
      return sentA - sentB;
    }
    return 0;
  });
  
  // Filter articles by sentiment if filter is active
  const filteredArticles = filterSentiment
    ? sortedArticles.filter(article => article.sentiment === filterSentiment)
    : sortedArticles;
  
  // Get sentiment badge styling
  const getSentimentBadgeClass = (sentiment?: string) => {
    switch (sentiment) {
      case 'positive':
        return 'bg-green-100 text-green-800';
      case 'neutral':
        return 'bg-gray-100 text-gray-800';
      case 'negative':
        return 'bg-red-100 text-red-800';
      case 'very_negative':
        return 'bg-red-200 text-red-900';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };
  
  // Format sentiment text for display
  const formatSentiment = (sentiment?: string) => {
    if (!sentiment) return 'Unknown';
    return sentiment.charAt(0).toUpperCase() + sentiment.slice(1).replace('_', ' ');
  };
  
  // Get source icon
  const getSourceIcon = (source: string) => {
    const sourceLower = source.toLowerCase();
    if (sourceLower.includes('google')) return 'fab fa-google text-blue-500';
    if (sourceLower.includes('bing')) return 'fab fa-microsoft text-blue-600';
    if (sourceLower.includes('lexisnexis')) return 'fas fa-balance-scale text-purple-600';
    if (sourceLower.includes('factiva') || sourceLower.includes('dowjones')) return 'fas fa-newspaper text-indigo-600';
    return 'fas fa-newspaper text-gray-600';
  };
  
  // Get sentiment counts for filter badges
  const sentimentCounts = articles.reduce(
    (acc, article) => {
      if (article.sentiment) {
        acc[article.sentiment] = (acc[article.sentiment] || 0) + 1;
      }
      return acc;
    },
    {} as Record<string, number>
  );
  
  return (
    <div className="p-4">
      <div className="mb-6 flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
        {/* Sorting options */}
        <div className="flex items-center space-x-3">
          <span className="text-sm text-gray-700">Sort by:</span>
          <div className="flex border border-gray-300 rounded-md overflow-hidden">
            <button
              className={`px-3 py-1.5 text-sm ${
                sortBy === 'relevance' ? 'bg-indigo-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
              onClick={() => setSortBy('relevance')}
            >
              Relevance
            </button>
            <button
              className={`px-3 py-1.5 text-sm border-l border-gray-300 ${
                sortBy === 'date' ? 'bg-indigo-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
              onClick={() => setSortBy('date')}
            >
              Date
            </button>
            <button
              className={`px-3 py-1.5 text-sm border-l border-gray-300 ${
                sortBy === 'sentiment' ? 'bg-indigo-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
              onClick={() => setSortBy('sentiment')}
            >
              Sentiment
            </button>
          </div>
        </div>
        
        {/* Sentiment filters */}
        <div className="flex flex-wrap gap-2">
          <button
            className={`px-2 py-1 rounded-md text-xs font-medium ${
              filterSentiment === null ? 'bg-gray-800 text-white' : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
            }`}
            onClick={() => setFilterSentiment(null)}
          >
            All ({articles.length})
          </button>
          
          {Object.entries(sentimentCounts).map(([sentiment, count]) => (
            <button
              key={sentiment}
              className={`px-2 py-1 rounded-md text-xs font-medium ${
                filterSentiment === sentiment
                  ? 'ring-2 ring-offset-2 ring-gray-500'
                  : ''
              } ${getSentimentBadgeClass(sentiment)}`}
              onClick={() => setFilterSentiment(sentiment === filterSentiment ? null : sentiment)}
            >
              {formatSentiment(sentiment)} ({count})
            </button>
          ))}
        </div>
      </div>
      
      <div className="space-y-4">
        {filteredArticles.length === 0 ? (
          <div className="text-center text-gray-500 py-4">
            <p>No articles match the current filter.</p>
          </div>
        ) : (
          filteredArticles.map((article, index) => (
            <div
              key={`${article.source}-${index}`}
              className="bg-white border border-gray-200 rounded-lg overflow-hidden"
            >
              <div className="p-4 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
                <div className="flex items-start">
                  <i className={`${getSourceIcon(article.source)} mt-1 mr-3 text-xl`}></i>
                  <div>
                    <h3 className="font-medium text-gray-900">{article.title}</h3>
                    <div className="flex flex-wrap items-center text-sm text-gray-500 mt-1 gap-x-4">
                      <span>{article.source}</span>
                      {article.published_date && (
                        <span>
                          {format(new Date(article.published_date), 'MMM d, yyyy')}
                        </span>
                      )}
                      {article.authors && article.authors.length > 0 && (
                        <span>By: {article.authors.join(', ')}</span>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {article.sentiment && (
                    <span className={`text-xs px-2 py-1 rounded-full ${getSentimentBadgeClass(article.sentiment)}`}>
                      {formatSentiment(article.sentiment)}
                    </span>
                  )}
                  <span className="bg-indigo-100 text-indigo-800 text-xs px-2 py-1 rounded-full">
                    Match: {Math.round(article.relevance_score * 100)}%
                  </span>
                  <button
                    className="text-gray-500 hover:text-gray-700"
                    onClick={() => setExpandedArticleIndex(expandedArticleIndex === index ? null : index)}
                    aria-label={expandedArticleIndex === index ? "Collapse details" : "Expand details"}
                  >
                    <i className={`fas fa-chevron-${expandedArticleIndex === index ? 'up' : 'down'}`}></i>
                  </button>
                </div>
              </div>
              
              {expandedArticleIndex === index && (
                <div className="p-4">
                  {article.summary ? (
                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-gray-700 mb-2">Summary</h4>
                      <p className="text-sm text-gray-600">{article.summary}</p>
                    </div>
                  ) : article.content ? (
                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-gray-700 mb-2">Content</h4>
                      <p className="text-sm text-gray-600">{article.content}</p>
                    </div>
                  ) : null}
                  
                  {article.keywords && article.keywords.length > 0 && (
                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-gray-700 mb-2">Keywords</h4>
                      <div className="flex flex-wrap gap-2">
                        {article.keywords.map((keyword, kidx) => (
                          <span
                            key={kidx}
                            className="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded-full"
                          >
                            {keyword}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {article.entities && article.entities.length > 0 && (
                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-gray-700 mb-2">Entities</h4>
                      <div className="flex flex-wrap gap-2">
                        {article.entities
                          .filter(entity => ['PERSON', 'ORG', 'GPE', 'LOC'].includes(entity.label))
                          .slice(0, 10)
                          .map((entity, eidx) => (
                            <span
                              key={eidx}
                              className={`text-xs px-2 py-1 rounded-full ${
                                entity.label === 'PERSON'
                                  ? 'bg-blue-100 text-blue-800'
                                  : entity.label === 'ORG'
                                  ? 'bg-purple-100 text-purple-800'
                                  : entity.label === 'GPE' || entity.label === 'LOC'
                                  ? 'bg-green-100 text-green-800'
                                  : 'bg-gray-100 text-gray-800'
                              }`}
                            >
                              <span className="font-semibold">{entity.label}:</span> {entity.text}
                            </span>
                          ))}
                      </div>
                    </div>
                  )}
                  
                  {article.url && (
                    <div className="mt-4 text-right">
                      <a
                        href={article.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-indigo-600 hover:text-indigo-800 text-sm font-medium"
                      >
                        Read Full Article →
                      </a>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default MediaSection;