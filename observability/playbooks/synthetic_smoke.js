'use strict';

/** Genesis System3 public PAPER dashboard synthetic. Read-only by design. */
const { chromium } = require('@playwright/test');
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

const SERVICE_URL = (process.env.SERVICE_URL || 'https://genesis-system3-web-doq2wplepa-el.a.run.app').replace(/\/$/, '');
const SERVICE_ORIGIN = new URL(SERVICE_URL).origin;
const ENV = process.env.SYSTEM3_ENV || 'prod';
const SERVICE = process.env.SERVICE_NAME || 'genesis-system3-web';
const BUCKET = process.env.OBSERVABILITY_BUCKET || 'system3-observability-artifacts';
const UPLOAD_REQUIRED = /^(1|true|yes)$/i.test(process.env.OBSERVABILITY_UPLOAD_REQUIRED || '0');
const SUCCESS_SAMPLE_RATE = Math.max(0, Math.min(1, Number(process.env.SUCCESS_SAMPLE_RATE || '0.02')));
const OUT_ROOT = process.env.SYNTHETIC_OUT_DIR || '/tmp/system3-synthetic';
const SENSITIVE_HEADER = /authorization|cookie|token|api[-_]?key|password|pin|totp|secret|session/i;
const SECRET_TEXT_PATTERNS = [
  /\bBearer\s+[^\s,;]+/gi,
  /\beyJ[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{8,}\b/g,
  /((?:api[-_ ]?key|access[-_ ]?token|refresh[-_ ]?token|password|pin|totp|secret|session)\s*[:=]\s*)[^\s,;]+/gi,
];

function redactText(value, limit = 1000) {
  let text = String(value || '');
  for (const pattern of SECRET_TEXT_PATTERNS) {
    text = text.replace(pattern, (match, prefix) => prefix ? `${prefix}<redacted>` : '<redacted>');
  }
  return text.slice(0, limit);
}

function traceContext() {
  const traceId = crypto.randomBytes(16).toString('hex');
  const parentSpanId = crypto.randomBytes(8).toString('hex');
  return { traceId, traceparent: `00-${traceId}-${parentSpanId}-01` };
}

function safeUrl(raw) {
  try {
    const u = new URL(raw);
    return `${u.origin}${u.pathname}`;
  } catch (_) {
    return '<invalid-url>';
  }
}

function sameServiceOrigin(raw) {
  try { return new URL(raw).origin === SERVICE_ORIGIN; } catch (_) { return false; }
}

function redactHeaders(headers) {
  const out = {};
  for (const [name, value] of Object.entries(headers || {})) {
    out[name] = SENSITIVE_HEADER.test(name) ? '<redacted>' : redactText(value, 500);
  }
  return out;
}

function scrubHar(har) {
  const clone = JSON.parse(JSON.stringify(har || {}));
  for (const entry of (((clone || {}).log || {}).entries || [])) {
    const req = entry.request || {};
    const res = entry.response || {};
    req.url = safeUrl(req.url || '');
    req.headers = (req.headers || []).map((h) => ({
      name: h.name,
      value: SENSITIVE_HEADER.test(h.name || '') ? '<redacted>' : redactText(h.value, 500),
    }));
    req.cookies = [];
    req.queryString = [];
    delete req.postData;
    res.headers = (res.headers || []).map((h) => ({
      name: h.name,
      value: SENSITIVE_HEADER.test(h.name || '') ? '<redacted>' : redactText(h.value, 500),
    }));
    res.cookies = [];
    if (res.content) {
      delete res.content.text;
      delete res.content._file;
    }
  }
  return clone;
}

async function metadataAccessToken() {
  const response = await fetch(
    'http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token',
    { headers: { 'Metadata-Flavor': 'Google' } },
  );
  if (!response.ok) throw new Error(`metadata_token_http_${response.status}`);
  const body = await response.json();
  if (!body.access_token) throw new Error('metadata_access_token_missing');
  return body.access_token;
}

async function uploadFile(token, localPath, objectName, contentType) {
  const response = await fetch(
    `https://storage.googleapis.com/upload/storage/v1/b/${encodeURIComponent(BUCKET)}/o?uploadType=media&name=${encodeURIComponent(objectName)}`,
    {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': contentType || 'application/octet-stream' },
      body: fs.readFileSync(localPath),
    },
  );
  if (!response.ok) throw new Error(`gcs_upload_http_${response.status}:${objectName}`);
}

function utcParts(date) {
  return {
    yyyy: String(date.getUTCFullYear()),
    mm: String(date.getUTCMonth() + 1).padStart(2, '0'),
    dd: String(date.getUTCDate()).padStart(2, '0'),
  };
}

async function run() {
  const started = new Date();
  const { traceId, traceparent } = traceContext();
  const outDir = path.join(OUT_ROOT, traceId);
  fs.mkdirSync(outDir, { recursive: true });
  const rawHarPath = path.join(outDir, 'raw.har');
  const redactedHarPath = path.join(outDir, 'redacted.har.json');
  const tracePath = path.join(outDir, 'trace.zip');
  const screenshotPath = path.join(outDir, 'failure.png');
  const metaPath = path.join(outDir, 'meta.json');
  const consolePath = path.join(outDir, 'console.json');
  const networkPath = path.join(outDir, 'network.json');
  const consoleRows = [];
  const networkRows = [];
  const failures = [];
  let servingRevision = 'unknown';
  let deploymentTag = 'unknown';
  let browser;
  let context;

  try {
    browser = await chromium.launch({ headless: true });
    context = await browser.newContext({
      recordHar: { path: rawHarPath, content: 'omit', mode: 'full' },
      viewport: { width: 1600, height: 1000 },
    });
    await context.tracing.start({ screenshots: true, snapshots: true, sources: false });
    const page = await context.newPage();

    await page.route('**/*', async (route) => {
      const req = route.request();
      if (!sameServiceOrigin(req.url())) return route.continue();
      return route.continue({ headers: { ...req.headers(), 'x-trace-id': traceId, traceparent } });
    });

    page.on('console', (msg) => {
      if (msg.type() === 'error' || msg.type() === 'warning') {
        consoleRows.push({ type: msg.type(), text: redactText(msg.text()) });
      }
    });
    page.on('pageerror', (err) => consoleRows.push({ type: 'pageerror', text: redactText(err.message || err) }));
    page.on('requestfailed', (req) => networkRows.push({
      name: safeUrl(req.url()), method: req.method(), status: null, failed: true,
      failure: redactText((req.failure() || {}).errorText || 'request_failed', 300),
    }));
    page.on('response', async (res) => {
      const req = res.request();
      if (!sameServiceOrigin(req.url())) return;
      const responseHeaders = await res.allHeaders().catch(() => ({}));
      const requestHeaders = await req.allHeaders().catch(() => ({}));
      servingRevision = responseHeaders['x-system3-revision'] || servingRevision;
      deploymentTag = responseHeaders['x-system3-deploy-sha'] || deploymentTag;
      const timing = req.timing() || {};
      const elapsed = timing.responseEnd >= 0 && timing.startTime >= 0
        ? Math.max(0, Math.round(timing.responseEnd - timing.startTime)) : null;
      networkRows.push({
        name: safeUrl(req.url()), method: req.method(), status: res.status(),
        size: Number(responseHeaders['content-length'] || 0) || null,
        time_ms: elapsed,
        request_headers: redactHeaders(requestHeaders), response_headers: redactHeaders(responseHeaders),
      });
    });

    const ui = await page.goto(`${SERVICE_URL}/ui`, { waitUntil: 'networkidle', timeout: 60000 });
    if (!ui || ui.status() !== 200) failures.push(`ui_http_${ui ? ui.status() : 'no_response'}`);
    await page.waitForTimeout(1500);
    const body = await page.locator('body').innerText().catch(() => '');
    if (!/SYSTEM3/i.test(body)) failures.push('system3_marker_missing');
    if (!/PAPER/i.test(body)) failures.push('paper_marker_missing');
    if (!/LIVE OFF/i.test(body)) failures.push('live_off_marker_missing');
    if (/DASHBOARD API KEY/i.test(body)) failures.push('dashboard_api_key_prompt_rendered');

    const checks = await page.evaluate(async () => {
      async function getJson(url) {
        const response = await fetch(url, { method: 'GET', credentials: 'omit' });
        let body = {};
        try { body = await response.json(); } catch (_) {}
        return { status: response.status, body };
      }
      return {
        auth: await getJson('/api/auth/status'), health: await getJson('/api/health'),
        state: await getJson('/api/state'), mutation: await getJson('/api/security/mutation-policy'),
      };
    });
    for (const [name, result] of Object.entries(checks)) if (result.status !== 200) failures.push(`${name}_http_${result.status}`);
    if (checks.auth.body.required !== false || checks.auth.body.mode !== 'auth_disabled') failures.push('public_dashboard_auth_contract_failed');
    if (checks.mutation.body.state !== 'ENFORCED') failures.push('mutation_policy_not_enforced');
    if (checks.mutation.body.live_mutation !== 'HARD_DENY') failures.push('live_mutation_not_hard_deny');
    if (checks.mutation.body.public_dashboard_read_only !== true) failures.push('dashboard_not_read_only');
    if (consoleRows.some((row) => row.type === 'pageerror')) failures.push('browser_pageerror');
    if (networkRows.some((row) => Number(row.status || 0) >= 500)) failures.push('backend_5xx_observed');
  } catch (err) {
    failures.push(`synthetic_exception:${redactText(`${err && err.name ? err.name : 'Error'}:${err && err.message ? err.message : err}`, 300)}`);
  } finally {
    if (context) {
      if (failures.length) {
        const pages = context.pages();
        if (pages[0] && !pages[0].isClosed()) await pages[0].screenshot({ path: screenshotPath, fullPage: true }).catch(() => {});
        await context.tracing.stop({ path: tracePath }).catch(() => {});
      } else {
        await context.tracing.stop().catch(() => {});
      }
      await context.close().catch(() => {});
    }
    if (browser) await browser.close().catch(() => {});
  }

  if (fs.existsSync(rawHarPath)) {
    try {
      const har = JSON.parse(fs.readFileSync(rawHarPath, 'utf8'));
      fs.writeFileSync(redactedHarPath, JSON.stringify(scrubHar(har)));
    } catch (err) {
      failures.push(`har_redaction_failed:${redactText(err.message || err, 200)}`);
    }
    fs.rmSync(rawHarPath, { force: true });
  }

  const meta = {
    schema_version: 1, trace_id: traceId, traceparent, timestamp: started.toISOString(),
    completed_at: new Date().toISOString(), env: ENV, service: SERVICE, service_origin: SERVICE_ORIGIN,
    deployment_tag: deploymentTag, serving_revision: servingRevision,
    failures, console_error_or_warning_count: consoleRows.length, network_request_count: networkRows.length,
    dashboard_api_key_used: false, broker_order_called: false, live_trading_enabled: false,
    request_response_bodies_persisted: false, cookies_persisted: false, query_values_persisted: false,
  };
  meta.duration_ms = new Date(meta.completed_at).getTime() - started.getTime();
  fs.writeFileSync(consolePath, JSON.stringify(consoleRows, null, 2));
  fs.writeFileSync(networkPath, JSON.stringify(networkRows, null, 2));

  const sampledSuccess = !failures.length && Math.random() < SUCCESS_SAMPLE_RATE;
  const shouldUpload = failures.length > 0 || sampledSuccess;
  let token = null;
  let prefix = null;
  if (shouldUpload) {
    try {
      token = await metadataAccessToken();
      const { yyyy, mm, dd } = utcParts(started);
      prefix = `har/${ENV}/${SERVICE}/${yyyy}/${mm}/${dd}/${traceId}`;
      meta.gcs_prefix = `gs://${BUCKET}/${prefix}/`;
      const files = [
        [consolePath, `${prefix}/console.json`, 'application/json'],
        [networkPath, `${prefix}/network.json`, 'application/json'],
      ];
      if (fs.existsSync(redactedHarPath)) files.push([redactedHarPath, `${prefix}/redacted.har.json`, 'application/json']);
      if (fs.existsSync(tracePath)) files.push([tracePath, `${prefix}/trace.zip`, 'application/zip']);
      if (fs.existsSync(screenshotPath)) files.push([screenshotPath, `${prefix}/failure.png`, 'image/png']);
      for (const [local, objectName, contentType] of files) await uploadFile(token, local, objectName, contentType);
    } catch (err) {
      meta.upload_error = redactText(err.message || err, 300);
      if (UPLOAD_REQUIRED) failures.push(`artifact_upload_failed:${meta.upload_error}`);
    }
  }

  meta.status = failures.length ? 'FAIL' : 'PASS';
  meta.failures = failures;
  fs.writeFileSync(metaPath, JSON.stringify(meta, null, 2));
  if (token && prefix) {
    try {
      await uploadFile(token, metaPath, `${prefix}/meta.json`, 'application/json');
    } catch (err) {
      meta.upload_error = redactText(err.message || err, 300);
      if (UPLOAD_REQUIRED && !failures.some((x) => x.startsWith('artifact_upload_failed:'))) {
        failures.push(`artifact_upload_failed:${meta.upload_error}`);
      }
      meta.status = failures.length ? 'FAIL' : 'PASS';
      meta.failures = failures;
      fs.writeFileSync(metaPath, JSON.stringify(meta, null, 2));
    }
  }

  console.log('SYSTEM3_SYNTHETIC', JSON.stringify(meta));
  process.exitCode = failures.length ? 2 : 0;
}

run().catch((err) => {
  console.error('SYSTEM3_SYNTHETIC_FATAL', redactText(err && err.message ? err.message : err, 500));
  process.exitCode = 3;
});
