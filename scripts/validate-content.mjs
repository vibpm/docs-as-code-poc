import fs from 'fs';
import path from 'path';
import yaml from 'js-yaml';
import matter from 'gray-matter';
import Ajv2020 from 'ajv/dist/2020.js';
import addFormats from 'ajv-formats';

const ajv = new Ajv2020({
  allErrors: true,
  strict: false
});

addFormats(ajv);

const blockSchema =
  JSON.parse(fs.readFileSync('schemas/block.schema.json'));

const documentSchema =
  JSON.parse(fs.readFileSync('schemas/document.schema.json'));

const validateBlock = ajv.compile(blockSchema);
const validateDocument = ajv.compile(documentSchema);

const ids = new Set();
const series = new Map();

function fail(message) {
  console.error(`ERROR: ${message}`);
  process.exitCode = 1;
}

function asDateString(value) {
  if (value instanceof Date) {
    return value.toISOString().substring(0, 10);
  }
  return value;
}

function normalizeMetadata(data) {
  return {
    ...data,
    valid_from: asDateString(data.valid_from),
    valid_to: asDateString(data.valid_to)
  };
}

for (const file of fs.readdirSync('content/blocks')) {

  if (!file.endsWith('.mdx')) continue;

  const full = path.join('content/blocks', file);
  const parsed = matter(fs.readFileSync(full, 'utf8'));
  const data = normalizeMetadata(parsed.data);

  if (!validateBlock(data)) {
    fail(`${file}: ${ajv.errorsText(validateBlock.errors)}`);
  }

  if (ids.has(data.id)) {
    fail(`Duplicate stable ID: ${data.id}`);
  }

  ids.add(data.id);

  const list = series.get(data.series_id) || [];
  list.push(data);
  series.set(data.series_id, list);
}

for (const [seriesId, revisions] of series.entries()) {

  revisions.sort(
    (a, b) =>
      new Date(a.valid_from) - new Date(b.valid_from)
  );

  for (let i = 0; i < revisions.length - 1; i++) {

    const current = revisions[i];
    const next = revisions[i + 1];

    if (!current.valid_to) {
      fail(
        `${seriesId}: open-ended revision ${current.id} overlaps ${next.id}`
      );
      continue;
    }

    if (
      new Date(current.valid_to) >=
      new Date(next.valid_from)
    ) {
      fail(
        `${seriesId}: effective date overlap between ` +
        `${current.id} and ${next.id}`
      );
    }
  }
}

for (const file of fs.readdirSync('content/documents')) {

  if (!file.endsWith('.yml')) continue;

  const full = path.join('content/documents', file);
  const doc = normalizeMetadata(
    yaml.load(fs.readFileSync(full, 'utf8'))
  );

  if (!validateDocument(doc)) {
    fail(`${file}: ${ajv.errorsText(validateDocument.errors)}`);
  }

  if (ids.has(doc.id)) {
    fail(`Duplicate stable ID: ${doc.id}`);
  }

  ids.add(doc.id);
}

if (process.exitCode) {
  process.exit(process.exitCode);
}

console.log('Content validation OK');
