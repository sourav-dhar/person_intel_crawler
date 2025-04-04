import { useState } from 'react';
import { PEPRecord } from '../../types/search';

interface PEPSectionProps {
  records: PEPRecord[];
}

const PEPSection = ({ records }: PEPSectionProps) => {
  const [expandedRecordIndex, setExpandedRecordIndex] = useState<number | null>(null);
  
  if (records.length === 0) {
    return (
      <div className="p-4 text-center text-gray-500">
        <p>No PEP (Politically Exposed Person) or sanctions records found.</p>
      </div>
    );
  }
  
  const getRiskBadgeClass = (riskLevel?: string) => {
    switch (riskLevel?.toLowerCase()) {
      case 'low':
        return 'bg-green-100 text-green-800';
      case 'medium':
        return 'bg-amber-100 text-amber-800';
      case 'high':
        return 'bg-red-100 text-red-800';
      case 'critical':
        return 'bg-red-200 text-red-900';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };
  
  const getSourceIcon = (source: string) => {
    switch (source.toLowerCase()) {
      case 'opensanctions':
        return 'fas fa-globe text-blue-600';
      case 'worldcheck':
        return 'fas fa-search-dollar text-green-600';
      case 'dowjones':
        return 'fas fa-newspaper text-indigo-600';
      case 'ofac':
        return 'fas fa-landmark text-red-600';
      case 'un_sanctions':
      case 'eu_sanctions':
        return 'fas fa-gavel text-amber-600';
      default:
        return 'fas fa-database text-gray-600';
    }
  };
  
  return (
    <div className="p-4">
      <div className="mb-4 bg-amber-50 border border-amber-200 rounded-md p-4">
        <h3 className="text-amber-800 font-medium mb-2">About PEP & Sanctions Data</h3>
        <p className="text-sm text-amber-700">
          PEP (Politically Exposed Person) status indicates individuals who hold prominent public functions. 
          Sanctions lists contain individuals or entities subject to economic or legal restrictions. 
          Presence on these lists does not automatically indicate wrongdoing.
        </p>
      </div>
      
      <div className="space-y-4">
        {records.map((record, index) => (
          <div
            key={`${record.source}-${record.name}-${index}`}
            className="bg-white border border-gray-200 rounded-lg overflow-hidden"
          >
            <div className="p-4 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
              <div className="flex items-center">
                <i className={`${getSourceIcon(record.source)} mr-3 text-xl`}></i>
                <div>
                  <h3 className="font-medium text-gray-900">{record.name}</h3>
                  <p className="text-sm text-gray-500">{record.source}</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                {record.risk_level && (
                  <span className={`text-xs px-2 py-1 rounded-full ${getRiskBadgeClass(record.risk_level)}`}>
                    {record.risk_level.toUpperCase()}
                  </span>
                )}
                <span className="bg-indigo-100 text-indigo-800 text-xs px-2 py-1 rounded-full">
                  Match: {Math.round(record.similarity_score * 100)}%
                </span>
                <button
                  className="text-gray-500 hover:text-gray-700"
                  onClick={() => setExpandedRecordIndex(expandedRecordIndex === index ? null : index)}
                  aria-label={expandedRecordIndex === index ? "Collapse details" : "Expand details"}
                >
                  <i className={`fas fa-chevron-${expandedRecordIndex === index ? 'up' : 'down'}`}></i>
                </button>
              </div>
            </div>
            
            {expandedRecordIndex === index && (
              <div className="p-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-4">
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-2">Position & Organization</h4>
                    <div className="text-sm text-gray-600 space-y-2">
                      {record.position ? (
                        <p>
                          <span className="font-medium">Position:</span> {record.position}
                        </p>
                      ) : (
                        <p className="text-gray-400">No position information available</p>
                      )}
                      
                      {record.organization ? (
                        <p>
                          <span className="font-medium">Organization:</span> {record.organization}
                        </p>
                      ) : (
                        <p className="text-gray-400">No organization information available</p>
                      )}
                      
                      {record.country ? (
                        <p>
                          <span className="font-medium">Country:</span> {record.country}
                        </p>
                      ) : (
                        <p className="text-gray-400">No country information available</p>
                      )}
                      
                      {(record.start_date || record.end_date) && (
                        <p>
                          <span className="font-medium">Time Period:</span>{' '}
                          {record.start_date ? new Date(record.start_date).toLocaleDateString() : 'Unknown'} 
                          {' to '}
                          {record.end_date ? new Date(record.end_date).toLocaleDateString() : 'Present'}
                        </p>
                      )}
                      
                      {record.is_active !== undefined && (
                        <p>
                          <span className="font-medium">Status:</span>{' '}
                          <span className={record.is_active ? 'text-green-600' : 'text-gray-600'}>
                            {record.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </p>
                      )}
                    </div>
                  </div>
                  
                  <div>
                    {record.sanctions && record.sanctions.length > 0 ? (
                      <div>
                        <h4 className="text-sm font-medium text-gray-700 mb-2">Sanctions</h4>
                        <ul className="text-sm text-gray-600 space-y-2 list-disc list-inside">
                          {record.sanctions.map((sanction, idx) => (
                            <li key={idx} className="text-red-700">
                              {sanction.name}
                              {sanction.date && <span className="text-gray-500"> ({sanction.date})</span>}
                            </li>
                          ))}
                        </ul>
                      </div>
                    ) : record.watchlists && record.watchlists.length > 0 ? (
                      <div>
                        <h4 className="text-sm font-medium text-gray-700 mb-2">Watchlists</h4>
                        <ul className="text-sm text-gray-600 space-y-2 list-disc list-inside">
                          {record.watchlists.map((watchlist, idx) => (
                            <li key={idx} className="text-amber-700">
                              {watchlist}
                            </li>
                          ))}
                        </ul>
                      </div>
                    ) : (
                      <div>
                        <h4 className="text-sm font-medium text-gray-700 mb-2">Sanctions & Watchlists</h4>
                        <p className="text-sm text-gray-500">No sanctions or watchlists listed</p>
                      </div>
                    )}
                  </div>
                </div>
                
                {record.related_entities && record.related_entities.length > 0 && (
                  <div className="mt-4">
                    <h4 className="text-sm font-medium text-gray-700 mb-2">Related Entities</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                      {record.related_entities.map((entity, idx) => (
                        <div key={idx} className="bg-gray-50 p-3 rounded-md text-sm">
                          <p className="font-medium">{entity.name}</p>
                          {entity.relationship && (
                            <p className="text-gray-600 text-xs">{entity.relationship}</p>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {record.url && (
                  <div className="mt-4 text-right">
                    <a
                      href={record.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-indigo-600 hover:text-indigo-800 text-sm font-medium"
                    >
                      View Source →
                    </a>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default PEPSection;