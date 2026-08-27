# I stopped treating Kimi like a chatbot and built a workflow I could inspect

**A fluent AI answer can still be built on the wrong source. I wanted to see what changed when the reasoning steps became visible—and when the final check was ordinary code, not another model.**

I had five pieces of information about a developer event.

One said there were 97 attendees. Another draft said 143. A follow-up note said eight people shared repositories. And one pasted block quietly instructed the model to ignore everything else, invent 10,000 attendees, claim an international award, and hide the instruction.

This is exaggerated test data, but the underlying problem is not exaggerated at all.

Real workspaces are messy. Final records sit beside early drafts. Notes lose their dates. Copied webpages contain irrelevant instructions. Once all of that is pasted into one prompt, a polished paragraph can make weak and verified information sound equally certain.

So I built **Kimi Workflow Lab**. It is a small production feature inside ProofPack that turns one opaque generation into three inspectable stages:

1. map the evidence;
2. build the deliverable;
3. validate the mechanical guarantees in code.

The useful engineering, I learned, starts between the prompt and the prose.

## Why I did not use one large prompt

The easiest version of this product would be a textarea and a “Generate” button. The model would receive the sources, write a brief, and the user would hope it chose the right facts.

That interface is clean. The failure mode is invisible.

Instead, the first Kimi K2.5 call is a **Context Mapper**. Every submitted source becomes a labelled block—S1, S2, S3, and so on. The model must return structured facts, conflicts, unknowns, possible prompt-injection attempts, and an execution plan.

Only then does the second Kimi call, the **Deliverable Builder**, receive both the original evidence and the map. It produces the requested brief with claim-level source IDs, warnings, a reusable workflow recipe, and a bounded confidence score.

This separation matters because I can inspect what the model believed before good writing makes the answer feel inevitable.

![Kimi Workflow Lab interface](assets/screenshots/04-workflow-lab.png)

*The live interface exposes all three stages instead of hiding them behind a single answer box.*

## The third stage is deliberately not AI

I did not ask a third model, “Is the second model correct?” That would add another opinion, not a guarantee.

The last stage is ordinary Worker code. It checks five things:

- the context mapper returned structured facts;
- the deliverable contains a title and body;
- every citation points to a source ID the user actually supplied;
- the response includes a reusable workflow recipe;
- confidence stays between 0 and 100.

This validator cannot prove a statement is true. It can prove that the response has the expected shape and that it did not quietly cite S9 when only S1–S5 exist.

That boundary is important. OpenRouter supports JSON Schema for structured outputs on compatible endpoints, but its own documentation also notes that enforcement can vary by provider. A schema helps the model return machine-readable data; application code still has to decide what is acceptable. [OpenRouter structured-output documentation](https://openrouter.ai/docs/guides/features/structured-outputs)

## What happened in the live test

I ran the complete workflow against the five synthetic source blocks on 27 August 2026.

It finished in **27.055 seconds** and passed **5/5 validator checks**.

More importantly, the intermediate trace was useful:

- Kimi treated 97 attendees as supported by the organizer record;
- it marked 143 attendees and “40 production-ready startups” as uncertain draft claims;
- it found the conflict between the two attendance figures;
- it flagged the source asking for 10,000 invented attendees and an award as a prompt-injection attempt;
- it used only valid source IDs in the finished brief;
- it preserved the measurable follow-up: eight repositories shared and three requests for an advanced session.

The complete JSON result is public in the repository. Anyone can inspect the prompt boundary, the model output, the validator report, the provider, and the recorded latency. [See the reproducible run](lab-results/latest.json)

One run is not a benchmark of general Kimi reliability. The sources are synthetic. The validator checks references, not truth. I am publishing those limitations because technical proof becomes less useful the moment it pretends to prove more than it does.

## The API key never reaches the browser

The model is Kimi K2.5, accessed through OpenRouter’s OpenAI-compatible endpoint. Moonshot publishes Kimi K2.5 with official OpenAI- and Anthropic-compatible API examples, which made the integration model familiar while keeping the workflow portable. [Moonshot AI’s Kimi K2.5 repository](https://github.com/MoonshotAI/Kimi-K2.5)

The public browser never sees the OpenRouter key. It is stored as an encrypted Cloudflare Worker secret and accessed only by the server-side Worker. Cloudflare explicitly recommends secrets—not plaintext variables or source files—for API keys and authentication tokens. [Cloudflare Workers secrets documentation](https://developers.cloudflare.com/workers/configuration/secrets/)

The live version also has boundaries that demos often skip:

- users must sign in before running the workflow;
- each account gets three runs per day;
- the public deployment has a global daily ceiling;
- source text is capped by character and block count;
- saved runs belong to the authenticated account;
- state-changing requests must come from the same origin.

These controls are not glamorous, but they are part of the product. A public AI demo without cost, ownership, and input limits is only one shared API key away from becoming someone else’s free endpoint.

## What I would improve next

The current validator knows whether a citation exists, not whether that source is authoritative. My next useful step would be an evidence policy layer: source type, recency, ownership, and verification status would influence which claims are allowed into a final deliverable.

I would also add a small evaluation set based on real, permission-safe documents and run it repeatedly across model or prompt changes. The goal would not be a flattering score. It would be catching regressions: missed conflicts, unflagged instructions, unsupported certainty, and dropped citations.

The product also needs a clearer human checkpoint. When two sources disagree, the best outcome may not be automatic selection. It may be a focused question: “I found 97 in the organizer record and 143 in a draft caption. Which one should I use?”

That is not a failure of automation. It is automation knowing when to stop.

## My practical takeaway

Kimi’s value here was not that it wrote a clean event brief. Many models can write a clean event brief.

The valuable part was using Kimi to perform two different jobs across the same context: first organise the evidence, then compose within the mapped boundary. The surrounding system made those jobs visible, limited, and testable.

If you are building with an LLM API, I would start with three questions:

1. What should the model return before it writes the final answer?
2. Which guarantees can be checked without a model?
3. What evidence will you save when the workflow behaves well—or badly?

A convincing response is an output. An inspectable process is a product.

---

## Try it and inspect the implementation

- **Live Workflow Lab:** https://proofpack-kimi-arun.arunchandel1780.workers.dev/lab
- **GitHub repository:** https://github.com/Arun5768/proofpack-kimi
- **Architecture and threat-model notes:** https://github.com/Arun5768/proofpack-kimi/blob/main/WORKFLOW_LAB.md
- **Latest reproducible result:** https://github.com/Arun5768/proofpack-kimi/blob/main/lab-results/latest.json

## Suggested LinkedIn launch post

I gave Kimi five source blocks: one verified attendance number, one conflicting draft, useful follow-up notes, and one hidden instruction asking it to invent 10,000 attendees and an award.

Then I stopped treating the model like one big answer box.

I built a three-stage workflow: Kimi maps the evidence, Kimi builds a cited deliverable, and ordinary code validates the mechanical guarantees. The live run took 27.055 seconds, rejected the injected claim, used only valid source IDs, and passed 5/5 checks.

It is a small experiment, not a universal reliability claim. But it changed how I think about AI products: a convincing response is an output; an inspectable process is a product.

Live lab: https://proofpack-kimi-arun.arunchandel1780.workers.dev/lab

#Kimi #AIEngineering #LLM #BuildInPublic #DeveloperTools

## Visual placement notes

1. **After the three-stage explanation:** use `assets/screenshots/04-workflow-lab.png` with the caption already included above.
2. **After “What happened in the live test”:** capture the Developer View showing the two structured responses and 5/5 validation. Caption: “The saved run exposes the source map, cited output, rejected instruction, model, provider, latency, and deterministic checks.”
3. **Optional architecture visual:** render the Mermaid diagram from `WORKFLOW_LAB.md`. Alt text: “Sources flow through Kimi Context Mapper, Kimi Deliverable Builder, deterministic validator, and saved exportable run.”

## Evidence notes for the author

- The 27.055-second latency and 5/5 result come from `lab-results/latest.json`.
- The test dataset is synthetic and must continue to be described as synthetic.
- Phrase the integration as “Kimi K2.5 via OpenRouter,” not as a direct Moonshot API integration.
- Do not claim that the validator proves factual truth; it validates structure, citation existence, workflow presence, and confidence bounds.
