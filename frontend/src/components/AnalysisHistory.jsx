import { useState } from 'react'
import DatasetResults from './DatasetResults'
import { formatTimestamp, formatRelativeTime } from '../utils/formatters'

function AnalysisHistory({ history, onRefresh, onDelete, onViewAnalysis }) {
  const [expandedId, setExpandedId] = useState(null)

  const toggleExpand = (analysisId) => {
    setExpandedId(expandedId === analysisId ? null : analysisId)
  }

  if (!history || history.length === 0) {
    return (
      <div className="history-empty">
        <p>No analysis history yet. Upload and analyze CSV files to see history here.</p>
      </div>
    )
  }

  return (
    <div className="history-section">
      <div className="history-header">
        <h2>Analysis History ({history.length})</h2>
        <button className="btn btn-secondary" onClick={onRefresh}>
          Refresh
        </button>
      </div>

      <div className="history-list">
        {history.map((item) => (
          <div key={item.analysis_id} className="history-item">
            <div className="history-item-header" onClick={() => toggleExpand(item.analysis_id)}>
              <div className="history-item-info">
                <div className="history-item-title">
                  <span className="dataset-name">{item.dataset_name}</span>
                  {item.has_issues && (
                    <span className="badge badge-warning">Has Issues</span>
                  )}
                  {!item.has_issues && (
                    <span className="badge badge-success">Clean</span>
                  )}
                </div>
                <div className="history-item-meta">
                  <span className="timestamp" title={formatTimestamp(item.analysis_timestamp, true)}>
                    {formatRelativeTime(item.analysis_timestamp)}
                  </span>
                  <span className="meta-divider">•</span>
                  <span>{item.total_records.toLocaleString()} records</span>
                  <span className="meta-divider">•</span>
                  <span>{item.total_columns} columns</span>
                  <span className="meta-divider">•</span>
                  <span className="analysis-id">ID: {item.analysis_id}</span>
                </div>
              </div>
              <div className="history-item-actions">
                {onViewAnalysis && (
                  <button
                    className="btn btn-primary btn-sm"
                    onClick={(e) => {
                      e.stopPropagation()
                      onViewAnalysis(item)
                    }}
                  >
                    View Details
                  </button>
                )}
                {onDelete && (
                  <button
                    className="btn btn-danger btn-sm"
                    onClick={(e) => {
                      e.stopPropagation()
                      onDelete(item)
                    }}
                  >
                    Delete
                  </button>
                )}
                <span className="expand-icon">
                  {expandedId === item.analysis_id ? '▼' : '▶'}
                </span>
              </div>
            </div>

            {expandedId === item.analysis_id && (
              <div className="history-item-expanded">
                <DatasetResults data={item.analysis_results} />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default AnalysisHistory
