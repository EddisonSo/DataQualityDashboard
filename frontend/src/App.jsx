import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'
import DatasetResults from './components/DatasetResults'
import AnalysisHistory from './components/AnalysisHistory'
import DuplicateFileModal from './components/DuplicateFileModal'
import { formatTimestamp, formatRelativeTime } from './utils/formatters'

const API_URL = 'http://localhost:8000'

function App() {
  const [files, setFiles] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [results, setResults] = useState(null)
  const [history, setHistory] = useState([])
  const [historyLoading, setHistoryLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('upload')
  const [selectedAnalysis, setSelectedAnalysis] = useState(null)
  const [showDuplicateModal, setShowDuplicateModal] = useState(false)
  const [duplicateFiles, setDuplicateFiles] = useState([])

  const handleFileChange = (e) => {
    setFiles(e.target.files)
    setError(null)
  }

  const handleAnalyze = async (forceReanalyze = false) => {
    if (!files || files.length === 0) {
      setError('Please select at least one CSV file')
      return
    }

    setLoading(true)
    setError(null)
    setResults(null)

    try {
      // First, check if files have been analyzed before
      if (!forceReanalyze) {
        const checkFormData = new FormData()
        Array.from(files).forEach(file => {
          checkFormData.append('files', file)
        })

        const checkResponse = await axios.post(`${API_URL}/check-files`, checkFormData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })

        const previouslyAnalyzed = checkResponse.data.file_checks.filter(
          check => check.previously_analyzed
        )

        if (previouslyAnalyzed.length > 0) {
          // Show custom modal instead of browser confirm
          setDuplicateFiles(previouslyAnalyzed)
          setShowDuplicateModal(true)
          setLoading(false)
          return
        }
      }

      // Proceed with analysis
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

  const handleViewAnalysis = (analysis) => {
    setSelectedAnalysis(analysis)
    setActiveTab('view-analysis')
  }

  const handleBackToHistory = () => {
    setSelectedAnalysis(null)
    setActiveTab('history')
  }

  const handleReanalyze = () => {
    setShowDuplicateModal(false)
    setDuplicateFiles([])
    // Force re-analyze
    handleAnalyze(true)
  }

  const handleViewPrevious = async () => {
    setShowDuplicateModal(false)
    setLoading(true)

    try {
      // Fetch the full analysis for each duplicate file
      const previousResults = duplicateFiles.map(check => {
        const prev = check.previous_analysis
        return axios.get(`${API_URL}/history/${prev.analysis_id}`)
      })

      const responses = await Promise.all(previousResults)
      setResults(responses.map(r => r.data.analysis.analysis_results))
    } catch (err) {
      setError('Failed to load previous results')
    } finally {
      setDuplicateFiles([])
      setLoading(false)
    }
  }

  const handleCancelDuplicateModal = () => {
    setShowDuplicateModal(false)
    setDuplicateFiles([])
    setLoading(false)
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
                  onClick={() => handleAnalyze()}
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
                onViewAnalysis={handleViewAnalysis}
              />
            )}
          </>
        )}

        {activeTab === 'view-analysis' && selectedAnalysis && (
          <>
            <div className="single-analysis-header">
              <button
                className="btn btn-secondary"
                onClick={handleBackToHistory}
              >
                ← Back to History
              </button>
              <div className="analysis-meta">
                <h2>{selectedAnalysis.dataset_name}</h2>
                <p className="analysis-timestamp">
                  <span className="timestamp-label">Analyzed:</span>{' '}
                  <span title={formatTimestamp(selectedAnalysis.analysis_timestamp, true)}>
                    {formatRelativeTime(selectedAnalysis.analysis_timestamp)}
                  </span>
                  {' '}
                  <span className="timestamp-full">
                    ({formatTimestamp(selectedAnalysis.analysis_timestamp)})
                  </span>
                </p>
                <p className="analysis-id-display">Analysis ID: {selectedAnalysis.analysis_id}</p>
              </div>
            </div>
            <div className="results-container">
              <DatasetResults data={selectedAnalysis.analysis_results} />
            </div>
          </>
        )}
      </div>

      {showDuplicateModal && (
        <DuplicateFileModal
          files={duplicateFiles}
          onReanalyze={handleReanalyze}
          onViewPrevious={handleViewPrevious}
          onCancel={handleCancelDuplicateModal}
        />
      )}
    </div>
  )
}

export default App
