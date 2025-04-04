import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Provider } from 'react-redux';
import { store } from './store';

// Components
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';

// Pages
import Dashboard from './pages/Dashboard';
import Search from './pages/Search';
import Results from './pages/Results';
import Login from './pages/Login';
import NotFound from './pages/NotFound';

// Styles
import './styles/tailwind.css';

const App = () => {
  return (
    <Provider store={store}>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          
          <Route path="/" element={<Layout />}>
            <Route index element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } />
            
            <Route path="search" element={
              <ProtectedRoute>
                <Search />
              </ProtectedRoute>
            } />
            
            <Route path="results/:requestId" element={
              <ProtectedRoute>
                <Results />
              </ProtectedRoute>
            } />
            
            <Route path="*" element={<NotFound />} />
          </Route>
        </Routes>
      </Router>
    </Provider>
  );
};

export default App;