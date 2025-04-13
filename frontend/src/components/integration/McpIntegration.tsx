import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Button } from '../ui/Button';

interface McpIntegrationProps {
  className?: string;
}

interface AgentCapability {
  name: string;
  capabilities: string[];
}

const McpIntegration: React.FC<McpIntegrationProps> = ({ className = '' }) => {
  const { isAuthenticated } = useAuth();
  const token = localStorage.getItem('auth_token');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [capabilities, setCapabilities] = useState<Record<string, string[]> | null>(null);
  const [queryResult, setQueryResult] = useState<any>(null);
  const [query, setQuery] = useState<string>('');

  const fetchCapabilities = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/mcp/capabilities', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error(`Error fetching capabilities: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      if (data.status === 'error') {
        throw new Error(data.message || 'Unknown error');
      }
      
      setCapabilities(data.capabilities);
    } catch (err: any) {
      setError(err.message || 'An error occurred while fetching capabilities');
      console.error('Error fetching capabilities:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleQuerySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!query.trim()) {
      setError('Please enter a query');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/mcp/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          query: query,
          context_preferences: {
            allocation: {
              global: 0.2,
              task: 0.5,
              conversation: 0.3
            }
          }
        })
      });
      
      if (!response.ok) {
        throw new Error(`Error submitting query: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error || 'Unknown error');
      }
      
      setQueryResult(data);
    } catch (err: any) {
      setError(err.message || 'An error occurred while submitting query');
      console.error('Error submitting query:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`p-6 bg-white rounded-lg shadow-md ${className}`}>
      <h2 className="text-2xl font-bold mb-4">Enhanced RAG Integration</h2>
      <p className="mb-6 text-gray-600">
        This panel demonstrates the enhanced RAG capabilities provided by the agentic RAG system.
      </p>
      
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-2">Agent Capabilities</h3>
        <Button 
          onClick={fetchCapabilities}
          disabled={loading}
          className="mb-4"
        >
          {loading ? 'Loading...' : 'Fetch Agent Capabilities'}
        </Button>
        
        {error && (
          <div className="p-3 bg-red-100 text-red-700 rounded-md mb-4">
            {error}
          </div>
        )}
        
        {capabilities && (
          <div className="bg-gray-50 p-4 rounded-md">
            <h4 className="font-medium mb-2">Available Agents:</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(capabilities).map(([agent, caps]) => (
                <div key={agent} className="border p-3 rounded-md">
                  <h5 className="font-semibold capitalize">{agent}</h5>
                  <ul className="list-disc pl-5 mt-2">
                    {caps.map((capability, index) => (
                      <li key={index} className="text-sm text-gray-600">
                        {capability}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
      
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-2">Query with Enhanced Context</h3>
        <form onSubmit={handleQuerySubmit}>
          <div className="mb-4">
            <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-1">
              Query
            </label>
            <input
              type="text"
              id="query"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter your query..."
            />
          </div>
          
          <Button 
            type="submit"
            disabled={loading}
          >
            {loading ? 'Submitting...' : 'Submit Query'}
          </Button>
        </form>
        
        {queryResult && (
          <div className="mt-4 bg-gray-50 p-4 rounded-md">
            <h4 className="font-medium mb-2">Result:</h4>
            <div className="mb-2">
              <span className="font-semibold">Answer:</span>
              <p className="mt-1 text-gray-700">{queryResult.answer}</p>
            </div>
            
            {queryResult.sources && queryResult.sources.length > 0 && (
              <div className="mb-2">
                <span className="font-semibold">Sources:</span>
                <ul className="list-disc pl-5 mt-1">
                  {queryResult.sources.map((source: any, index: number) => (
                    <li key={index} className="text-sm text-gray-600">
                      {source.id} (Relevance: {source.relevance_score.toFixed(2)})
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {queryResult.confidence && (
              <div className="mb-2">
                <span className="font-semibold">Confidence:</span>
                <p className="mt-1 text-gray-700">{(queryResult.confidence * 100).toFixed(1)}%</p>
              </div>
            )}
            
            {queryResult.context_usage && (
              <div className="mb-2">
                <span className="font-semibold">Context Usage:</span>
                <pre className="mt-1 text-xs bg-gray-100 p-2 rounded overflow-x-auto">
                  {JSON.stringify(queryResult.context_usage, null, 2)}
                </pre>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default McpIntegration;
