# Absolute Dos and Don'ts for This Fork

Concise reference for coding, commit/PR, UI, i18n, security, and local setup. Distilled from `AGENTS.md`, `CONTRIBUTING.md`, linting docs, the design-system guide, and `.claude` / `.github` conventions.

---

## Local setup (must do)

**Requirements**

- **Node** `>=22.18.0` (enforced in root `package.json`; prefer this over older CONTRIBUTING “20+”)
- **pnpm** `11.3.0` (repo `packageManager`)
- Docker Engine running
- Python 3.8+, Postgres 14, Redis 6.2.7
- **≥12 GB RAM** recommended (8 GB often fails builds)

**Bootstrap**

1. `chmod +x setup.sh && ./setup.sh` — copies `.env.example` → `.env` for root + `apps/{web,api,space,admin,live}`
2. `docker compose -f docker-compose-local.yml up` — infra/API stack
3. `pnpm dev` — web `:3000`, admin `:3001`
4. Register instance admin at `http://localhost:3001/god-mode/`, then log in at `http://localhost:3000`

**Quality gates before you ship**

- `pnpm check` (format + lint + types) or at least `pnpm fix` then `pnpm check:types`
- Backend API tests: `./setup.sh` once, then Docker compose test stack per `AGENTS.md` / `apps/api/tests/RUNNING_TESTS.md`

---

## Coding guidelines — DO

| Area          | Rule                                                                      |
| ------------- | ------------------------------------------------------------------------- |
| Imports       | Internal: `workspace:*`; external: `catalog:`                             |
| TypeScript    | Strict mode; every file typed; prefer modern TS 5.x patterns              |
| Format / lint | **oxfmt** + **OxLint** (single root `.oxlintrc.json`)                     |
| Naming        | camelCase vars/fns; PascalCase components/types                           |
| State         | MobX stores in `packages/shared-state`                                    |
| UI components | Build reusable UI in `@plane/ui` + Storybook                              |
| Tests         | Every feature/bugfix needs unit tests                                     |
| Errors        | try/catch with proper types; log appropriately                            |
| Design tokens | Canvas → Surface → Layer hierarchy (`packages/tailwind-config/AGENTS.md`) |
| Text/borders  | Semantic only: `text-primary/secondary/tertiary`, `border-subtle/strong`  |
| Hover         | Always match base: `bg-layer-X hover:bg-layer-X-hover`                    |

---

## Coding guidelines — DON'T

- Don't invent one-off ESLint configs — OxLint root config only
- Don't suppress lint with `eslint-disable` except sparingly; fix the issue
- Don't use `bg-canvas` except at the **single app root**
- Don't nest surfaces on the same plane (use layers); exception: modals/overlays on another z-plane
- Don't pair `surface-1` with `layer-2` for content cards (only rare form-control separation)
- Don't use mismatched hover classes or bare `bg-layer-X-hover` without `hover:`
- Don't hardcode random colors when semantic tokens exist
- Don't skip tests for features/fixes (`CONTRIBUTING.md`)

---

## Commits, branches, PRs — DO

**Pre-commit (Husky)** — runs automatically on commit:

- oxfmt on staged files
- OxLint `--fix --deny-warnings` on JS/TS

If the hook fails, **fix and commit again** (do not skip hooks).

**Branch names** (from `.claude/skills/branch-name`):

```text
<type>/<work-item-id>-<short-description>
```

Examples: `fix/silo-1146-relative-config-urls`, `feat/web-1234-app-tile-visibility`  
Types: `feat` | `fix` | `chore` | `refactor` | `docs` | `perf`  
Work item ID required (lowercase in branch); don't invent IDs.

**PR conventions** (from `.claude/skills/create-pull-request`):

- Default base branch: **`preview`**
- Title: `[WORK-ITEM-ID] <type>: <summary>` (under ~70 chars)
- Fill `.github/pull_request_template.md`: Description, Type, Screenshots, Test Scenarios, References
- CI on `preview` PRs includes lint/build, copyright (`addlicense` + `COPYRIGHT.txt`), i18n sync when locales change, react-doctor, CodeQL

**Issues** (`CONTRIBUTING.md`): `🐛 Bug: …`, `🚀 Feature: …`, etc.; provide a minimal reproduction for bugs.

---

## Commits / PRs — DON'T

- Don't `--no-verify` / skip Husky unless explicitly required and approved
- Don't commit secrets (`.env`, credentials)
- Don't open a feature PR without a prior proposal/issue when contributing upstream-style features
- Don't leave PR template sections empty / invent irrelevant test scenarios
- Don't target the wrong default base (use `preview` unless told otherwise)
- Don't put work-item ID at the end of the branch name (breaks extraction)

---

## i18n — absolute rules

When touching `packages/i18n/src/locales`:

- **DO** add new keys to **all** locales (English placeholder OK)
- **DO** preserve ICU placeholders, tags, and **full CLDR plural forms** per locale
- **DO NOT** translate brand marks: Plane, Plane AI, Power K, PQL, Intake, Active Cycles, Sticky/Stickies, plan tiers (Pro/Business/Enterprise), third-party names, acronyms
- **DO** translate feature common nouns (Cycle, Module, Epic, Page) per glossary in the translate skill
- Run sync check; CI `i18n-sync-check` will fail on key drift

---

## Security & conduct — DON'T

- Don't file security issues publicly — email **security@plane.so**; keep confidential until fixed
- Don't run automated vuln scans on production infra without consent
- Don't exploit, DDoS, spam, social-engineer, or touch third-party apps while testing
- Don't harass / doxx / use sexualized language in community spaces (`CODE_OF_CONDUCT.md` → squawk@plane.so)

---

## Day-to-day command cheat sheet

```bash
pnpm dev                 # all frontend apps
pnpm check               # format + lint + types
pnpm fix                 # auto-fix format + lint
pnpm check:lint          # OxLint only
pnpm --filter=@plane/ui storybook
docker compose -f docker-compose-test.yml up --build --abort-on-container-exit --exit-code-from api-tests
```

**K8s community deploy**: chart docs live on Artifact Hub (`plane-ce`); see `deployments/kubernetes/community/README.md` — not required for local app development.

---

## Priority stack (if you remember nothing else)

1. Setup: `./setup.sh` → Docker local compose → `pnpm dev` (≥12GB RAM, Node 22+, pnpm 11)
2. Ship clean: oxfmt + OxLint (`--deny-warnings`) + types; tests for features/fixes
3. UI: Canvas once at root; surfaces siblings; layers match surfaces; matched hovers
4. Git: branch `type/id-desc` → Husky must pass → PR to `preview` titled `[ID] type: …`
5. i18n: all locales in sync; never translate brand/DNT terms
6. Security: private disclosure only
