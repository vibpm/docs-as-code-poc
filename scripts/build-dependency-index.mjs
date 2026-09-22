import fs from 'fs';
import yaml from 'js-yaml';

fs.mkdirSync('generated', { recursive: true });

const graph = {
  blocks: {},
  documents: {}
};

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

    if (!section.block_ref) continue;

    graph.documents[doc.id].blocks.push(section.block_ref);

    graph.blocks[section.block_ref] ??= {
      usedBy: []
    };

    graph.blocks[section.block_ref].usedBy.push(doc.id);
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
