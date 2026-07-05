/**
 * WebSocket Hook for Real-time Updates
 * Falls back to polling if WebSocket is unavailable
 * Only activates during market hours (Monday-Friday, 9:15 AM - 3:30 PM IST)
 */
import { useEffect, useRef, useState, useCallback } from 'react'
import { API_BASE } from '../config'
import { isMarketOpen, getMarketStatus } from '../utils/marketHours'

interface WebSocketMessage {
  type: string
  file?: string
  timestamp?: string
  data?: any
}

interface UseWebSocketOptions {
  onMessage?: (message: WebSocketMessage) => void
  onError?: (error: Event) => void
  onConnect?: () => void
  onDisconnect?: () => void
  fallbackPollInterval?: number // Polling interval if WebSocket fails (ms)
  enabled?: boolean // Enable/disable WebSocket
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const {
    onMessage,
    onError,
    onConnect,
    onDisconnect,
    fallbackPollInterval = 3000,
    enabled = true
  } = options

  const [isConnected, setIsConnected] = useState(false)
  const [usePolling, setUsePolling] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const isConnectingRef = useRef(false)
  const marketCheckIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const reconnectAttemptsRef = useRef(0)

  // Store callbacks in refs to prevent unnecessary reconnections
  const callbacksRef = useRef({ onMessage, onError, onConnect, onDisconnect })
  
  // Update callbacks ref when they change (without causing reconnection)
  useEffect(() => {
    callbacksRef.current = { onMessage, onError, onConnect, onDisconnect }
  }, [onMessage, onError, onConnect, onDisconnect])

  const connect = useCallback(() => {
    if (!enabled) return
    
    // Check if market is open - only connect during market hours
    if (!isMarketOpen()) {
      // Market is closed, use polling instead
      setUsePolling(true)
      setIsConnected(false)
      return
    }
    
    if (isConnectingRef.current) return // Prevent multiple simultaneous connections
    if (wsRef.current?.readyState === WebSocket.OPEN) return // Already connected

    isConnectingRef.current = true

    try {
      // Close existing connection if any
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
      }

      // Convert http:// to ws:// or https:// to wss://
      const wsUrl = API_BASE.replace(/^http/, 'ws') + '/ws/stream'
      const ws = new WebSocket(wsUrl)

      ws.onopen = () => {
        isConnectingRef.current = false
        reconnectAttemptsRef.current = 0
        setIsConnected(true)
        setUsePolling(false)
        callbacksRef.current.onConnect?.()
        // Clear any polling fallback
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current)
          pollIntervalRef.current = null
        }
      }

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          callbacksRef.current.onMessage?.(message)
        } catch (error) {
          // Silently handle parse errors
        }
      }

      ws.onerror = (error) => {
        isConnectingRef.current = false
        // Don't log WebSocket errors to console (they're expected during connection)
        setUsePolling(true)
        callbacksRef.current.onError?.(error)
      }

      ws.onclose = (event) => {
        isConnectingRef.current = false
        setIsConnected(false)
        setUsePolling(true) // Fall back to polling immediately
        callbacksRef.current.onDisconnect?.()
        
        // Only attempt to reconnect if:
        // 1. It wasn't a normal closure (code 1000)
        // 2. WebSocket is still enabled
        // 3. Market is still open
        if (event.code !== 1000 && enabled && wsRef.current === ws && isMarketOpen()) {
          if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current)
          }
          // Exponential backoff with jitter, capped at 30s. Previously a
          // fixed 3s retry with no cap - a backend outage meant every
          // connected tab hammered the server with a reconnect attempt
          // every 3 seconds indefinitely.
          const attempt = reconnectAttemptsRef.current
          reconnectAttemptsRef.current = attempt + 1
          const baseDelay = Math.min(3000 * 2 ** attempt, 30000)
          const jitter = baseDelay * 0.2 * Math.random()
          const delay = baseDelay + jitter
          reconnectTimeoutRef.current = setTimeout(() => {
            if (enabled && !isConnectingRef.current && isMarketOpen()) {
              connect()
            }
          }, delay)
        }
      }

      wsRef.current = ws
    } catch (error) {
      isConnectingRef.current = false
      // WebSocket not available, silently fall back to polling
      setUsePolling(true)
    }
  }, [enabled]) // Only depend on enabled, not callbacks

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
    if (marketCheckIntervalRef.current) {
      clearInterval(marketCheckIntervalRef.current)
      marketCheckIntervalRef.current = null
    }
    if (wsRef.current) {
      wsRef.current.close(1000, 'Component unmounting') // Normal closure
      wsRef.current = null
    }
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current)
      pollIntervalRef.current = null
    }
    isConnectingRef.current = false
    reconnectAttemptsRef.current = 0
    setIsConnected(false)
  }, [])

  useEffect(() => {
    if (enabled) {
      // Check market status and connect if market is open
      const checkAndConnect = () => {
        if (isMarketOpen()) {
          if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
            connect()
          }
        } else {
          // Market is closed, disconnect and use polling
          disconnect()
          setUsePolling(true)
        }
      }
      
      // Initial check after a small delay
      const timeoutId = setTimeout(checkAndConnect, 500)
      
      // Check market status every minute to handle market open/close transitions
      marketCheckIntervalRef.current = setInterval(checkAndConnect, 60000) // Check every minute
      
      return () => {
        clearTimeout(timeoutId)
        if (marketCheckIntervalRef.current) {
          clearInterval(marketCheckIntervalRef.current)
          marketCheckIntervalRef.current = null
        }
        disconnect()
      }
    } else {
      disconnect()
      return () => {}
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [enabled]) // Only depend on enabled, not connect/disconnect

  // Polling fallback
  useEffect(() => {
    if (usePolling && fallbackPollInterval > 0 && callbacksRef.current.onMessage) {
      const poll = () => {
        // Trigger a polling update
        callbacksRef.current.onMessage?.({
          type: 'poll',
          timestamp: new Date().toISOString()
        })
      }

      pollIntervalRef.current = setInterval(poll, fallbackPollInterval)
      return () => {
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current)
          pollIntervalRef.current = null
        }
      }
    }
  }, [usePolling, fallbackPollInterval]) // Removed onMessage dependency

  return {
    isConnected,
    usePolling,
    connect,
    disconnect
  }
}
