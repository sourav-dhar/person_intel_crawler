import { useMemo, useState } from 'react';

interface SourcesSectionProps {
  sources: string[];
  successful: string[];
}

interface SourceInfo {
  id: string;
  type: string;
  name: string;
  success: boolean;
}

const SourcesSection = ({ sources, successful }: SourcesSectionProps) => {
  const [activeFilter, setActiveFilter] = useState<string | null>(null);
  
  // Process sources into a structured format
  const processedSources = useMemo(() => {
    return sources.map(source => {
      const [type, name] = source.split(':');
      return {
        id: source,
        type,
        name,
        success: successful.includes(source)
      };
    });
  }, [sources, successful]);
  
  // Get unique types for filtering
  const sourceTypes = useMemo(() => {
    return Array.from(new Set(processedSources.map(source => source.type)));
  }, [processedSources]);
  
  // Filter sources based on active filter
  const filteredSources = useMemo(() => {
    if (!activeFilter) return processedSources;
    return processedSources.filter(source => source.type === activeFilter);
  }, [processedSources, activeFilter]);
  
  // Count success/fail by type
  const typeSummary = useMemo(() => {
    return sourceTypes.map(type => {
      const typeSourcesCount = processedSources.filter(source => source.type === type).length;
      const typeSuccessCount = processedSources.filter(
        source => source.type === type && source.success
      ).length;
      return {
        type,
        total: typeSourcesCount,
        success: typeSuccessCount,
        failure: typeSourcesCount - typeSuccessCount,
        successRate: typeSourcesCount > 0 ? (typeSuccessCount / typeSourcesCount) * 100 : 0
      };
    });
  }, [processedSources, sourceTypes]);
  
  // Get icon for source type
  const getSourceTypeIcon = (type: string) => {
    switch (type) {
      case 'social':
        return 'fas fa-users text-blue-500';
      case 'pep':
        return 'fas fa-shield-alt text-amber-500';
      case 'media':
        return 'fas fa-newspaper text-purple-500';
      default:
        return 'fas fa-database text-gray-500';
    }
  };
  
  // Get icon for specific source
  const getSourceIcon = (sourceType: string, sourceName: string) => {
    if (sourceType === 'social') {
      switch (sourceName) {
        case 'twitter':
          return 'fab fa-twitter text-blue-400';
        case 'linkedin':
          return 'fab fa-linkedin text-blue-700';
        case 'facebook':
          return 'fab fa-facebook text-blue-600';
        case 'instagram':
          return 'fab fa-instagram text-pink-600';
        case 'tiktok':
          return 'fab fa-tiktok text-black';
        case 'youtube':
          return 'fab fa-youtube text-red-600';
        case 'reddit':
          return 'fab fa-reddit text-orange-600';
        case 'github':
          return 'fab fa-github text-gray-800';
        default:
          return 'fas fa-share-alt text-gray-500';
      }
    } else if (sourceType === 'pep') {
      switch (sourceName) {
        case 'opensanctions':
          return 'fas fa-globe text-blue-600';
        case 'worldcheck':
          return 'fas fa-search-dollar text-green-600';
        case 'dowjones':
          return 'fas fa-newspaper text-indigo-600';
        case 'ofac':
          return 'fas fa-landmark text-red-600';
        case 'un_sanctions':
          return 'fas fa-gavel text-amber-600';
        case 'eu_sanctions':
          return 'fas fa-gavel text-amber-600';
        default:
          return 'fas fa-database text-gray-600';
      }
    } else if (sourceType === 'media') {
      switch (sourceName) {
        case 'google_news':
          return 'fab fa-google text-blue-500';
        case 'bing_news':
          return 'fab fa-microsoft text-blue-600';
        case 'lexisnexis':
          return 'fas fa-balance-scale text-purple-600';
        case 'factiva':
          return 'fas fa-newspaper text-indigo-600';
        default:
          return 'fas fa-newspaper text-gray-600';
      }
    }
    return 'fas fa-question text-gray-500';
  };
  
  // Format source name for display
  const formatSourceName = (name: string) => {
    return name
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };
  
  if (sources.length === 0) {
    return (
      <div className="p-4 text-center text-gray-500">
        <p>No source information available.</p>
      </div>
    );
  }
  
  return (
    <div className="p-4">
      <div className="mb-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Source Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {typeSummary.map(summary => (
            <div
              key={summary.type}
              className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => setActiveFilter(activeFilter === summary.type ? null : summary.type)}
            >
              <div className="flex items-center mb-3">
                <i className={`${getSourceTypeIcon(summary.type)} mr-2 text-xl`}></i>
                <h4 className="text-gray-900 font-medium capitalize">{summary.type} Sources</h4>
              </div>
              <div className="flex justify-between items-center">
                <div>
                  <p className="text-gray-500 text-sm">Successful: {summary.success}/{summary.total}</p>
                  <p className="text-gray-500 text-sm">Success Rate: {summary.successRate.toFixed(0)}%</p>
                </div>
                <div className="h-10 w-10 rounded-full flex items-center justify-center">
                  <svg viewBox="0 0 36 36" className="h-10 w-10">
                    <path
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      fill="none"
                      stroke="#E5E7EB"
                      strokeWidth="3"
                      strokeDasharray="100, 100"
                    />
                    <path
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      fill="none"
                      stroke={summary.successRate >= 75 ? '#10B981' : summary.successRate >= 50 ? '#F59E0B' : '#EF4444'}
                      strokeWidth="3"
                      strokeDasharray={`${summary.successRate}, 100`}
                    />
                    <text x="18" y="20.5" textAnchor="middle" fontSize="10" fill="gray">
                      {summary.successRate.toFixed(0)}%
                    </text>
                  </svg>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      <div className="mb-4 flex flex-wrap gap-2">
        <button
          className={`px-3 py-1.5 text-sm font-medium rounded-md ${
            activeFilter === null
              ? 'bg-gray-800 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
          onClick={() => setActiveFilter(null)}
        >
          All Sources ({sources.length})
        </button>
        
        {sourceTypes.map(type => (
          <button
            key={type}
            className={`px-3 py-1.5 text-sm font-medium rounded-md flex items-center ${
              activeFilter === type
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
            onClick={() => setActiveFilter(activeFilter === type ? null : type)}
          >
            <i className={`${getSourceTypeIcon(type)} mr-1.5`}></i>
            <span className="capitalize">{type}</span>
            <span className="ml-1.5 bg-white bg-opacity-20 text-xs px-1.5 py-0.5 rounded-full">
              {processedSources.filter(source => source.type === type).length}
            </span>
          </button>
        ))}
      </div>
      
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Source
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Type
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredSources.map(source => (
              <tr key={source.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <i className={`${getSourceIcon(source.type, source.name)} mr-3 text-lg`}></i>
                    <div className="text-sm font-medium text-gray-900">
                      {formatSourceName(source.name)}
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-500 capitalize">{source.type}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    source.success
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {source.success ? 'Success' : 'Failed'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default SourcesSection;