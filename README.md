# Docs-as-Code PoC

Docusaurus + Decap CMS + GitLab based regulatory content platform.

## Architecture

GitLab
  |
  +-- Repository
  +-- Merge Requests
  +-- CI/CD
  +-- Container Registry
  |
  v
Decap CMS
  |
  v
Content objects
  |
  +-- reusable blocks
  +-- document manifests
  +-- glossary
  +-- taxonomy
  |
  v
Assembler
  |
  +-- dependency graph
  +-- effective-date resolution
  +-- provenance
  |
  v
Docusaurus
  |
  v
Static OCI container
  |
  v
Nginx

## Local start

Install:

    npm install

Build:

    npm run build

Docker:

    docker compose up --build

Open:

    http://localhost:8080

CMS:

    http://localhost:8080/admin/

## Time-travel build

Current content:

    docker compose up --build

Future state:

    CONTENT_AS_OF=2027-01-01 docker compose up --build

This demonstrates future regulatory revisions without long-lived Git branches.

## Dependency graph

    npm run graph

Output:

    generated/dependency-graph.json

## Validation

    npm run validate

## Full build

    npm run build

## GitLab

See:

    GITLAB_SETUP.md

## Colleague demo

Editable demo stack (Basic Auth + CMS + auto-rebuild):

    DEMO.md
    compose.demo.yaml

## FPF (First Principles Framework)

Connected corpus: [ailev/FPF](https://github.com/ailev/FPF) → local `vendor/FPF/` (clone or junction).

Project working publications for the Dismissal Guide:

- CuePack (`A.16.1`): `fpf/cuepacks/hr.dismissal-guide.pre-articulation.cuepack.md`
- ProblemCard Thin (`C.22.2`): `fpf/problem-cards/hr.dismissal-ssot.problem-card.md`

How to use: `fpf/README.md` and `vendor/FPF/USING-FPF.md`.
