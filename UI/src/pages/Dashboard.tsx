import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../hooks/redux';
import { fetchRecentSearches } from '../store/searchSlice';

// Components
import SearchStats from '../components/dashboard/SearchStats';
import RecentSearches from '../components/dashboard/RecentSearches';
import RiskDistribution from '../components/dashboard/RiskDistribution';
import DashboardCard from '../components/dashboard/DashboardCard';
import LoadingSpinner from '../components/common/LoadingSpinner';

// Icons
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';

const Dashboard = () => {
  const dispatch = useAppDispatch();
  const { recentSearches, loading, error } = useAppSelector((state) => state.search);
  
  useEffect(() => {
    dispatch(fetchRecentSearches());
  }, [dispatch]);
  
  if (loading && recentSearches.length === 0) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }
  
  return (
    <div className="py-6">
      <div className="mb-6 flex justify-between items-center">
        <h1 className="text-2xl font-semibold text-gray-900">Dashboard</h1>
        <Link
          to="/search"
          className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          <MagnifyingGlassIcon className="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
          New Search
        </Link>
      </div>
      
      {error && (
        <div className="mb-4 p-4 bg-red-50 text-red-700 rounded-md">
          Error loading dashboard data: {error}
        </div>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <SearchStats />
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <DashboardCard title="Recent Searches">
          <RecentSearches searches={recentSearches.slice(0, 5)} />
        </DashboardCard>
        
        <DashboardCard title="Risk Level Distribution">
          <RiskDistribution />
        </DashboardCard>
      </div>
      
      <div className="grid grid-cols-1 gap-6">
        <DashboardCard title="Activity Timeline">
          {/* Activity timeline component would go here */}
          <p className="text-gray-500 italic">Activity timeline visualization</p>
        </DashboardCard>
      </div>
    </div>
  );
};

export default Dashboard;