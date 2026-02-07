import { useState, useEffect } from 'react';
import { AlertCircle, CheckCircle, AlertTriangle, ChevronDown, ChevronUp, Loader2, Settings } from 'lucide-react';

// ============================================================
// API HELPERS — all AI logic lives in the Python backend
// ============================================================

const API_BASE = '/api';

async function fetchStatus() {
  const res = await fetch(`${API_BASE}/status`);
  return res.json();
}

async function fetchPersonas() {
  const res = await fetch(`${API_BASE}/personas`);
  return res.json();
}

async function fetchExamplePolicies() {
  const res = await fetch(`${API_BASE}/example-policies`);
  return res.json();
}

async function testPolicyApi(policyText, categories, model) {
  const res = await fetch(`${API_BASE}/test-policy`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      policy_text: policyText,
      categories,
      model,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(err.detail || 'Request failed');
  }
  return res.json();
}

// ============================================================
// MAIN COMPONENT
// ============================================================

function App() {
  // Data from the Python backend
  const [personas, setPersonas] = useState({});
  const [examplePolicies, setExamplePolicies] = useState({});

  // UI state
  const [policyText, setPolicyText] = useState('');
  const [selectedCategories, setSelectedCategories] = useState([]);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [expandedResults, setExpandedResults] = useState({});

  // Ollama settings
  const [ollamaModel, setOllamaModel] = useState('');
  const [showSettings, setShowSettings] = useState(false);
  const [ollamaConnected, setOllamaConnected] = useState(false);
  const [availableModels, setAvailableModels] = useState([]);

  // Load personas, policies, and check status on mount
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [status, personaData, policyData] = await Promise.all([
        fetchStatus(),
        fetchPersonas(),
        fetchExamplePolicies(),
      ]);

      setOllamaConnected(status.connected);
      setAvailableModels(status.models);
      setOllamaModel(status.default_model);

      setPersonas(personaData);
      setSelectedCategories(Object.keys(personaData));

      setExamplePolicies(policyData);
    } catch (err) {
      console.error('Failed to load initial data:', err);
    }
  };

  const checkOllamaConnection = async () => {
    try {
      const status = await fetchStatus();
      setOllamaConnected(status.connected);
      setAvailableModels(status.models);
      if (status.models.length > 0 && !status.models.includes(ollamaModel)) {
        setOllamaModel(status.default_model);
      }
    } catch {
      setOllamaConnected(false);
      setAvailableModels([]);
    }
  };

  // Toggle category selection
  const handleCategoryToggle = (category) => {
    setSelectedCategories(prev =>
      prev.includes(category)
        ? prev.filter(c => c !== category)
        : [...prev, category]
    );
  };

  // Load an example policy into the textarea
  const loadExamplePolicy = (policyKey) => {
    setPolicyText(examplePolicies[policyKey].text);
  };

  // ============================================================
  // CORE FUNCTION: Test policy via Python backend
  // ============================================================
  const testPolicy = async () => {
    if (!policyText.trim()) {
      alert('Please enter a policy to test');
      return;
    }

    if (selectedCategories.length === 0) {
      alert('Please select at least one category');
      return;
    }

    if (!ollamaConnected) {
      alert('Ollama is not connected. Check the settings panel.');
      return;
    }

    setLoading(true);
    setResults(null);

    try {
      const data = await testPolicyApi(policyText, selectedCategories, ollamaModel);
      setResults(data.results || []);
    } catch (error) {
      console.error('Error:', error);
      alert('Error testing policy: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // Toggle expanded state for a result card
  const toggleExpanded = (index) => {
    setExpandedResults(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  // Get the appropriate icon for each result status
  const getStatusIcon = (status) => {
    switch (status) {
      case 'CONFLICT':
      case 'UNINTENDED_CONSEQUENCE':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      case 'GAP':
        return <AlertTriangle className="w-5 h-5 text-amber-500" />;
      case 'STRENGTH':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      default:
        return <AlertCircle className="w-5 h-5 text-gray-500" />;
    }
  };

  // Get background color for result cards
  const getStatusBg = (status) => {
    switch (status) {
      case 'CONFLICT':
      case 'UNINTENDED_CONSEQUENCE':
        return 'bg-red-50 border-red-200';
      case 'GAP':
        return 'bg-amber-50 border-amber-200';
      case 'STRENGTH':
        return 'bg-green-50 border-green-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  // Calculate summary statistics
  const getSummaryStats = () => {
    if (!results) return null;
    return {
      conflicts: results.filter(r => r.status === 'CONFLICT' || r.status === 'UNINTENDED_CONSEQUENCE').length,
      gaps: results.filter(r => r.status === 'GAP').length,
      strengths: results.filter(r => r.status === 'STRENGTH').length
    };
  };

  const stats = getSummaryStats();

  // ============================================================
  // RENDER
  // ============================================================
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-[#1d70b8] text-white py-6 px-6">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Policy Tester Interface</h1>
            <p className="text-blue-100 mt-1">Test draft parole policies against lived experience scenarios</p>
          </div>
          <div className="flex items-center gap-3">
            <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm ${ollamaConnected ? 'bg-green-500/20 text-green-100' : 'bg-red-500/20 text-red-100'}`}>
              <div className={`w-2 h-2 rounded-full ${ollamaConnected ? 'bg-green-400' : 'bg-red-400'}`} />
              {ollamaConnected ? `Ollama (${ollamaModel})` : 'Ollama disconnected'}
            </div>
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="p-2 rounded-lg hover:bg-white/10 transition-colors"
              title="Ollama Settings"
            >
              <Settings className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Ollama Settings */}
      {showSettings && (
        <div className="max-w-7xl mx-auto p-6">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <h3 className="font-semibold text-blue-800 mb-2">Ollama Settings</h3>
            <p className="text-sm text-blue-700 mb-3">
              Make sure Ollama is running locally. Start it with <code className="bg-blue-100 px-1 rounded">ollama serve</code> in your terminal.
            </p>
            <div className="flex gap-2 mb-3">
              <div className="flex-1">
                <label className="block text-xs font-medium text-blue-700 mb-1">Model</label>
                <select
                  value={ollamaModel}
                  onChange={(e) => setOllamaModel(e.target.value)}
                  className="w-full px-3 py-2 border border-blue-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                >
                  {availableModels.length > 0 ? (
                    availableModels.map(m => (
                      <option key={m} value={m}>{m}</option>
                    ))
                  ) : (
                    <option value={ollamaModel}>{ollamaModel}</option>
                  )}
                </select>
              </div>
              <div className="flex items-end">
                <button
                  onClick={checkOllamaConnection}
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
                >
                  Reconnect
                </button>
              </div>
            </div>
            {!ollamaConnected && (
              <p className="text-sm text-red-600">
                ⚠ Cannot connect to Ollama. Is it running?
              </p>
            )}
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-7xl mx-auto p-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

          {/* Left Panel - Policy Input */}
          <div className="space-y-4">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">Policy Text</h3>

              {/* Example Policy Buttons */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Load Example Policy:
                </label>
                <div className="flex gap-2 flex-wrap">
                  {Object.entries(examplePolicies).map(([key, policy]) => (
                    <button
                      key={key}
                      onClick={() => loadExamplePolicy(key)}
                      className="px-3 py-1 text-sm bg-blue-50 text-blue-700 rounded hover:bg-blue-100"
                    >
                      {policy.title}
                    </button>
                  ))}
                </div>
              </div>

              {/* Policy Textarea */}
              <textarea
                value={policyText}
                onChange={(e) => setPolicyText(e.target.value)}
                placeholder="Paste draft policy text here..."
                className="w-full h-64 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
              />

              {/* Category Checkboxes */}
              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Test Against Personas:
                </label>
                <div className="space-y-2">
                  {Object.entries(personas).map(([key, persona]) => (
                    <label key={key} className="flex items-start space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={selectedCategories.includes(key)}
                        onChange={() => handleCategoryToggle(key)}
                        className="mt-1 w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                      />
                      <div>
                        <span className="text-sm font-medium">{persona.name}</span>
                        <span className="text-sm text-gray-500"> - {persona.category}</span>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              {/* Test Button */}
              <button
                onClick={testPolicy}
                disabled={loading || !ollamaConnected}
                className="w-full mt-6 bg-[#1d70b8] text-white py-3 px-4 rounded-lg font-semibold hover:bg-[#165a94] disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    Analyzing Policy...
                  </>
                ) : (
                  'Test Policy'
                )}
              </button>
            </div>

            {/* Persona Details (collapsible) */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">Persona Details</h3>
              <div className="space-y-4">
                {selectedCategories.map(key => {
                  const persona = personas[key];
                  if (!persona) return null;
                  return (
                    <div key={key} className="border-l-4 border-blue-500 pl-4">
                      <h4 className="font-medium">{persona.name} - {persona.category}</h4>
                      <p className="text-sm text-gray-600 mt-1">{persona.scenario}</p>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Right Panel - Results */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Analysis Results</h3>

            {!results && !loading && (
              <div className="text-center text-gray-500 py-12">
                <AlertCircle className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                <p>Enter a policy and click "Test Policy" to see results</p>
              </div>
            )}

            {loading && (
              <div className="text-center py-12">
                <Loader2 className="w-12 h-12 mx-auto mb-4 text-blue-500 animate-spin" />
                <p className="text-gray-600">Analyzing policy against lived experience scenarios...</p>
              </div>
            )}

            {results && (
              <>
                {/* Summary Stats */}
                <div className="grid grid-cols-3 gap-4 mb-6">
                  <div className="bg-red-50 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-red-600">{stats.conflicts}</div>
                    <div className="text-sm text-red-700">Conflicts</div>
                  </div>
                  <div className="bg-amber-50 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-amber-600">{stats.gaps}</div>
                    <div className="text-sm text-amber-700">Gaps</div>
                  </div>
                  <div className="bg-green-50 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-green-600">{stats.strengths}</div>
                    <div className="text-sm text-green-700">Strengths</div>
                  </div>
                </div>

                {/* Result Cards */}
                <div className="space-y-3">
                  {results.map((result, index) => (
                    <div
                      key={index}
                      className={`border rounded-lg p-4 ${getStatusBg(result.status)}`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-start space-x-3 flex-1">
                          {getStatusIcon(result.status)}
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-xs font-semibold px-2 py-1 bg-white rounded">
                                {result.category}
                              </span>
                              <span className="text-xs text-gray-600">{result.persona}</span>
                            </div>
                            <h4 className="font-semibold text-sm mb-1">{result.status.replace(/_/g, ' ')}</h4>
                            <p className="text-sm text-gray-700">{result.issue}</p>

                            {expandedResults[index] && (
                              <div className="mt-3 pt-3 border-t border-gray-200">
                                <p className="text-sm text-gray-700 mb-3">{result.explanation}</p>
                                <div className="bg-white rounded p-3">
                                  <p className="text-xs font-semibold text-gray-600 mb-1">Recommendation:</p>
                                  <p className="text-sm text-gray-800">{result.recommendation}</p>
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                        <button
                          onClick={() => toggleExpanded(index)}
                          className="ml-2 text-gray-400 hover:text-gray-600"
                        >
                          {expandedResults[index] ? (
                            <ChevronUp className="w-5 h-5" />
                          ) : (
                            <ChevronDown className="w-5 h-5" />
                          )}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="bg-gray-100 py-4 px-6 mt-12">
        <div className="max-w-7xl mx-auto text-center text-sm text-gray-600">
          Policy Tester Interface - Built for Justice AI Hackathon 2026
        </div>
      </div>
    </div>
  );
}

export default App;
