import { useState } from 'react';
import { SearchResult } from '../../types/search';

interface RawDataSectionProps {
  result: SearchResult;
}

const RawDataSection = ({ result }: RawDataSectionProps) => {
  const [format, setFormat] = useState<'json' | 'pretty'>('pretty');
  const [copied, setCopied] = useState(false);
  
  // Prepare raw JSON
  const rawJson = JSON.stringify(result, null, 2);
  
  // Copy to clipboard
  const handleCopy = () => {
    navigator.clipboard.writeText(rawJson);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  
  // Download JSON file
  const handleDownload = () => {
    const blob = new Blob([rawJson], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `person-intel-${result.name.replace(/\s+/g, '_').toLowerCase()}-${new Date().toISOString().slice(0, 10)}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };
  
  return (
    <div className="p-4">
      <div className="mb-4 flex justify-between items-center">
        <div>
          <h3 className="text-lg font-medium text-gray-900">Raw Data</h3>
          <p className="text-sm text-gray-500">
            View and export the complete raw data for further analysis
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <div className="bg-gray-100 rounded-md p-1 flex items-center">
            <button
              className={`px-3 py-1 text-sm rounded-md ${
                format === 'pretty' ? 'bg-white shadow text-gray-800' : 'text-gray-500'
              }`}
              onClick={() => setFormat('pretty')}
            >
              Formatted
            </button>
            <button
              className={`px-3 py-1 text-sm rounded-md ${
                format === 'json' ? 'bg-white shadow text-gray-800' : 'text-gray-500'
              }`}
              onClick={() => setFormat('json')}
            >
              Raw JSON
            </button>
          </div>
          
          <button
            className="text-gray-700 hover:text-gray-900 px-3 py-1.5 rounded-md border border-gray-300 text-sm font-medium flex items-center"
            onClick={handleCopy}
          >
            <i className={`fas fa-${copied ? 'check' : 'copy'} mr-1.5`}></i>
            {copied ? 'Copied!' : 'Copy'}
          </button>
          
          <button
            className="bg-indigo-600 text-white hover:bg-indigo-700 px-3 py-1.5 rounded-md text-sm font-medium flex items-center"
            onClick={handleDownload}
          >
            <i className="fas fa-download mr-1.5"></i>
            Download
          </button>
        </div>
      </div>
      
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 overflow-hidden">
        {format === 'pretty' ? (
          <div className="space-y-6">
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">Basic Information</h4>
              <div className="bg-white rounded-md border border-gray-200 p-3">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <div>
                    <span className="block text-xs text-gray-500">Name</span>
                    <span className="text-sm text-gray-900">{result.name}</span>
                  </div>
                  <div>
                    <span className="block text-xs text-gray-500">Risk Level</span>
                    <span className="text-sm text-gray-900">{result.risk_level.toUpperCase()}</span>
                  </div>
                  <div>
                    <span className="block text-xs text-gray-500">Confidence</span>
                    <span className="text-sm text-gray-900">{result.confidence_score.toFixed(2)}</span>
                  </div>
                  <div>
                    <span className="block text-xs text-gray-500">Query Time</span>
                    <span className="text-sm text-gray-900">{new Date(result.query_time).toLocaleString()}</span>
                  </div>
                  <div>
                    <span className="block text-xs text-gray-500">Sources Checked</span>
                    <span className="text-sm text-gray-900">{result.sources_checked.length}</span>
                  </div>
                  <div>
                    <span className="block text-xs text-gray-500">Sources Successful</span>
                    <span className="text-sm text-gray-900">{result.sources_successful.length}</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">Data Overview</h4>
              <div className="bg-white rounded-md border border-gray-200 p-3">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <span className="block text-xs text-gray-500">Social Media Profiles</span>
                    <span className="text-sm text-gray-900">
                      {Object.values(result.social_media_profiles || {}).flat().length} profiles 
                      across {Object.keys(result.social_media_profiles || {}).length} platforms
                    </span>
                  </div>
                  <div>
                    <span className="block text-xs text-gray-500">PEP Records</span>
                    <span className="text-sm text-gray-900">
                      {(result.pep_records || []).length} records
                    </span>
                  </div>
                  <div>
                    <span className="block text-xs text-gray-500">News Articles</span>
                    <span className="text-sm text-gray-900">
                      {(result.news_articles || []).length} articles
                    </span>
                  </div>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">Summary</h4>
              <div className="bg-white rounded-md border border-gray-200 p-3">
                <p className="text-sm text-gray-600 whitespace-pre-line">{result.summary}</p>
              </div>
            </div>
            
            {result.errors && result.errors.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">Errors</h4>
                <div className="bg-white rounded-md border border-gray-200 p-3">
                  <ul className="list-disc list-inside text-sm text-red-600 space-y-1">
                    {result.errors.map((error, index) => (
                      <li key={index}>
                        <span className="font-medium">{error.source}:</span> {error.message} 
                        ({new Date(error.timestamp).toLocaleString()})
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>
        ) : (
          <pre className="text-sm text-gray-800 overflow-auto p-2 h-96 whitespace-pre">
            {rawJson}
          </pre>
        )}
      </div>
    </div>
  );
};

export default RawDataSection;