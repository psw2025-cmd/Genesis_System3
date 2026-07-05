import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function fmt(n: number | null | undefined, decimals = 2): string {
  if (n == null || isNaN(n)) return '--'
  return n.toLocaleString('en-IN', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })
}

export function fmtPct(n: number | null | undefined): string {
  if (n == null || isNaN(n)) return '--'
  return (n >= 0 ? '+' : '') + n.toFixed(2) + '%'
}

export function fmtCr(n: number | null | undefined): string {
  if (n == null || isNaN(n)) return '--'
  const abs = Math.abs(n)
  if (abs >= 1e7) return (n < 0 ? '-' : '') + (abs/1e7).toFixed(2) + ' Cr'
  if (abs >= 1e5) return (n < 0 ? '-' : '') + (abs/1e5).toFixed(2) + ' L'
  return '₹' + n.toLocaleString('en-IN', { maximumFractionDigits: 0 })
}

export function signClass(n: number | null | undefined): string {
  if (n == null) return 'text-text-muted'
  return n > 0 ? 'text-up' : n < 0 ? 'text-down' : 'text-text-muted'
}
