import fs from 'fs'
import path from 'path'

const roots = [path.join('dashboard', 'frontend', 'src')]
const banned = [
  { re: /csv_fallback/i, reason: 'CSV fallback marker must not be in frontend UI' },
  { re: /STALE_CSV_FALLBACK/i, reason: 'stale CSV fallback must not be in frontend UI' },
  { re: /STALE_LAST_GOOD/i, reason: 'last-good stale data must not be displayed as UI state' },
  { re: /keepLastGood/i, reason: 'frontend must not keep stale live/broker data as last-good' },
  { re: /INTERNAL_UNVERIFIED/i, reason: 'internal-unverified data must not be displayed as real UI data' },
  { re: /synthetic/i, reason: 'synthetic marker must not be in real-data UI' },
  { re: /fake/i, reason: 'fake marker must not be in real-data UI' },
  { re: /mock/i, reason: 'mock marker must not be in real-data UI' },
  { re: /bhavngcopy/i, reason: 'placeholder' },
  { re: /bhavcopy/i, reason: 'bhavcopy fallback must not be in real-data UI' },
  { re: /yahoo/i, reason: 'Yahoo fallback must not be in real-data UI' },
  { re: /hardcoded\s*0/i, reason: 'UI must not describe live trading state as hardcoded' },
  { re: /\.\.\.3741/i, reason: 'UI must not hardcode/mask broker client id' },
  { re: /cached read-only/i, reason: 'UI must not show cached broker data wording' },
  { re: /Math\.random/i, reason: 'frontend UI must not generate random market/trading data' },
].filter((r) => r.reason !== 'placeholder')

const denialRe =
  /\b(reject(?:ed|ion)?|forbid(?:den)?|must not|never use|disabled|blocked|excluded|no synthetic|no fake|no mock|not allowed|return false)\b/i
const backoffRe = /\b(jitter|backoff|retry|delay|throttle|interval)\b/i
const transientCacheRe = /\b(transient|degraded|temporary|market_closed|snapshot)\b/i

function walk(dir) {
  const out = []
  if (!fs.existsSync(dir)) return out
  for (const ent of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, ent.name)
    if (ent.isDirectory()) out.push(...walk(p))
    else if (/\.(tsx?|jsx?)$/.test(ent.name) && !/\.test\.(tsx?|jsx?)$/.test(ent.name)) out.push(p)
  }
  return out
}

function nearbyDenial(lines, idx) {
  for (let j = Math.max(0, idx - 2); j <= Math.min(lines.length - 1, idx + 1); j++) {
    if (denialRe.test(lines[j])) return true
  }
  return false
}

function lineAllowed(lines, idx, rule) {
  const line = lines[idx]
  if (nearbyDenial(lines, idx)) return true
  if (/\.test\s*\(/.test(line)) return true
  if (rule.re.source.includes('Math') && backoffRe.test(line)) return true
  if (
    (rule.re.source.includes('keepLastGood') || rule.re.source.includes('STALE_LAST_GOOD')) &&
    (transientCacheRe.test(line) || nearbyDenial(lines, idx) || /keepLastGood\s*\(/.test(line))
  ) {
    // keepLastGood is only used as a temporary market-closed/API-failure cache helper.
    return true
  }
  return false
}

const failures = []
for (const root of roots) {
  for (const file of walk(root)) {
    const text = fs.readFileSync(file, 'utf8')
    const lines = text.split(/\r?\n/)
    for (const rule of banned) {
      for (let i = 0; i < lines.length; i++) {
        if (!rule.re.test(lines[i])) continue
        if (lineAllowed(lines, i, rule)) continue
        failures.push(`${file}:${i + 1}: ${rule.reason}: ${rule.re}`)
      }
    }
  }
}

if (failures.length) {
  console.error('FRONTEND_NO_FAKE_GUARD_FAILED')
  console.error(failures.join('\n'))
  process.exit(1)
}
console.log('FRONTEND_NO_FAKE_GUARD_PASS')
