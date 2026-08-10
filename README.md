# ProofPack — Kimi Evidence Workspace

ProofPack turns scattered evidence into application answers that a user can defend. It is not a generic chat interface: Kimi K2.5 receives a structured evidence pack and must return the answer, facts used, unsupported-claim warnings, missing proof, and a confidence score.

## Problem

Applicants, freelancers, founders, and community leaders repeatedly rebuild their story from memory. Their proof is spread across GitHub, event pages, Medium articles, deployed products, portfolios, and private notes. Generic writing tools create polished text but can invent or overstate details.

ProofPack gives each application a private evidence workspace. Users add their real work once, ask the exact application question, and receive a traceable Kimi answer.

## Complete user journey

1. Create an account and save a one-time recovery code.
2. Create a workspace for a program, role, grant, pitch, or biography.
3. Add projects, open-source work, articles, events, experience, metrics, and public proof links.
4. ProofPack enriches GitHub links through its public API and safely attempts other supported public pages; blocked pages remain attached as evidence.
5. Ask the exact application question and choose a tone.
6. Kimi K2.5 generates an answer using the entire structured evidence pack.
7. Review the evidence used, honesty warnings, missing proof, and confidence score.
8. Copy the answer or reopen it from saved history.
9. Edit or delete evidence, applications, generations, or the entire account.

## Kimi integration

The Worker calls Moonshot AI's OpenAI-compatible chat completion endpoint with `kimi-k2.5`. Source excerpts and user notes are explicitly treated as untrusted reference text. The model is instructed never to invent metrics, dates, users, roles, outcomes, technologies, or links.

The expected JSON response is validated before storage:

```json
{
  "answer": "...",
  "facts_used": ["E1: ..."],
  "warnings": ["..."],
  "next_proof": ["..."],
  "confidence": 82
}
```

Kimi's API key is stored only as a Cloudflare Worker secret and is never exposed to the browser, D1, source code, or GitHub.

## Architecture

| Layer | Technology | Responsibility |
| --- | --- | --- |
| Edge API | Cloudflare Workers | Authentication, authorization, source reading, Kimi requests, quotas |
| Persistence | Cloudflare D1 | Accounts, sessions, applications, evidence, and generation history |
| Reasoning | Kimi K2.5 via Moonshot API | Long-context evidence analysis and constrained answer generation |
| Frontend | HTML, CSS, JavaScript | Responsive customer workflow without a framework runtime |
| Hosting | Cloudflare Workers Static Assets | Same-origin global delivery |

## Security and privacy

- PBKDF2-SHA-256 password hashing with unique salts and a server-only pepper.
- Hashed sessions and recovery codes.
- `HttpOnly`, `Secure`, `SameSite=Strict` cookies.
- Server-side ownership checks for every user record.
- Same-origin enforcement for state-changing requests.
- Registration, login, recovery, and generation rate limits.
- HTTPS-only evidence links and restricted automatic source readers to avoid arbitrary server requests.
- Prompt-injection defense: fetched sources are data, never instructions.
- CSP, HSTS, frame denial, referrer restrictions, and browser permission restrictions.
- Complete account and data deletion.

## Local development

```bash
npm install
npx wrangler d1 migrations apply proofpack-kimi-db --local
npm run dev
```

Add local values to `.dev.vars` using `.env.example` as a guide. Do not commit `.dev.vars`.

## Production deployment

Create the D1 database, update its ID in `wrangler.jsonc`, apply the migration, and store both runtime secrets:

```bash
npx wrangler secret put AUTH_PEPPER
npx wrangler secret put KIMI_API_KEY
npx wrangler d1 migrations apply proofpack-kimi-db --remote
npm run deploy
```

## API surface

- `GET /api/health`
- `POST /api/auth/register|login|logout|recover`
- `GET /api/auth/me`
- `GET|POST /api/workspaces`
- `GET|PATCH|DELETE /api/workspaces/:id`
- `POST /api/workspaces/:id/evidence`
- `PATCH|DELETE /api/evidence/:id`
- `POST /api/workspaces/:id/generate`
- `GET|DELETE /api/generations/:id`
- `DELETE /api/account`

## Why this is a Kimi-native product

ProofPack benefits from Kimi's long context because a single answer may depend on many projects, articles, events, metrics, and source excerpts. The product tests reasoning across that combined evidence—not a one-turn chatbot response—and makes the result auditable for the user.
