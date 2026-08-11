'use strict';

/**
 * Genesis System3 public PAPER dashboard synthetic.
 *
 * Safety invariants:
 * - anonymous/read-only only: no login, dashboard API key or broker order call;
 * - trace headers are injected only to the configured System3 origin;
 * - HAR is scrubbed before upload: no bodies, cookies, query values or
 *   sensitive header values are retained;
 * - LIVE/mutation authority is never exercised.
 */

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

function redactHeaders(headers) {
  const out = {};
  for (const [name, value] of Object.entries(headers || {})) {
    out[name] = SENSITIVE_HEADER.test(name) ? '<redacted>' : String(value).slice(0, 500);
  }
  return out;
}

function scrubHar(har) {
  const clone = JSON.parse(JSON.stringify(har || {}));
  const entries = (((clone || {}).log || {}).entries || []);
  for (const entry of entries) {
    const req = entry.request || {};
    const res = entry.response || {};
    req.url = safeUrl(req.url || '');
    req.headers = (req.headers || []).map((h) => ({
      name: h.name,
      value: SENSITIVE_HEADER.test(h.name || '') ? '<redacted>' : String(h.value || '').slice(0, 500),
    }));
    req.cookies = [];
    req.queryString = [];
    delete req.postData;

    res.headers = (res.headers || []).map((h) => ({
      name: h.name,
      value: SENSITIVE_HEADER.test(h.name || '') ? '<redacted>' : String(h.value || '').slice(0, 500),
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
  const bytes = fs.readFileSync(localPath);
  const url = `https://storage.googleapis.com/upload/storage/v1/b/${encodeURIComponent(BUCKET)}/o?uploadType=media&name=${encodeURIComponent(objectName)}`;
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': contentType || 'application/octet-stream',
    },
    body: bytes,
  });
  if (!response.ok) throw new Error(`gcs_upload_http_${response.status}:${objectName}`);
}

function utcParts(date = new Date()) {
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
  const tracePath = path.join(outDir, 'trace.zip');
  const screenshotPath = path.join(outDir, 'failure.png');
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
      let sameOrigin = false;
      try { sameOrigin = new URL(req.url()).origin === SERVICE_ORIGIN; } catch (_) {}
      if (!sameOrigin) return route.continue();
      return route.continue({
        headers: {
          ...req.headers(),
          'x-trace-id': traceId,
          traceparent,
        },
      });
    });

    page.on('console', (msg) => {
      if (msg.type() === 'error' || msg.type() === 'warning') {
        consoleRows.push({ type: msg.type(), text: msg.text().slice(0, 1000) });
      }
    });
    page.on('pageerror', (err) => {
      consoleRows.push({ type: 'pageerror', text: String(err.message || err).slice(0, 1000) });
    });
    page.on('requestfailed', (req) => {
      networkRows.push({
        name: safeUrl(req.url()),
        method: req.method(),
        status: null,
        failed: true,
        failure: String((req.failure() || {}).errorText || 'request_failed').slice(0, 300),
      });
    });
    page.on('response', async (res) => {
      const req = res.request();
      if (new URL(req.url()).origin !== SERVICE_ORIGIN) return;
      const responseHeaders = await res.allHeaders().catch(() => ({}));
      const requestHeaders = await req.allHeaders().catch(() => ({}));
      servingRevision = responseHeaders['x-system3-revision'] || servingRevision;
      deploymentTag = responseHeaders['x-system3-deploy-sha'] || deploymentTag;
      const timing = req.timing();
      networkRows.push({
        name: safeUrl(req.url()),
        method: req.method(),
        status: res.status(),
        size: Number(responseHeaders['content-length'] || 0) || null,
        time_ms: timing && timing.responseEnd >= 0 ? Math.round(timing.responseEnd) : null,
        request_headers: redactHeaders(requestHeaders),
        response_headers: redactHeaders(responseHeaders),
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
      async function getJson(path) {
        const response = await fetch(path, { method: 'GET', credentials: 'omit' });
        let body = {};
        try { body = await response.json(); } catch (_) {}
        return { status: response.status, body };
      }
      return {
        auth: await getJson('/api/auth/status'),
        health: await getJson('/api/health'),
        state: await getJson('/api/state'),
        mutation: await getJson('/api/security/mutation-policy'),
      };
    });

    for (const [name, result] of Object.entries(checks)) {
      if (result.status !== 200) failures.push(`${name}_http_${result.status}`);
    }
    if (checks.auth.body.required !== false || checks.auth.body.mode !== 'auth_disabled') failures.push('public_dashboard_auth_contract_failed');
    if (checks.mutation.body.state !== 'ENFORCED') failures.push('mutation_policy_not_enforced');
    if (checks.mutation.body.live_mutation !== 'HARD_DENY') failures.push('live_mutation_not_hard_deny');
    if (checks.mutation.body.public_dashboard_read_only !== true) failures.push('dashboard_not_read_only');

    if (consoleRows.some((row) => row.type === 'pageerror')) failures.push('browser_pageerror');
    if (networkRows.some((row) => row.status >= 500)) failures.push('backend_5xx_observed');
  } catch (err) {
    failures.push(`synthetic_exception:${err && err.name ? err.name : 'Error'}:${String(err && err.message ? err.message : err).slice(0, 300)}`);
  } finally {
    if (context) {
      if (failures.length) {
        const pages = context.pages();
        if (pages[0] && !pages[0].isClosed()) await pages[0].screenshot({ path: screenshotPath, fullPage: true }).catch(() => {});
        await context.tracing.stop({ path: tracePath }).catch(() => {});
      } else {
        await context.tracing.stop().catch(() => {});
      }
      await context.close().catch(() => {}); // flush HAR
    }
    if (browser) await browser.close().catch(() => {});
  }

  const ended = new Date();
  const redactedHarPath = path.join(outDir, 'redacted.har.json');
  if (fs.existsSync(rawHarPath)) {
    try {
      const har = JSON.parse(fs.readFileSync(rawHarPath, 'utf8'));
      fs.writeFileSync(redactedHarPath, JSON.stringify(scrubHar(har)));
    } catch (err) {
      failures.push(`har_redaction_failed:${String(err.message || err).slice(0, 200)}`);
    }
    fs.rmSync(rawHarPath, { force: true });
  }

  const meta = {
    schema_version: 1,
    trace_id: traceId,
    traceparent,
    timestamp: started.toISOString(),
    completed_at: ended.toISOString(),
    duration_ms: ended.getTime() - started.getTime(),
    env: ENV,
    service: SERVICE,
    service_origin: SERVICE_ORIGIN,
    deployment_tag: deploymentTag,
    serving_revision: servingRevision,
    status: failures.length ? 'FAIL' : 'PASS',
    failures,
    console_error_or_warning_count: consoleRows.length,
    network_request_count: networkRows.length,
    dashboard_api_key_used: false,
    broker_order_called: false,
    live_trading_enabled: false,
    request_response_bodies_persisted: false,
    cookies_persisted: false,
    query_values_persisted: false,
  };

  const metaPath = path.join(outDir, 'meta.json');
  const consolePath = path.join(outDir, 'console.json');
  const networkPath = path.join(outDir, 'network.json');
  fs.writeFileSync(metaPath, JSON.stringify(meta, null, 2));
  fs.writeFileSync(consolePath, JSON.stringify(consoleRows, null, 2));
  fs.writeFileSync(networkPath, JSON.stringify(networkRows, null, 2));

  const sampledSuccess = !failures.length && Math.random() < SUCCESS_SAMPLE_RATE;
  const shouldUpload = failures.length > 0 || sampledSuccess;
  if (shouldUpload) {
    try {
      const token = await metadataAccessToken();
      const { yyyy, mm, dd } = utcParts(started);
      const prefix = `har/${ENV}/${SERVICE}/${yyyy}/${mm}/${dd}/${traceId}`;
      const files = [
        [metaPath, `${prefix}/meta.json`, 'application/json'],
        [consolePath, `${prefix}/console.json`, 'application/json'],
        [networkPath, `${prefix}/network.json`, 'application/json'],
      ];
      if (fs.existsSync(redactedHarPath)) files.push([redactedHarPath, `${prefix}/redacted.har.json`, 'application/json']);
      if (fs.existsSync(tracePath)) files.push([tracePath, `${prefix}/trace.zip`, 'application/zip']);
      if (fs.existsSync(screenshotPath)) files.push([screenshotPath, `${prefix}/failure.png`, 'image/png']);
      for (const [local, objectName, contentType] of files) await uploadFile(token, local, objectName, contentType);
      meta.gcs_prefix = `gs://${BUCKET}/${prefix}/`;
      fs.writeFileSync(metaPath, JSON.stringify(meta, null, 2));
    } catch (err) {
      meta.upload_error = String(err.message || err).slice(0, 300);
      fs.writeFileSync(metaPath, JSON.stringify(meta, null, 2));
      if (UPLOAD_REQUIRED) failures.push(`artifact_upload_failed:${meta.upload_error}`);
    }
  }

  console.log('SYSTEM3_SYNTHETIC', JSON.stringify(meta));
  process.exitCode = failures.length ? 2 : 0;
}

run().catch((err) => {
  console.error('SYSTEM3_SYNTHETIC_FATAL', String(err && err.message ? err.message : err).slice(0, 500));
  process.exitCode = 3;
});
