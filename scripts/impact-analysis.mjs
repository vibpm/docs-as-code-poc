import fs from 'fs';

const graph = JSON.parse(
  fs.readFileSync(
    'generated/dependency-graph.json',
    'utf8'
  )
);

const changed =
  (process.env.CHANGED_BLOCKS || '')
    .split(',')
    .map(x => x.trim())
    .filter(Boolean);

const affected = new Set();

for (const block of changed) {

  const entry = graph.blocks[block];

  if (!entry) continue;

  for (const doc of entry.usedBy) {
    affected.add(doc);
  }
}

const report = {
  changedBlocks: changed,
  affectedDocuments: [...affected]
};

fs.writeFileSync(
  'generated/impact-report.json',
  JSON.stringify(report, null, 2)
);

console.log(JSON.stringify(report, null, 2));
