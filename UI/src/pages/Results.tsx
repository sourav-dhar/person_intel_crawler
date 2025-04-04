import { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../hooks/redux';
import { fetchSearchStatus, fetchSearchResult } from '../store/resultSlice';

// Components
import ResultSummary from '../components/results/ResultSummary';
import ResultTabs from '../components/results/ResultTabs';
import LoadingSpinner from '../components/common/LoadingSpinner';
import SearchProgress from '../components/results/SearchProgress';
import ErrorMessage from '../components/common/ErrorMessage';

const Results = () => {
  const { requestId } = useParams<{ requestId: string }>();
  const dispatch = useAppDispatch();
  const { status, result, loading, error } = useAppSelector((state) => state.result);
  
  useEffect(() => {
    if (!requestId) return;
    
    // Poll status until completed
    const pollInterval = setInterval(() => {
      dispatch(fetchSearchStatus(requestId));
      
      if (status?.status === 'completed') {
        clearInterval(pollInterval);
        dispatch(fetchSearchResult(requestId));
      }
    }, 3000);
    
    // Initial status fetch
    dispatch(fetchSearchStatus(requestId));
    
    return () => clearInterval(pollInterval);
  }, [dispatch, requestId, status?.status]);
  
  if (loading && !status) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }
  
  if (error) {
    return <ErrorMessage message={error} />;
  }
  
  if (!status) {
    return <ErrorMessage message="Search not found" />;
  }
  
  if (status.status !== 'completed') {
    return (
      <div className="py-6">
        <div className="mb-6">
          <h1 className="text-2xl font-semibold text-gray-900">
            Search for: {status.name}
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Search ID: {requestId}
          </p>
        </div>
        
        <div className="bg-white shadow rounded-lg p-6">
          <SearchProgress status={status} />
        </div>
      </div>
    );
  }
  
  if (!result) {
    return (
      <div className="py-6">
        <div className="mb-6">
          <h1 className="text-2xl font-semibold text-gray-900">
            Search completed for: {status.name}
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Loading results...
          </p>
        </div>
        
        <div className="flex justify-center items-center h-64">
          <LoadingSpinner size="lg" />
        </div>
      </div>
    );
  }
  
  return (
    <div className="py-6">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-gray-900">
          Results: {result.name}
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          Search ID: {result.request_id}
        </p>
      </div>
      
      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <ResultSummary result={result} />
      </div>
      
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <ResultTabs result={result} />
      </div>
    </div>
  );
};

export default Results;