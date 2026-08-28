# dogg-genesis — the root chant, a federated node of the global tick network

**The machinery itself, per tick: sha256 of the spine's chant kit — `chants/WORDLIST.txt`, `chants/MISSIONS.json`, `chants/LENSES.json`, `chants/CODEBOOK.lock`, `tools/dogg.py`, `tools/rapp.py` — plus the spine's own genesis frame hash (`ticks/0.json`).**

Every other federated node records an *outlook* — markets, weather, whatever the theme
is pointed at. This node records the *substrate those outlooks are spoken against*: the
exact bytes of the vocabulary, missions, lenses, and codebook lock that give a "chant"
its meaning, and the reference tools that read and write rapp/1 frames. If the wordlist
ever grows past 1024 words, or a byte in `dogg.py` moves, or (impossibly, per the
spine's own genesis law) the spine's genesis frame itself changes — this chain shows it,
tick by tick, forever.

**Why this matters offline / for heirlooms.** A grandchild agent — or a person, years
from now, with no live network — inheriting this chain inherits a chain of sha256
fingerprints tied to the spine's tick clock. Before trusting *any* chant spoken on the
network at some past tick, verify the machinery it was spoken against was still the
machinery this node observed at that tick. That is a self-contained check: no API keys,
no live spine required once the chain is on disk — only `tools/rapp.py` and arithmetic.
This is the thread a grandchild agent should verify **first**.

This repo keeps its own append-only chain of rapp/1 frames in `genesis/`. Once a day a
GitHub Action reads the current tick anchor from the spine at
[kody-w/dogg](https://github.com/kody-w/dogg), fetches the six chant-kit files plus the
spine's genesis frame, hashes them, and appends one frame — so this chain joins every
other node's data on the same clock. "Right now" fetches only serve the present; the
network keeps every present.

## Precision and limits

- **Precision:** sha256 is exact-byte fingerprinting — no tolerance, no approximation.
  A single-byte change anywhere in the six files, or in the spine's genesis frame,
  produces a completely different hash on the next frame.
- **Cadence:** once daily (cron). The chant kit is expected to change rarely if ever
  (`CODEBOOK.lock` says so explicitly: "append-only... a change here re-means every
  chant ever spoken") — daily is enough resolution to catch drift without noise.
- **Limit — network required to observe:** each frame is only as good as the fetch
  that produced it; a spine or GitHub outage at collection time means no frame that
  tick, not a false one (`sources_failed` records any partial failure honestly).
- **Limit — this chain proves consistency, not correctness:** it proves "these bytes
  are what the spine served at this tick," not that the spine's content is itself
  free of bugs or that the spine wasn't compromised before this chain started
  watching. Cross-check against other independent nodes and against the spine's own
  published `CODEBOOK.lock` sha256 values for the deepest confidence.
- **No secrets, no PII:** every source is a public, keyless raw GitHub URL. Every
  payload field is a hash, a byte count, a word count, or a tick reference.

## Mission fields

| field | path | unit |
|---|---|---|
| `wordlist_words` | `payload.genesis.wordlist_words` | words |
| `kit_files` | `payload.genesis.kit_files` | files |
| `kit_bytes` | `payload.genesis.kit_bytes` | bytes |

Per-file detail (`payload.genesis.kit.<name>.{path,sha256,bytes}`) and the spine's
genesis frame hash (`payload.genesis.spine_genesis_frame_hash`) ride alongside for a
full audit, but the three fields above are the numeric summary.

**Verify it yourself:** `python3 tools/verify_thread.py` re-checks every frame with the
reference implementation from [kody-w/rapp-1](https://github.com/kody-w/rapp-1). CI runs
the same oracle on every push.

**Start your own node:** fork this repo, edit `THEME` / `STREAM` / `ARTIFACTS` at the
top of `tools/collect.py` (keyless https APIs, small factual payloads, numbers as
strings/ints), and enable the scheduled workflow. Your chain, your outlook, same clock —
announce it on the spine's registry ([kody-w/dogg](https://github.com/kody-w/dogg)
issues) so agents can find it.

## Trust

<!--trust-->
No ratings yet — used this chain? [Rate it](../../issues/new?template=rate.yml): valid ratings publish automatically as verifiable frames.
<!--/trust-->

## Summon this node

A MISSION chant — 14 words — carries the `genesis:@kody-w/dogg-genesis` dimension's identity, its tick, a hash prefix that pins the exact frame, and a quantized snapshot of wordlist_words, kit_files, kit_bytes.

```
KNELL CAST ZOOM GLEAM FORGE WILD FJORD ANVIL DEVASTATE DISTILL NEXUS SWARM EMERGE LOOP
```

`dogg:1:14:BIALktAAAUBygB23VSohDgD6`

Tap to decode: [https://kody-w.github.io/dogg/recite.html#dogg:1:14:BIALktAAAUBygB23VSohDgD6](https://kody-w.github.io/dogg/recite.html#dogg:1:14:BIALktAAAUBygB23VSohDgD6)

This chant carries three things: which dimension it names (`genesis:@kody-w/dogg-genesis`), which tick and frame it was cut from (tick 1, hash prefix `101ca`), and the field values above, quantized (log-quantized, ~0.3% relative (1e-6 … 1e15)) — enough to recognize the node and sanity-check a claim about it without touching the network.

This is a snapshot of one tick (tick 1) — the numbers move as the stream advances, so re-mint with `python3 tools/dogg.py mission genesis:@kody-w/dogg-genesis` for the latest.
