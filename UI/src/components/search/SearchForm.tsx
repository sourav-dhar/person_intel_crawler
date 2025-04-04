import { SearchRequest } from '../../types/search';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';

interface SearchFormProps {
  searchData: SearchRequest;
  handleInputChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  handleSubmit: (e: React.FormEvent) => void;
  loading: boolean;
}

const SearchForm = ({
  searchData,
  handleInputChange,
  handleSubmit,
  loading
}: SearchFormProps) => {
  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-700">
          Name to Search
        </label>
        <div className="mt-1 relative rounded-md shadow-sm">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
          </div>
          <input
            type="text"
            name="name"
            id="name"
            value={searchData.name}
            onChange={handleInputChange}
            className="focus:ring-indigo-500 focus:border-indigo-500 block w-full pl-10 pr-12 sm:text-sm border-gray-300 rounded-md"
            placeholder="Enter full name (e.g., John Smith)"
            required
          />
        </div>
        <p className="mt-2 text-sm text-gray-500">
          Enter the full name of the person you want to search for.
        </p>
      </div>
      
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center space-x-4">
          <div className="flex items-center">
            <input
              id="include_social_media"
              name="include_social_media"
              type="checkbox"
              checked={searchData.include_social_media}
              onChange={handleInputChange}
              className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
            />
            <label htmlFor="include_social_media" className="ml-2 block text-sm text-gray-700">
              Social Media
            </label>
          </div>
          
          <div className="flex items-center">
            <input
              id="include_pep"
              name="include_pep"
              type="checkbox"
              checked={searchData.include_pep}
              onChange={handleInputChange}
              className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
            />
            <label htmlFor="include_pep" className="ml-2 block text-sm text-gray-700">
              PEP Databases
            </label>
          </div>
          
          <div className="flex items-center">
            <input
              id="include_adverse_media"
              name="include_adverse_media"
              type="checkbox"
              checked={searchData.include_adverse_media}
              onChange={handleInputChange}
              className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
            />
            <label htmlFor="include_adverse_media" className="ml-2 block text-sm text-gray-700">
              Adverse Media
            </label>
          </div>
        </div>
        
        <button
          type="submit"
          disabled={loading || !searchData.name.trim()}
          className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <>
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Processing...
            </>
          ) : (
            <>
              <MagnifyingGlassIcon className="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
              Start Search
            </>
          )}
        </button>
      </div>
    </form>
  );
};

export default SearchForm;