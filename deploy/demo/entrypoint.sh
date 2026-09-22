#!/bin/sh
set -eu

SITE_URL="${SITE_URL:-http://localhost:8080}"
BRANCH="${CONTENT_BRANCH:-master}"

mkdir -p /app/content/blocks /app/content/documents /app/static/admin /app/build/admin /app/generated /app/static/uploads

write_cms_config() {
  cat > /app/static/admin/config.yml <<EOF
backend:
  name: proxy
  proxy_url: ${SITE_URL}/api/v1
  branch: ${BRANCH}

media_folder: static/uploads
public_folder: /uploads

collections:
  - name: blocks
    label: Общие нормативные блоки
    folder: content/blocks
    create: true
    extension: mdx
    format: frontmatter
    identifier_field: id
    fields:
      - { label: Stable ID, name: id, widget: string }
      - { label: Series ID, name: series_id, widget: string }
      - { label: Название, name: title, widget: string }
      - { label: Content Type, name: content_type, widget: hidden, default: regulatory_block }
      - { label: Jurisdiction, name: jurisdiction, widget: string }
      - { label: Owner, name: owner, widget: string }
      - { label: Approver, name: approver, widget: string }
      - { label: Lifecycle, name: lifecycle, widget: select, options: [draft, approved, effective, retired] }
      - { label: Valid From, name: valid_from, widget: datetime, date_format: YYYY-MM-DD, time_format: false }
      - { label: Valid To, name: valid_to, widget: datetime, required: false, date_format: YYYY-MM-DD, time_format: false }
      - { label: Topics, name: topics, widget: list }
      - { label: Текст, name: body, widget: markdown }

  - name: documents
    label: Документы
    folder: content/documents
    create: true
    extension: yml
    format: yaml
    identifier_field: id
    fields:
      - { label: Stable ID, name: id, widget: string }
      - { label: Название, name: title, widget: string }
      - { label: Content Type, name: content_type, widget: hidden, default: assembled_document }
      - { label: Owner, name: owner, widget: string }
      - { label: Approver, name: approver, widget: string }
      - { label: Lifecycle, name: lifecycle, widget: select, options: [draft, approved, effective, retired] }
      - { label: Valid From, name: valid_from, widget: datetime, date_format: YYYY-MM-DD, time_format: false }
      - { label: Sections, name: sections, widget: list, fields: [
            { label: Heading, name: heading, widget: string },
            { label: Local text, name: body, widget: markdown, required: false },
            { label: Shared block, name: block_ref, widget: string, required: false },
            { label: File ref, name: file_ref, widget: string, required: false }
          ] }
EOF
  cp /app/static/admin/index.html /app/build/admin/index.html
  cp /app/static/admin/config.yml /app/build/admin/config.yml
}

content_hash() {
  find /app/content -type f -print0 2>/dev/null | sort -z | xargs -0 cat 2>/dev/null | sha256sum | awk '{print $1}'
}

write_cms_config
echo "[demo] SITE_URL=${SITE_URL}"

cd /app
(
  echo "[demo] CMS proxy on 127.0.0.1:8081"
  PORT=8081 BIND_HOST=127.0.0.1 npx --yes decap-server
) &

(
  PREV="$(content_hash)"
  echo "[demo] watching content/ (hash=${PREV})"
  while true; do
    sleep 4
    CUR="$(content_hash)"
    if [ "$CUR" != "$PREV" ]; then
      echo "[demo] content changed → rebuild"
      CONTENT_AS_OF="${CONTENT_AS_OF:-$(date -u +%Y-%m-%d)}" npm run build \
        && write_cms_config \
        && echo "[demo] rebuild OK" \
        || echo "[demo] rebuild FAILED"
      PREV="$(content_hash)"
    fi
  done
) &

exec nginx -g 'daemon off;'
