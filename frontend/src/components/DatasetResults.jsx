import React from 'react'
import DataPreview from './DataPreview'

function DatasetResults({ data }) {
  const {
    dataset_name,
    total_records,
    total_columns,
    data_preview,
    missing_values,
    invalid_values,
    duplicates,
    logical_issues,
    outliers,
    statistics,
    column_details
  } = data

  const totalIssues =
    missing_values.total_missing_values +
    invalid_values.total_invalid_count +
    duplicates.total_duplicates +
    logical_issues.total_issues +
    (outliers?.total_outlier_count || 0)

  const getSeverityClass = (percentage) => {
    if (percentage > 10) return 'badge-danger'
    if (percentage > 5) return 'badge-warning'
    return 'badge-info'
  }

  return (
    <div className="dataset-result">
      <div className="dataset-header">
        <h2>{dataset_name}</h2>
        <div className="dataset-stats">
          <div className="stat-item">
            <strong>Records:</strong> {total_records.toLocaleString()}
          </div>
          <div className="stat-item">
            <strong>Columns:</strong> {total_columns}
          </div>
          <div className="stat-item">
            <strong>Total Issues:</strong> {totalIssues.toLocaleString()}
          </div>
        </div>
      </div>

      <DataPreview dataPreview={data_preview} />

      <div className="summary-cards">
        <div className="summary-card">
          <h4>Missing Values</h4>
          <div className="value">{missing_values.total_missing_values.toLocaleString()}</div>
          <div style={{ fontSize: '0.875rem', opacity: 0.9, marginTop: '0.25rem' }}>
            {missing_values.overall_missing_percentage}% overall
          </div>
        </div>
        <div className="summary-card">
          <h4>Invalid Values</h4>
          <div className="value">{invalid_values.total_invalid_count.toLocaleString()}</div>
          <div style={{ fontSize: '0.875rem', opacity: 0.9, marginTop: '0.25rem' }}>
            {invalid_values.invalid_patterns.length} pattern{invalid_values.invalid_patterns.length !== 1 ? 's' : ''}
          </div>
        </div>
        <div className="summary-card">
          <h4>Duplicates</h4>
          <div className="value">{duplicates.total_duplicates.toLocaleString()}</div>
          <div style={{ fontSize: '0.875rem', opacity: 0.9, marginTop: '0.25rem' }}>
            {duplicates.duplicate_patterns.length} pattern{duplicates.duplicate_patterns.length !== 1 ? 's' : ''}
          </div>
        </div>
        <div className="summary-card">
          <h4>Logical Issues</h4>
          <div className="value">{logical_issues.total_issues.toLocaleString()}</div>
          <div style={{ fontSize: '0.875rem', opacity: 0.9, marginTop: '0.25rem' }}>
            {logical_issues.logical_inconsistencies.length} type{logical_issues.logical_inconsistencies.length !== 1 ? 's' : ''}
          </div>
        </div>
        <div className="summary-card">
          <h4>Outliers</h4>
          <div className="value">{outliers?.total_outlier_count?.toLocaleString() || 0}</div>
          <div style={{ fontSize: '0.875rem', opacity: 0.9, marginTop: '0.25rem' }}>
            {outliers?.outlier_patterns?.length || 0} column{(outliers?.outlier_patterns?.length || 0) !== 1 ? 's' : ''}
          </div>
        </div>
      </div>

      <div className="sections">
        {/* Missing Values Section */}
        {missing_values.columns_with_missing.length > 0 && (
          <div className="section">
            <h3>
              Missing Values
              <span className={`badge ${getSeverityClass(missing_values.overall_missing_percentage)}`}>
                {missing_values.columns_with_missing.length} columns affected
              </span>
            </h3>
            <div className="issue-list">
              {missing_values.columns_with_missing.map((item, idx) => (
                <div key={idx} className="issue-item">
                  <div className="issue-header">
                    <span className="issue-title">{item.column}</span>
                    <span className={`badge ${getSeverityClass(item.missing_percentage)}`}>
                      {item.missing_percentage}%
                    </span>
                  </div>
                  <div className="issue-description">
                    {item.missing_count.toLocaleString()} missing value{item.missing_count !== 1 ? 's' : ''} out of {total_records.toLocaleString()} records
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Invalid Values Section */}
        {invalid_values.invalid_patterns.length > 0 && (
          <div className="section">
            <h3>
              Invalid Values
              <span className="badge badge-danger">
                {invalid_values.invalid_patterns.length} issue{invalid_values.invalid_patterns.length !== 1 ? 's' : ''}
              </span>
            </h3>
            <div className="issue-list">
              {invalid_values.invalid_patterns.map((item, idx) => (
                <div key={idx} className="issue-item">
                  <div className="issue-header">
                    <span className="issue-title">
                      {item.column} - {item.issue_type}
                    </span>
                    <span className={`badge ${getSeverityClass(item.percentage)}`}>
                      {item.percentage}%
                    </span>
                  </div>
                  <div className="issue-description">{item.description}</div>

                  {item.invalid_rows && item.invalid_rows.length > 0 && (
                    <div style={{ marginTop: '0.75rem', overflowX: 'auto', maxWidth: '100%' }}>
                      <table className="column-table">
                        <thead>
                          <tr>
                            {Object.keys(item.invalid_rows[0]).map((col, i) => (
                              <th key={i}>{col}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {item.invalid_rows.map((row, rowIdx) => (
                            <tr key={rowIdx}>
                              {Object.values(row).map((val, valIdx) => (
                                <td key={valIdx}>
                                  {val !== null && val !== undefined && val !== '' ? String(val) : (
                                    <span style={{ color: '#cbd5e0', fontStyle: 'italic' }}>null</span>
                                  )}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Duplicates Section */}
        {duplicates.duplicate_patterns.length > 0 && (
          <div className="section">
            <h3>
              Duplicate Records
              <span className="badge badge-warning">
                {duplicates.total_duplicates} record{duplicates.total_duplicates !== 1 ? 's' : ''}
              </span>
            </h3>
            <div className="issue-list">
              {duplicates.duplicate_patterns.map((item, idx) => (
                <div key={idx} className="issue-item">
                  <div className="issue-header">
                    <span className="issue-title">{item.type}</span>
                    <span className={`badge ${getSeverityClass(item.percentage)}`}>
                      {item.percentage}%
                    </span>
                  </div>
                  <div className="issue-description">
                    {item.description} - {item.duplicate_groups ? item.duplicate_groups.length : 0} duplicate group{item.duplicate_groups && item.duplicate_groups.length !== 1 ? 's' : ''} found
                  </div>

                  {item.duplicate_groups && item.duplicate_groups.length > 0 && (
                    <div style={{ marginTop: '0.75rem' }}>
                      {item.duplicate_groups.map((group, groupIdx) => (
                        <div key={groupIdx} style={{ marginBottom: '1.5rem' }}>
                          <div style={{
                            fontSize: '0.9rem',
                            fontWeight: '600',
                            color: '#4a5568',
                            marginBottom: '0.5rem',
                            padding: '0.5rem',
                            background: '#f7fafc',
                            borderRadius: '4px'
                          }}>
                            Duplicate Group {groupIdx + 1} ({group.length} records)
                          </div>
                          <div style={{ overflowX: 'auto', maxWidth: '100%' }}>
                            <table className="column-table">
                              <thead>
                                <tr>
                                  {Object.keys(group[0]).map((col, i) => (
                                    <th key={i}>{col}</th>
                                  ))}
                                </tr>
                              </thead>
                              <tbody>
                                {group.map((row, rowIdx) => (
                                  <tr key={rowIdx}>
                                    {Object.values(row).map((val, valIdx) => (
                                      <td key={valIdx}>
                                        {val !== null && val !== undefined && val !== '' ? String(val) : (
                                          <span style={{ color: '#cbd5e0', fontStyle: 'italic' }}>null</span>
                                        )}
                                      </td>
                                    ))}
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Logical Issues Section */}
        {logical_issues.logical_inconsistencies.length > 0 && (
          <div className="section">
            <h3>
              Logical Inconsistencies
              <span className="badge badge-danger">
                {logical_issues.total_issues} issue{logical_issues.total_issues !== 1 ? 's' : ''}
              </span>
            </h3>
            <div className="issue-list">
              {logical_issues.logical_inconsistencies.map((item, idx) => (
                <div
                  key={idx}
                  className={`issue-item severity-${item.severity}`}
                >
                  <div className="issue-header">
                    <span className="issue-title">{item.type}</span>
                    <span className={`badge ${getSeverityClass(item.percentage)}`}>
                      {item.count.toLocaleString()} records
                    </span>
                  </div>
                  <div className="issue-description">{item.description}</div>

                  {item.issue_rows && item.issue_rows.length > 0 && (
                    <div style={{ marginTop: '0.75rem', overflowX: 'auto', maxWidth: '100%' }}>
                      <table className="column-table">
                        <thead>
                          <tr>
                            {Object.keys(item.issue_rows[0]).map((col, i) => (
                              <th key={i}>{col}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {item.issue_rows.map((row, rowIdx) => (
                            <tr key={rowIdx}>
                              {Object.values(row).map((val, valIdx) => (
                                <td key={valIdx}>
                                  {val !== null && val !== undefined && val !== '' ? String(val) : (
                                    <span style={{ color: '#cbd5e0', fontStyle: 'italic' }}>null</span>
                                  )}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Outliers Section */}
        {outliers && outliers.outlier_patterns && outliers.outlier_patterns.length > 0 && (
          <div className="section">
            <h3>
              Statistical Outliers (1.5×IQR Method)
              <span className="badge badge-warning">
                {outliers.outlier_patterns.length} column{outliers.outlier_patterns.length !== 1 ? 's' : ''}
              </span>
            </h3>
            <div className="issue-list">
              {outliers.outlier_patterns.map((item, idx) => (
                <div key={idx} className="issue-item">
                  <div className="issue-header">
                    <span className="issue-title">{item.column}</span>
                    <span className={`badge ${getSeverityClass(item.percentage)}`}>
                      {item.count.toLocaleString()} outlier{item.count !== 1 ? 's' : ''} ({item.percentage}%)
                    </span>
                  </div>
                  <div className="issue-description">
                    Values outside the range [{item.lower_bound}, {item.upper_bound}]
                  </div>

                  {/* Statistical Details */}
                  <div style={{
                    marginTop: '0.75rem',
                    padding: '0.75rem',
                    background: '#f7fafc',
                    borderRadius: '4px',
                    fontSize: '0.875rem'
                  }}>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '0.5rem' }}>
                      <div>
                        <strong>Q1 (25%):</strong> {item.Q1}
                      </div>
                      <div>
                        <strong>Q3 (75%):</strong> {item.Q3}
                      </div>
                      <div>
                        <strong>IQR:</strong> {item.IQR}
                      </div>
                      <div>
                        <strong>Lower Bound:</strong> {item.lower_bound}
                      </div>
                      <div>
                        <strong>Upper Bound:</strong> {item.upper_bound}
                      </div>
                    </div>
                  </div>

                  {/* Example Outlier Values */}
                  {item.outlier_values && item.outlier_values.length > 0 && (
                    <div style={{ marginTop: '0.75rem' }}>
                      <div style={{ fontSize: '0.875rem', fontWeight: '600', marginBottom: '0.25rem' }}>
                        Example outlier values:
                      </div>
                      <div style={{ fontSize: '0.875rem', color: '#4a5568' }}>
                        {item.outlier_values.join(', ')}
                      </div>
                    </div>
                  )}

                  {/* Outlier Rows Table */}
                  {item.outlier_rows && item.outlier_rows.length > 0 && (
                    <div style={{ marginTop: '0.75rem', overflowX: 'auto', maxWidth: '100%' }}>
                      <div style={{ fontSize: '0.875rem', fontWeight: '600', marginBottom: '0.5rem' }}>
                        Affected records:
                      </div>
                      <table className="column-table">
                        <thead>
                          <tr>
                            {Object.keys(item.outlier_rows[0]).map((col, i) => (
                              <th key={i}>{col}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {item.outlier_rows.slice(0, 10).map((row, rowIdx) => (
                            <tr key={rowIdx}>
                              {Object.entries(row).map(([colName, val], valIdx) => (
                                <td
                                  key={valIdx}
                                  style={colName === item.column ? {
                                    background: '#fff5f5',
                                    fontWeight: '600',
                                    color: '#c53030'
                                  } : {}}
                                >
                                  {val !== null && val !== undefined && val !== '' ? String(val) : (
                                    <span style={{ color: '#cbd5e0', fontStyle: 'italic' }}>null</span>
                                  )}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                      {item.outlier_rows.length > 10 && (
                        <div style={{ fontSize: '0.875rem', color: '#718096', marginTop: '0.5rem', fontStyle: 'italic' }}>
                          Showing 10 of {item.outlier_rows.length} outlier records
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Statistical Summary Section */}
        {statistics && Object.keys(statistics).length > 0 && (
          <div className="section">
            <h3>
              Statistical Summary
              <span className="badge badge-info">
                {Object.keys(statistics).length} numeric column{Object.keys(statistics).length !== 1 ? 's' : ''}
              </span>
            </h3>
            <div style={{ overflowX: 'auto', maxWidth: '100%' }}>
              <table className="column-table">
                <thead>
                  <tr>
                    <th>Column</th>
                    <th>Mean</th>
                    <th>Median</th>
                    <th>Min</th>
                    <th>Max</th>
                    <th>Std Dev</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(statistics).map(([colName, stats], idx) => (
                    <tr key={idx}>
                      <td><strong>{colName}</strong></td>
                      <td>{stats.mean !== null ? stats.mean : <span style={{ color: '#cbd5e0', fontStyle: 'italic' }}>N/A</span>}</td>
                      <td>{stats.median !== null ? stats.median : <span style={{ color: '#cbd5e0', fontStyle: 'italic' }}>N/A</span>}</td>
                      <td>{stats.min !== null ? stats.min : <span style={{ color: '#cbd5e0', fontStyle: 'italic' }}>N/A</span>}</td>
                      <td>{stats.max !== null ? stats.max : <span style={{ color: '#cbd5e0', fontStyle: 'italic' }}>N/A</span>}</td>
                      <td>{stats.std !== null ? stats.std : <span style={{ color: '#cbd5e0', fontStyle: 'italic' }}>N/A</span>}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Missing Value Analysis Section */}
        <div className="section">
          <h3>Missing Value Analysis</h3>
          <table className="column-table">
            <thead>
              <tr>
                <th>Column Name</th>
                <th>Null %</th>
              </tr>
            </thead>
            <tbody>
              {column_details.map((col, idx) => (
                <tr key={idx}>
                  <td><strong>{col.name}</strong></td>
                  <td>
                    <span className={`badge ${getSeverityClass(col.null_percentage)}`}>
                      {col.null_percentage}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {totalIssues === 0 && (
        <div className="no-issues">
          <h3>No Data Quality Issues Found</h3>
          <p>This dataset appears to be clean and well-maintained.</p>
        </div>
      )}
    </div>
  )
}

export default DatasetResults
