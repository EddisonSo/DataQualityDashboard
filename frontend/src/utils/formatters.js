/**
 * Utility functions for formatting data
 */

/**
 * Format timestamp to local time in a readable format
 * Uses the user's locale and timezone automatically
 * @param {string} timestamp - ISO timestamp string
 * @param {boolean} includeSeconds - Whether to include seconds in the output
 * @returns {string} Formatted local time string
 */
export const formatTimestamp = (timestamp, includeSeconds = false) => {
  if (!timestamp) return 'N/A'

  const date = new Date(timestamp)

  // Check if date is valid
  if (isNaN(date.getTime())) return 'Invalid date'

  const options = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  }

  if (includeSeconds) {
    options.second = '2-digit'
  }

  // Use user's locale by not specifying locale parameter
  return date.toLocaleString(undefined, options)
}

/**
 * Format timestamp to relative time (e.g., "2 hours ago")
 * @param {string} timestamp - ISO timestamp string
 * @returns {string} Relative time string
 */
export const formatRelativeTime = (timestamp) => {
  if (!timestamp) return 'N/A'

  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now - date
  const diffSec = Math.floor(diffMs / 1000)
  const diffMin = Math.floor(diffSec / 60)
  const diffHour = Math.floor(diffMin / 60)
  const diffDay = Math.floor(diffHour / 24)

  if (diffSec < 60) {
    return 'Just now'
  } else if (diffMin < 60) {
    return `${diffMin} minute${diffMin !== 1 ? 's' : ''} ago`
  } else if (diffHour < 24) {
    return `${diffHour} hour${diffHour !== 1 ? 's' : ''} ago`
  } else if (diffDay < 7) {
    return `${diffDay} day${diffDay !== 1 ? 's' : ''} ago`
  } else {
    return formatTimestamp(timestamp)
  }
}

/**
 * Format date only (no time)
 * Uses the user's locale automatically
 * @param {string} timestamp - ISO timestamp string
 * @returns {string} Formatted date string
 */
export const formatDate = (timestamp) => {
  if (!timestamp) return 'N/A'

  const date = new Date(timestamp)

  return date.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

/**
 * Format time only (no date)
 * Uses the user's locale automatically
 * @param {string} timestamp - ISO timestamp string
 * @returns {string} Formatted time string
 */
export const formatTime = (timestamp) => {
  if (!timestamp) return 'N/A'

  const date = new Date(timestamp)

  return date.toLocaleTimeString(undefined, {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: true
  })
}
