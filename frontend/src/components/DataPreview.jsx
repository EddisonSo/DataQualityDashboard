import { useState, useMemo } from 'react'

function DataPreview({ dataPreview }) {
  const [currentPage, setCurrentPage] = useState(1)
  const [sortColumn, setSortColumn] = useState(null)
  const [sortDirection, setSortDirection] = useState('asc') // 'asc' or 'desc'
  const rowsPerPage = 10

  if (!dataPreview || !dataPreview.data || dataPreview.data.length === 0) {
    return null
  }

  const { columns, data, total_rows } = dataPreview

  // Sort the data
  const sortedData = useMemo(() => {
    if (!sortColumn) {
      return data
    }

    return [...data].sort((a, b) => {
      const aVal = a[sortColumn]
      const bVal = b[sortColumn]

      // Handle null/undefined values - push them to the end
      if (aVal === null || aVal === undefined) return 1
      if (bVal === null || bVal === undefined) return -1

      // Compare values based on type
      let comparison = 0
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        comparison = aVal - bVal
      } else if (typeof aVal === 'boolean' && typeof bVal === 'boolean') {
        comparison = aVal === bVal ? 0 : aVal ? 1 : -1
      } else {
        // String comparison
        const aStr = String(aVal).toLowerCase()
        const bStr = String(bVal).toLowerCase()
        comparison = aStr.localeCompare(bStr)
      }

      return sortDirection === 'asc' ? comparison : -comparison
    })
  }, [data, sortColumn, sortDirection])

  const totalPages = Math.ceil(total_rows / rowsPerPage)

  // Calculate the data for current page
  const startIndex = (currentPage - 1) * rowsPerPage
  const endIndex = startIndex + rowsPerPage
  const currentData = sortedData.slice(startIndex, endIndex)

  const goToPage = (page) => {
    setCurrentPage(Math.max(1, Math.min(page, totalPages)))
  }

  const handleSort = (column) => {
    if (sortColumn === column) {
      // Toggle direction if clicking the same column
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      // New column, default to ascending
      setSortColumn(column)
      setSortDirection('asc')
    }
    // Reset to first page when sorting
    setCurrentPage(1)
  }

  const getSortIndicator = (column) => {
    if (sortColumn !== column) {
      return <span className="sort-indicator">⇅</span>
    }
    return sortDirection === 'asc'
      ? <span className="sort-indicator active">↑</span>
      : <span className="sort-indicator active">↓</span>
  }

  const formatValue = (value) => {
    if (value === null || value === undefined) {
      return <span className="null-value">null</span>
    }
    if (typeof value === 'boolean') {
      return value.toString()
    }
    if (typeof value === 'number') {
      return value.toLocaleString()
    }
    return String(value)
  }

  return (
    <div className="data-preview-section">
      <div className="section-header">
        <h3>Data Preview</h3>
        <span className="preview-info">
          Showing {startIndex + 1}-{Math.min(endIndex, total_rows)} of {total_rows} rows
        </span>
      </div>

      <div className="table-wrapper">
        <table className="data-preview-table">
          <thead>
            <tr>
              <th className="row-number-header">#</th>
              {columns.map((col, idx) => (
                <th
                  key={idx}
                  className="sortable-header"
                  onClick={() => handleSort(col)}
                  title={`Click to sort by ${col}`}
                >
                  <div className="header-content">
                    <span>{col}</span>
                    {getSortIndicator(col)}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {currentData.map((row, rowIdx) => (
              <tr key={startIndex + rowIdx}>
                <td className="row-number">{startIndex + rowIdx + 1}</td>
                {columns.map((col, colIdx) => (
                  <td key={colIdx}>{formatValue(row[col])}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="pagination">
          <button
            className="pagination-btn"
            onClick={() => goToPage(1)}
            disabled={currentPage === 1}
          >
            ««
          </button>
          <button
            className="pagination-btn"
            onClick={() => goToPage(currentPage - 1)}
            disabled={currentPage === 1}
          >
            ‹
          </button>

          <div className="pagination-info">
            Page {currentPage} of {totalPages}
          </div>

          <button
            className="pagination-btn"
            onClick={() => goToPage(currentPage + 1)}
            disabled={currentPage === totalPages}
          >
            ›
          </button>
          <button
            className="pagination-btn"
            onClick={() => goToPage(totalPages)}
            disabled={currentPage === totalPages}
          >
            »»
          </button>
        </div>
      )}
    </div>
  )
}

export default DataPreview
