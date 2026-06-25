import { appendFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const hookDir = dirname(fileURLToPath(import.meta.url));
const logDir = join(hookDir, 'logs');
const logFile = join(logDir, 'audit.log');

const payload = await new Response(process.stdin).text();
const timestamp = new Date().toISOString();

mkdirSync(logDir, { recursive: true });
appendFileSync(logFile, `${timestamp} ${payload}\n`);

let parsed;
try {
  parsed = JSON.parse(payload);
} catch {
  parsed = null;
}

if (parsed && typeof parsed.command === 'string') {
  console.log(JSON.stringify({ permission: 'allow' }));
}

