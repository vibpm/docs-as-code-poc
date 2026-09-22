import fs from 'fs';
import path from 'path';
import yaml from 'js-yaml';

fs.mkdirSync('generated', { recursive: true });

const graph = {
  blocks: {},
  documents: {}
};

function link(docId, seriesId) {
  if (!seriesId) return;

  if (!graph.documents[docId].blocks.includes(seriesId)) {
    graph.documents[docId].blocks.push(seriesId);
  }

  graph.blocks[seriesId] ??= { usedBy: [] };

  if (!graph.blocks[seriesId].usedBy.includes(docId)) {
    graph.blocks[seriesId].usedBy.push(docId);
  }
}

function collectMarkers(text, docId) {
  const re = /\{\{block:([a-z0-9._-]+)\}\}/g;
  let match;
  while ((match = re.exec(text)) !== null) {
    link(docId, match[1]);
  }
}

for (const file of fs.readdirSync('content/documents')) {

  if (!file.endsWith('.yml')) continue;

  const doc = yaml.load(
    fs.readFileSync(`content/documents/${file}`, 'utf8')
  );

  graph.documents[doc.id] = {
    title: doc.title,
    blocks: []
  };

  for (const section of doc.sections || []) {

    if (section.block_ref) {
      link(doc.id, section.block_ref);
    }

    if (section.body) {
      collectMarkers(section.body, doc.id);
    }

    if (section.file_ref) {
      const fullPath = path.resolve(section.file_ref);
      if (!fullPath.startsWith(path.resolve('content'))) {
        throw new Error(
          `file_ref must stay under content/: ${section.file_ref}`
        );
      }
      collectMarkers(
        fs.readFileSync(fullPath, 'utf8'),
        doc.id
      );
    }
  }
}

fs.writeFileSync(
  'generated/dependency-graph.json',
  JSON.stringify(graph, null, 2)
);

console.log('Dependency graph generated');

for (const [block, data] of Object.entries(graph.blocks)) {
  console.log(`${block} -> ${data.usedBy.join(', ')}`);
}
