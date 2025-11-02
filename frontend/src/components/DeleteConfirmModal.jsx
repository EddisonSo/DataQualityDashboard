import { formatTimestamp } from '../utils/formatters'

function DeleteConfirmModal({ analysis, onConfirm, onCancel }) {
  if (!analysis) return null

  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header modal-header-danger">
          <h2>⚠️ Confirm Delete</h2>
          <button className="modal-close" onClick={onCancel}>×</button>
        </div>

        <div className="modal-body">
          <p className="modal-description">
            Are you sure you want to delete this analysis? This action cannot be undone.
          </p>

          <div className="delete-confirm-item">
            <div className="file-icon">📊</div>
            <div className="file-info">
              <div className="file-name">{analysis.dataset_name}</div>
              <div className="file-meta">
                <span className="meta-item">
                  <strong>Analyzed:</strong> {formatTimestamp(analysis.analysis_timestamp)}
                </span>
                <span className="meta-divider">•</span>
                <span className="meta-item">
                  <strong>Records:</strong> {analysis.total_records?.toLocaleString()}
                </span>
                <span className="meta-divider">•</span>
                <span className="meta-item">
                  <strong>Columns:</strong> {analysis.total_columns}
                </span>
              </div>
              <div className="analysis-id-small">
                ID: {analysis.analysis_id}
              </div>
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onCancel}>
            Cancel
          </button>
          <button className="btn btn-danger" onClick={onConfirm}>
            Delete Analysis
          </button>
        </div>
      </div>
    </div>
  )
}

export default DeleteConfirmModal
