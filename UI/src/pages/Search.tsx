import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../hooks/redux';
import { startSearch } from '../store/searchSlice';

// Components
import SearchForm from '../components/search/SearchForm';
import SearchOptions from '../components/search/SearchOptions';
import LoadingSpinner from '../components/common/LoadingSpinner';

// Types
import { SearchRequest } from '../types/search';

const Search = () => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const { loading, error } = useAppSelector((state) => state.search);
  
  const [searchData, setSearchData] = useState<SearchRequest>({
    name: '',
    include_social_media: true,
    include_pep: true,
    include_adverse_media: true,
    output_format: 'json',
    save_results: false
  });
  
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    
    if (type === 'checkbox') {
      const checkbox = e.target as HTMLInputElement;
      setSearchData({
        ...searchData,
        [name]: checkbox.checked
      });
    } else {
      setSearchData({
        ...searchData,
        [name]: value
      });
    }
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const result = await dispatch(startSearch(searchData)).unwrap();
      navigate(`/results/${result.request_id}`);
    } catch (err) {
      console.error('Failed to start search:', err);
    }
  };
  
  return (
    <div className="py-6">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-gray-900">New Search</h1>
        <p className="mt-1 text-sm text-gray-500">
          Enter a name to search for information across various sources.
        </p>
      </div>
      
      {error && (
        <div className="mb-4 p-4 bg-red-50 text-red-700 rounded-md">
          Error: {error}
        </div>
      )}
      
      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <SearchForm 
          searchData={searchData}
          handleInputChange={handleInputChange}
          handleSubmit={handleSubmit}
          loading={loading}
        />
      </div>
      
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Search Options</h2>
        <SearchOptions 
          searchData={searchData}
          handleInputChange={handleInputChange}
        />
      </div>
      
      {loading && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-xl max-w-md w-full">
            <LoadingSpinner size="lg" />
            <p className="text-center mt-4 text-gray-700">
              Starting search... This may take a moment.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Search;