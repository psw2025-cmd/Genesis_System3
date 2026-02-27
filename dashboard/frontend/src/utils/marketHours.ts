/**
 * Market Hours Detection for Indian Stock Market (Frontend)
 * Checks if market is open (Monday-Friday, 9:15 AM - 3:30 PM IST)
 */

// Market hours in IST
const MARKET_OPEN_HOUR = 9
const MARKET_OPEN_MINUTE = 15
const MARKET_CLOSE_HOUR = 15
const MARKET_CLOSE_MINUTE = 30

/**
 * Check if market is currently open
 * @returns {boolean} True if market is open (Monday-Friday, 9:15 AM - 3:30 PM IST)
 */
export function isMarketOpen(): boolean {
  const now = new Date()
  
  // Convert to IST (UTC+5:30)
  const istOffset = 5.5 * 60 * 60 * 1000 // IST is UTC+5:30
  const utcTime = now.getTime() + (now.getTimezoneOffset() * 60 * 1000)
  const istTime = new Date(utcTime + istOffset)
  
  // Get day of week (0=Sunday, 1=Monday, ..., 6=Saturday)
  const dayOfWeek = istTime.getUTCDay()
  
  // Check if it's a weekday (Monday=1 to Friday=5)
  if (dayOfWeek === 0 || dayOfWeek === 6) {
    return false // Weekend
  }
  
  // Get hours and minutes in IST
  const hours = istTime.getUTCHours()
  const minutes = istTime.getUTCMinutes()
  
  // Check if within market hours (9:15 AM - 3:30 PM IST)
  const currentTimeMinutes = hours * 60 + minutes
  const openTimeMinutes = MARKET_OPEN_HOUR * 60 + MARKET_OPEN_MINUTE // 9:15 = 555 minutes
  const closeTimeMinutes = MARKET_CLOSE_HOUR * 60 + MARKET_CLOSE_MINUTE // 15:30 = 930 minutes
  
  return currentTimeMinutes >= openTimeMinutes && currentTimeMinutes <= closeTimeMinutes
}

/**
 * Get market status information
 * @returns {object} Market status with details
 */
export function getMarketStatus(): {
  isOpen: boolean
  reason: string
  nextOpen?: string
} {
  const now = new Date()
  
  // Convert to IST (UTC+5:30)
  const istOffset = 5.5 * 60 * 60 * 1000
  const utcTime = now.getTime() + (now.getTimezoneOffset() * 60 * 1000)
  const istTime = new Date(utcTime + istOffset)
  
  const dayOfWeek = istTime.getUTCDay()
  const hours = istTime.getUTCHours()
  const minutes = istTime.getUTCMinutes()
  const currentTimeMinutes = hours * 60 + minutes
  const openTimeMinutes = MARKET_OPEN_HOUR * 60 + MARKET_OPEN_MINUTE
  const closeTimeMinutes = MARKET_CLOSE_HOUR * 60 + MARKET_CLOSE_MINUTE
  
  // Check if weekend
  if (dayOfWeek === 0 || dayOfWeek === 6) {
    const dayName = dayOfWeek === 0 ? 'Sunday' : 'Saturday'
    return {
      isOpen: false,
      reason: `Market closed: Weekend (${dayName})`
    }
  }
  
  // Check if before market open
  if (currentTimeMinutes < openTimeMinutes) {
    return {
      isOpen: false,
      reason: `Market closed: Before market hours (opens at ${MARKET_OPEN_HOUR}:${MARKET_OPEN_MINUTE.toString().padStart(2, '0')} AM IST)`
    }
  }
  
  // Check if after market close
  if (currentTimeMinutes > closeTimeMinutes) {
    return {
      isOpen: false,
      reason: `Market closed: After market hours (closed at ${MARKET_CLOSE_HOUR}:${MARKET_CLOSE_MINUTE.toString().padStart(2, '0')} PM IST)`
    }
  }
  
  // Market is open
  return {
    isOpen: true,
    reason: 'Market open'
  }
}

/**
 * Get next market open time
 * @returns {Date} Next market open datetime
 */
export function getNextMarketOpen(): Date {
  const now = new Date()
  const istOffset = 5.5 * 60 * 60 * 1000
  const utcTime = now.getTime() + (now.getTimezoneOffset() * 60 * 1000)
  const istTime = new Date(utcTime + istOffset)
  
  let nextOpen = new Date(istTime)
  nextOpen.setUTCHours(MARKET_OPEN_HOUR, MARKET_OPEN_MINUTE, 0, 0)
  
  const dayOfWeek = istTime.getUTCDay()
  const hours = istTime.getUTCHours()
  const minutes = istTime.getUTCMinutes()
  const currentTimeMinutes = hours * 60 + minutes
  const openTimeMinutes = MARKET_OPEN_HOUR * 60 + MARKET_OPEN_MINUTE
  
  // If today is weekday and before market open, return today's open time
  if (dayOfWeek >= 1 && dayOfWeek <= 5 && currentTimeMinutes < openTimeMinutes) {
    // Convert back to local time
    const localTime = new Date(nextOpen.getTime() - istOffset + (now.getTimezoneOffset() * 60 * 1000))
    return localTime
  }
  
  // Find next weekday
  let daysToAdd = 1
  while (true) {
    const nextDate = new Date(istTime)
    nextDate.setUTCDate(nextDate.getUTCDate() + daysToAdd)
    const nextDayOfWeek = nextDate.getUTCDay()
    
    if (nextDayOfWeek >= 1 && nextDayOfWeek <= 5) {
      // Found next weekday
      nextDate.setUTCHours(MARKET_OPEN_HOUR, MARKET_OPEN_MINUTE, 0, 0)
      // Convert back to local time
      const localTime = new Date(nextDate.getTime() - istOffset + (now.getTimezoneOffset() * 60 * 1000))
      return localTime
    }
    daysToAdd++
  }
}
