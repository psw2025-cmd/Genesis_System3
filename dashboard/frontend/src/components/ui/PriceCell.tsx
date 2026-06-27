import { useEffect, useRef, useState } from 'react'
import { cn, fmt } from '../../lib/utils'

export function PriceCell({ value, decimals = 2, className = '' }: {
  value: number | null | undefined
  decimals?: number
  className?: string
}) {
  const prev  = useRef<number | null>(null)
  const [flash, setFlash] = useState<'up' | 'down' | null>(null)

  useEffect(() => {
    if (value == null) return
    if (prev.current != null && value !== prev.current) {
      setFlash(value > prev.current ? 'up' : 'down')
      const t = setTimeout(() => setFlash(null), 400)
      return () => clearTimeout(t)
    }
    prev.current = value
  }, [value])

  return (
    <span className={cn(
      'num inline-block px-1 rounded transition-colors duration-100',
      flash === 'up'   && 'animate-flash-up',
      flash === 'down' && 'animate-flash-down',
      className
    )}>
      {fmt(value, decimals)}
    </span>
  )
}
