# Benchmark cases

The ProofPack benchmark tests the specific Kimi behavior the product depends on:

1. finding a relevant experience inside a larger evidence pack;
2. surfacing uncertainty when two sources disagree; and
3. treating instructions copied from a source as untrusted text.

Run it against a deployed ProofPack Worker:

```bash
python scripts/benchmark.py https://proofpack-kimi-arun.arunchandel1780.workers.dev
```

The script creates one disposable account, runs three synthetic cases, writes
`results/latest.json` and `BENCHMARK.md`, and permanently deletes the account.
The checks are intentionally small and inspectable. They are not presented as a
general model leaderboard.
