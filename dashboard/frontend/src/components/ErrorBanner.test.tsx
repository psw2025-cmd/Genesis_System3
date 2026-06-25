import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import ErrorBanner from './ErrorBanner'

describe('ErrorBanner', () => {
  it('renders the endpoint and message', () => {
    render(<ErrorBanner endpoint="/api/state" message="Network timeout" />)
    expect(screen.getByText('/api/state')).toBeInTheDocument()
    expect(screen.getByText('Network timeout')).toBeInTheDocument()
  })

  it('shows HTTP status when provided', () => {
    render(<ErrorBanner endpoint="/api/state" status={503} message="Service unavailable" />)
    expect(screen.getByText('503')).toBeInTheDocument()
  })

  it('does not render a status line when status is omitted', () => {
    render(<ErrorBanner endpoint="/api/state" message="Network timeout" />)
    expect(screen.queryByText('HTTP Status:')).not.toBeInTheDocument()
  })

  it('calls onRetry when the retry button is clicked', () => {
    const onRetry = vi.fn()
    render(<ErrorBanner endpoint="/api/state" message="Network timeout" onRetry={onRetry} />)
    const retryButton = screen.getByRole('button')
    fireEvent.click(retryButton)
    expect(onRetry).toHaveBeenCalledTimes(1)
  })
})
