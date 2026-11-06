/**
 * Strict flag helpers — replaces `(x as any) === 1` escapes.
 * Keeps `noImplicitAny` + `strict` meaningful while accepting
 * the backend's loose boolean|number|string flags.
 */

export type LiveFlag = boolean | number | string | null | undefined | unknown;

export function isLiveFlagOn(raw: unknown): boolean {
  return raw === true || raw === 1 || raw === '1';
}

export function asRecord(value: unknown): Record<string, unknown> {
  return typeof value === 'object' && value !== null
    ? (value as Record<string, unknown>)
    : {};
}

export function getResponseStatus(reason: unknown): number | null {
  if (typeof reason !== 'object' || reason === null) return null;
  const response = (reason as { response?: unknown }).response;
  if (typeof response !== 'object' || response === null) return null;
  const status = (response as { status?: unknown }).status;
  return typeof status === 'number' ? status : null;
}

export function getErrorMessage(reason: unknown): string {
  if (typeof reason !== 'object' || reason === null) return 'unknown';
  const message = (reason as { message?: unknown }).message;
  return typeof message === 'string' && message ? message : 'unknown';
}

export function gainValue(row: unknown): number {
  const r = asRecord(row);
  const v =
    r['gain_pct'] ?? r['confidence'] ?? r['score'] ?? r['display_score'] ?? 0;
  const n = Number(v);
  return Number.isFinite(n) ? n : 0;
}
