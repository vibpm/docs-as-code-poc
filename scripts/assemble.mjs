import fs from 'fs';
import path from 'path';
import yaml from 'js-yaml';
import matter from 'gray-matter';

const asOf =
  new Date(
    process.env.CONTENT_AS_OF ||
    new Date().toISOString().substring(0, 10)
  );

const blocks = new Map();

for (const file of fs.readdirSync('content/blocks')) {

  if (!file.endsWith('.mdx')) continue;

  const parsed = matter(
    fs.readFileSync(
      path.join('content/blocks', file),
      'utf8'
    )
  );

  const data = parsed.data;

  const from = new Date(data.valid_from);
  const to = data.valid_to
    ? new Date(data.valid_to)
    : new Date('9999-12-31');

  if (from <= asOf && asOf <= to) {

    if (blocks.has(data.series_id)) {
      throw new Error(
        `Ambiguous effective revision for ${data.series_id}`
      );
    }

    blocks.set(data.series_id, {
      metadata: data,
      body: parsed.content.trim()
    });
  }
}

fs.rmSync('generated/docs', {
  recursive: true,
  force: true
});

fs.mkdirSync('generated/docs', {
  recursive: true
});

const catalog = [];

for (const file of fs.readdirSync('content/documents')) {

  if (!file.endsWith('.yml')) continue;

  const doc = yaml.load(
    fs.readFileSync(
      path.join('content/documents', file),
      'utf8'
    )
  );

  let output = `---
id: ${doc.id}
title: "${doc.title}"
---

# ${doc.title}

<div className="effective-notice">

**Состояние контента на:** ${asOf.toISOString().substring(0,10)}

</div>

`;

  const provenance = [];

  for (const section of doc.sections || []) {

    output += `## ${section.heading}\n\n`;

    if (section.body) {
      output += `${section.body}\n\n`;
    }

    if (section.block_ref) {

      const block = blocks.get(section.block_ref);

      if (!block) {
        throw new Error(
          `No effective block for ${section.block_ref} ` +
          `used by ${doc.id}`
        );
      }

      provenance.push(block.metadata.id);

      output += `<div className="shared-block">\n\n`;
      output += block.body;
      output += `\n\n</div>\n\n`;
    }
  }

  output += `
<div className="provenance">

**Document ID:** ${doc.id}

**Shared content:** ${provenance.join(', ') || 'none'}

**Build commit:** ${process.env.CI_COMMIT_SHA || 'local'}

</div>
`;

  fs.writeFileSync(
    `generated/docs/${doc.id}.mdx`,
    output
  );

  catalog.push({
    id: doc.id,
    title: doc.title
  });
}

catalog.sort((a, b) => a.title.localeCompare(b.title, 'ru'));

const asOfLabel = asOf.toISOString().substring(0, 10);

let index = `---
id: index
slug: /
title: Regulatory Content Platform
---

# Regulatory Content Platform

<div className="effective-notice">

**Состояние контента на:** ${asOfLabel}

</div>

Собранные документы:

`;

for (const item of catalog) {
  index += `- [${item.title}](/${item.id})\n`;
}

fs.writeFileSync('generated/docs/index.mdx', index);

console.log(
  `Documents assembled for ${asOfLabel}`
);
