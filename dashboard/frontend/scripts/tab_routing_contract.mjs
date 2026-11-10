// Static release gate: every UI navigation tab must have an explicit component route.
// Runtime browser tests remain required separately; this gate prevents silent tab loss.
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

const src = join(dirname(fileURLToPath(import.meta.url)), '..', 'src')
const sidebar = readFileSync(join(src, 'components', 'Sidebar.tsx'), 'utf8')
const app = readFileSync(join(src, 'App.tsx'), 'utf8')
const config = JSON.parse(readFileSync(join(src, '..', 'tsconfig.json'), 'utf8'))

const nav = sidebar.split('export const DASHBOARD_TABS = [')[1]?.split('] as const')[0]
assert.ok(nav, 'Sidebar canonical navigation catalog missing')
const tabs = [...nav.matchAll(/\bid:\s*'([^']+)'/g)].map(m => m[1])
assert.equal(tabs.length, 24, 'Genesis UI must expose exactly 24 navigation tabs')
assert.equal(new Set(tabs).size, tabs.length, 'Duplicate tab IDs are not allowed')

const content = app.split('function Content()')[1]?.split('function DashboardTabUrlSync()')[0]
assert.ok(content, 'App tab dispatch function missing')
const routes = [...content.matchAll(/case\s+'([^']+)'\s*:/g)].map(m => m[1])
assert.deepEqual([...routes].sort(), [...tabs].sort(), 'Every navigation tab must have an explicit route')
assert.ok(tabs.includes('mobile-trader'), 'Mobile Trader must be reachable in standard navigation')
assert.match(app, /view'\)\s*===\s*'mobile-trader'/, 'Standalone mobile route must remain available')
assert.equal(config.compilerOptions.strict, true, 'Keep TypeScript strict checking enabled')
assert.equal(config.compilerOptions.noImplicitAny, true, 'Keep TypeScript noImplicitAny enabled')
console.log('PASS: 24 unique navigation tabs, 24 explicit routes, standalone mobile route and strict TS')
