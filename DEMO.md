# Демо для коллег (портал + правки в CMS)

Стек: nginx (Basic Auth) + Decap CMS proxy + авто-пересборка после сохранения.

## Быстрый старт на сервере с Docker

```bash
git clone <repo-url> docs-as-code-poc
cd docs-as-code-poc
cp .env.demo.example .env
# Обязательно укажите публичный URL, с которого заходят коллеги:
# SITE_URL=https://docs-demo.example.com
# DEMO_PASSWORD=...сильный пароль...

docker compose -f compose.demo.yaml --env-file .env up --build -d
```

Открыть:

- Портал: `SITE_URL/`
- CMS: `SITE_URL/admin/`
- Логин (по умолчанию): `demo` / `demo2026`

После правки блока в CMS подождите ~10–30 сек — watcher пересоберёт сайт.

## Что сказать коллегам

1. Зайти по ссылке, ввести логин/пароль демо.
2. Читать путеводитель `/hr.dismissal-guide/`.
3. «Редактировать» → CMS → «Общие нормативные блоки» → изменить текст → Save.
4. Обновить страницу путеводителя через полминуты.

## Важно (demo ≠ production)

- CMS proxy **без GitLab OAuth**: любой, кто знает пароль Basic Auth, может менять файлы.
- Не выставляйте в открытый интернет без смены пароля и без ограничения по IP/VPN.
- Для боевого контура — GitLab/GitHub backend + MR approvals (`GITLAB_SETUP.md`).

## Fly.io (если есть аккаунт)

```bash
flyctl auth login
flyctl launch --dockerfile deploy/demo/Dockerfile.demo --no-deploy
# задать SITE_URL=https://<app>.fly.dev и секреты
flyctl secrets set SITE_URL=https://<app>.fly.dev DEMO_PASSWORD='...'
flyctl deploy --dockerfile deploy/demo/Dockerfile.demo
```

## Нужен хост

Если сервера ещё нет — пришлите один из вариантов:

1. SSH: `user@host` + ключ  
2. Timeweb / VPS с Docker  
3. Подтверждение `flyctl auth login` в браузере
