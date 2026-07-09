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
  { re: /bhavcopy/i, reason: 'bhavcopy fallback must not be in real-data UI' },
  { re: /yahoo/i, reason: 'Yahoo fallback must not be in real-data UI' },
  { re: /hardcoded\s*0/i, reason: 'UI must not describe live trading state as hardcoded' },
  { re: /\.\.\.3741/i, reason: 'UI must not hardcode/mask broker client id' },
  { re: /cached read-only/i, reason: 'UI must not show cached broker data wording' },
  { re: /Math\.random/i, reason: 'frontend UI must not generate random market/trading data' },
]

function walk(dir) {
  const out = []
  if (!fs.existsSync(dir)) return out
  for (const ent of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, ent.name)
    if (ent.isDirectory()) out.push(...walk(p))
    else if (/\.(tsx?|jsx?)$/.test(ent.name)) out.push(p)
  }
  return out
}

const failures = []
for (const root of roots) {
  for (const file of walk(root)) {
    const text = fs.readFileSync(file, 'utf8')
    for (const rule of banned) {
      if (rule.re.test(text)) failures.push(`${file}: ${rule.reason}: ${rule.re}`)
    }
  }
}

if (failures.length) {
  console.error('FRONTEND_NO_FAKE_GUARD_FAILED')
  console.error(failures.join('\n'))
  process.exit(1)
}
console.log('FRONTEND_NO_FAKE_GUARD_PASS')
