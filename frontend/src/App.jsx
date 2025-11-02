import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'
import DatasetResults from './components/DatasetResults'
import AnalysisHistory from './components/AnalysisHistory'

const API_URL = 'http://localhost:8000'

function App() {
  const [files, setFiles] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [results, setResults] = useState(null)
  const [history, setHistory] = useState([])
  const [historyLoading, setHistoryLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('upload')

  const handleFileChange = (e) => {
    setFiles(e.target.files)
    setError(null)
  }

  const handleAnalyze = async () => {
    if (!files || files.length === 0) {
      setError('Please select at least one CSV file')
      return
    }

    setLoading(true)
    setError(null)
    setResults(null)

    try {
      const formData = new FormData()
      Array.from(files).forEach(file => {
        formData.append('files', file)
      })

      const response = await axios.post(`${API_URL}/analyze`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      setResults(response.data.results)
      // Refresh history after new analysis
      fetchHistory()
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred while analyzing the files')
    } finally {
      setLoading(false)
    }
  }

  const fetchHistory = async () => {
    setHistoryLoading(true)
    try {
      const response = await axios.get(`${API_URL}/history`)
      setHistory(response.data.analyses)
    } catch (err) {
      console.error('Error fetching history:', err)
    } finally {
      setHistoryLoading(false)
    }
  }

  const handleDeleteHistory = async (analysisId) => {
    try {
      await axios.delete(`${API_URL}/history/${analysisId}`)
      // Refresh history after deletion
      fetchHistory()
    } catch (err) {
      console.error('Error deleting analysis:', err)
      alert('Failed to delete analysis')
    }
  }

  // Fetch history on component mount
  useEffect(() => {
    fetchHistory()
  }, [])

  return (
    <div className="app">
      <header className="header">
        <h1>Data Quality Dashboard</h1>
        <p>Comprehensive data quality analysis for CSV files</p>
      </header>

      <div className="container">
        <div className="tabs">
          <button
            className={`tab ${activeTab === 'upload' ? 'active' : ''}`}
            onClick={() => setActiveTab('upload')}
          >
            New Analysis
          </button>
          <button
            className={`tab ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveTab('history')}
          >
            Analysis History
          </button>
        </div>

        {activeTab === 'upload' && (
          <>
            <div className="upload-section">
              <h2>Upload CSV Files</h2>
              <div className="file-input-wrapper">
                <div className="file-input">
                  <input
                    type="file"
                    accept=".csv"
                    multiple
                    onChange={handleFileChange}
                  />
                </div>
                <button
                  className="btn btn-primary"
                  onClick={handleAnalyze}
                  disabled={loading || !files}
                >
                  {loading ? 'Analyzing...' : 'Analyze Data Quality'}
                </button>
              </div>
              {files && files.length > 0 && (
                <p style={{ marginTop: '1rem', color: '#718096' }}>
                  Selected {files.length} file{files.length > 1 ? 's' : ''}
                </p>
              )}
            </div>

            {error && (
              <div className="error">
                <strong>Error:</strong> {error}
              </div>
            )}

            {loading && (
              <div className="loading">
                <div className="spinner"></div>
                <p>Analyzing your data...</p>
              </div>
            )}

            {results && (
              <div className="results-container">
                {results.map((result, index) => (
                  <DatasetResults key={index} data={result} />
                ))}
              </div>
            )}
          </>
        )}

        {activeTab === 'history' && (
          <>
            {historyLoading && (
              <div className="loading">
                <div className="spinner"></div>
                <p>Loading history...</p>
              </div>
            )}
            {!historyLoading && (
              <AnalysisHistory
                history={history}
                onRefresh={fetchHistory}
                onDelete={handleDeleteHistory}
              />
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default App
