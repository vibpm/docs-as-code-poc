# GitLab configuration

## 1. Repository

Create:

CLIENT_GROUP/docs-as-code-poc

Push this repository to it.

---

## 2. OAuth Application

Create a GitLab OAuth application for Decap CMS.

Redirect URI must correspond to the deployed CMS URL.

Example:

https://docs.example.com/admin/

Use Authorization Code / PKCE compatible configuration.

Put only the public Application ID into:

static/admin/config.yml

Never put the OAuth client secret into the repository or browser configuration.

---

## 3. Decap configuration

Update:

static/admin/config.yml

Values:

repo
api_root
base_url
auth_endpoint
app_id

Example:

repo: client/docs-as-code-poc
api_root: https://gitlab.client.example/api/v4
base_url: https://gitlab.client.example

---

## 4. Protected main

Protect:

main

Recommended:

Direct push: disabled
Force push: disabled
Merge only through Merge Request
Successful pipeline required
Resolved discussions required

Where GitLab edition supports it:

Required approvals
CODEOWNERS approvals

---

## 5. Roles

Author:
- edit through Decap
- create draft
- submit for review

Reviewer:
- review MR
- inspect impact report
- inspect Review App

Approver:
- approve MR
- merge to main

Production deployment:
- protected environment

---

## 6. CI variables

Configure protected/masked variables as required by deployment adapter.

Examples:

PREVIEW_HOST
PREVIEW_SSH_KEY
PRODUCTION_HOST
PRODUCTION_SSH_KEY

Do not store secrets in repository files.
