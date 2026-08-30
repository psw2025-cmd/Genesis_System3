import React, { Component, ErrorInfo, ReactNode } from 'react'
import { AlertTriangle, RefreshCw } from 'lucide-react'

interface Props {
  children: ReactNode
  widgetName?: string
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
}

export class WidgetErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    }
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
    }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.warn(`[WidgetErrorBoundary] Caught error in ${this.props.widgetName || 'widget'}:`, error, errorInfo)
    this.setState({
      error,
      errorInfo,
    })
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    })
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      const widgetTitle = this.props.widgetName || 'Component'

      return (
        <div className="p-4 rounded-xl border border-amber-500/30 bg-amber-950/20 text-slate-200 flex flex-col justify-between min-h-[140px] transition-all">
          <div className="flex items-start gap-3">
            <div className="p-2 rounded-lg bg-amber-500/20 text-amber-400 mt-0.5">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex items-center justify-between gap-2">
                <h4 className="font-semibold text-sm text-amber-200 truncate">{widgetTitle} Unavailable</h4>
                <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
                  Protected
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-1">
                Data stream or rendering temporarily interrupted. Other widgets remain fully operational.
              </p>
              {this.state.error && (
                <details className="mt-2 text-[11px] text-slate-400 font-mono">
                  <summary className="cursor-pointer text-amber-400/80 hover:text-amber-300 transition-colors">
                    View Diagnostic Trace
                  </summary>
                  <pre className="mt-1 p-2 rounded bg-black/60 text-amber-300/90 overflow-x-auto text-[10px] max-h-24">
                    {this.state.error.message || String(this.state.error)}
                  </pre>
                </details>
              )}
            </div>
          </div>
          <div className="mt-3 flex justify-end">
            <button
              onClick={this.handleReset}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 text-xs font-medium border border-amber-500/30 active:scale-95 transition-all focus:outline-none focus:ring-2 focus:ring-amber-400/50"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Retry Widget</span>
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
export default WidgetErrorBoundary
