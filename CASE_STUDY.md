# Building ProofPack: why I did not make another AI writing box

I kept running into the same problem while filling applications: the writing was not the difficult part. Finding the right project link, remembering an event result, checking a number, and deciding whether a claim was actually defensible took most of the time.

Generic chat tools can polish an answer, but they usually see only the paragraph pasted into the prompt. That makes it easy to produce confident language that is disconnected from the applicant's real work.

## The product decision

ProofPack starts with evidence, not a blank chat box. A user creates a workspace for one application and adds projects, open-source work, articles, events, experience, metrics, and public links. Only then do they paste the application question.

Kimi K2.5 receives that structured evidence pack and returns five things:

1. The answer.
2. The exact facts it used.
3. Claims the user should check.
4. Proof that would make the answer stronger.
5. A confidence score.

The character limit is enforced again by the server. Even if the model writes too much, the saved answer cannot exceed the user's selected limit.

## Why Kimi fits this problem

An application answer can depend on several projects, event pages, articles, metrics, and notes at once. This is closer to evidence synthesis than ordinary copywriting. Kimi's long-context reasoning lets ProofPack consider the combined record while the product layer keeps the response constrained and auditable.

The integration runs through OpenRouter from a Cloudflare Worker. The API key never reaches the browser or GitHub. Cloudflare D1 stores user workspaces and generation history, while passwords, sessions, and recovery codes are stored only as hashes.

## What changed after testing

The first version was technically complete but asked a reviewer to create an account before understanding the product. I added a read-only sample workspace that displays a real Kimi-generated answer, its two supporting facts, an honesty warning, and the next proof to collect. Reviewers can now understand the complete workflow in seconds and create an account only when they want to use their own evidence.

I also added per-user and whole-app generation limits. A production demo should not leave a public model key open to unlimited spending.

## Current result

ProofPack now has a complete deployed journey: account creation, recovery, private workspaces, public-link enrichment, evidence management, Kimi generation, character-limit enforcement, answer history, and complete account deletion.

The most important outcome is not that Kimi writes a better paragraph. It is that the user can see why that paragraph can—or cannot—be trusted.

- Live product: https://proofpack-kimi-arun.arunchandel1780.workers.dev
- Source code: https://github.com/Arun5768/proofpack-kimi
