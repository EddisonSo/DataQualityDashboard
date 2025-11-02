import { formatTimestamp, formatRelativeTime } from '../utils/formatters'

function DuplicateFileModal({ files, onReanalyze, onViewPrevious, onCancel }) {
  if (!files || files.length === 0) return null

  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Files Already Analyzed</h2>
          <button className="modal-close" onClick={onCancel}>×</button>
        </div>

        <div className="modal-body">
          <p className="modal-description">
            {files.length === 1 ? 'This file has' : `${files.length} files have`} been analyzed before.
            Would you like to re-analyze or view the previous results?
          </p>

          <div className="duplicate-files-list">
            {files.map((file, idx) => (
              <div key={idx} className="duplicate-file-item">
                <div className="file-icon">📄</div>
                <div className="file-info">
                  <div className="file-name">{file.filename}</div>
                  <div className="file-meta">
                    <span
                      className="meta-item"
                      title={formatTimestamp(file.previous_analysis.analysis_timestamp, true)}
                    >
                      <strong>Analyzed:</strong> {formatRelativeTime(file.previous_analysis.analysis_timestamp)}
                    </span>
                    <span className="meta-divider">•</span>
                    <span className="meta-item">
                      <strong>{file.previous_analysis.total_records.toLocaleString()}</strong> records
                    </span>
                    <span className="meta-divider">•</span>
                    <span className="meta-item">
                      <strong>{file.previous_analysis.total_columns}</strong> columns
                    </span>
                    {file.previous_analysis.has_issues && (
                      <>
                        <span className="meta-divider">•</span>
                        <span className="badge badge-warning">Has Issues</span>
                      </>
                    )}
                    {!file.previous_analysis.has_issues && (
                      <>
                        <span className="meta-divider">•</span>
                        <span className="badge badge-success">Clean</span>
                      </>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onCancel}>
            Cancel
          </button>
          <button className="btn btn-primary" onClick={onViewPrevious}>
            View Previous Results
          </button>
          <button className="btn btn-reanalyze" onClick={onReanalyze}>
            Re-Analyze Files
          </button>
        </div>
      </div>
    </div>
  )
}

export default DuplicateFileModal
