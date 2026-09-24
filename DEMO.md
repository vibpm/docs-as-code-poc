# Демо-стек (ops)

Стек: nginx (Basic Auth) + Decap CMS proxy + авто-пересборка после сохранения.

**Сопроводительный текст для коллег:** [`ДЛЯ_КОЛЛЕГ.md`](ДЛЯ_КОЛЛЕГ.md)

## Живое демо (Render)

- Портал: https://docs-as-code-poc.onrender.com  
- CMS: https://docs-as-code-poc.onrender.com/admin/  
- Логин: `demo` / `demo2026`

## Локальный запуск Docker

```bash
git clone https://github.com/vibpm/docs-as-code-poc.git
cd docs-as-code-poc
cp .env.demo.example .env
# SITE_URL=http://localhost:8080
# DEMO_PASSWORD=...

docker compose -f compose.demo.yaml --env-file .env up --build -d
```

- Портал: `SITE_URL/`
- CMS: `SITE_URL/admin/`

После правки блока в CMS подождите ~10–30 сек — watcher пересоберёт сайт.

## Важно (demo ≠ production)

- CMS proxy **без GitLab OAuth**: любой, кто знает пароль Basic Auth, может менять файлы.
- Не выставляйте в открытый интернет без смены пароля и без ограничения по IP/VPN.
- Для боевого контура — GitLab/GitHub backend + MR approvals (`GITLAB_SETUP.md`).
