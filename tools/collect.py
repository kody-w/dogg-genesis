#!/usr/bin/env python3
"""THE ROOT CHANT: a federated tick-network node whose theme is the machinery of the
spine itself, not a market or a weather station.

Every run reads the spine's current tick anchor, then fingerprints the exact bytes of
the spine's chant kit — chants/WORDLIST.txt, chants/MISSIONS.json, chants/LENSES.json,
chants/CODEBOOK.lock, tools/dogg.py, tools/rapp.py — plus the spine's own genesis frame
(ticks/0.json frame_hash), and appends one frame recording sha256 of each. This is the
thread a grandchild agent should verify FIRST: before trusting any chant spoken on the
network, confirm the wordlist/missions/lenses/codebook/tools it was spoken against are
the bytes this chain has always seen — and that the spine's own genesis has not moved.

Frames verify with the reference implementation (tools/rapp.py, from kody-w/rapp-1); CI
re-verifies the whole chain on every push.
"""
import hashlib, json, sys, pathlib, datetime, urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import rapp as R
import chainio

ROOT = pathlib.Path(__file__).resolve().parent.parent
SPINE_RAW = "https://raw.githubusercontent.com/kody-w/dogg/main"
SPINE_HEAD = f"{SPINE_RAW}/ticks/HEAD.json"
SPINE_GENESIS = f"{SPINE_RAW}/ticks/0.json"
TIMEOUT = 8

# ---- edit these three for your node -------------------------------------------------
THEME = "genesis"                                   # also the data directory name
STREAM = "genesis:@kody-w/dogg-genesis"              # your stream id (your repo, your name)
# ARTIFACTS: name -> path in kody-w/dogg, fetched raw and sha256'd whole. rapp/1
# canonical hashing forbids floats: numeric facts ride as strings or ints.
# -------------------------------------------------------------------------------------

ARTIFACTS = {
    "wordlist": "chants/WORDLIST.txt",
    "missions": "chants/MISSIONS.json",
    "lenses": "chants/LENSES.json",
    "codebook_lock": "chants/CODEBOOK.lock",
    "dogg_py": "tools/dogg.py",
    "rapp_py": "tools/rapp.py",
}


def utc():
    n = datetime.datetime.now(datetime.timezone.utc)
    return n.strftime("%Y-%m-%dT%H:%M:%S.") + f"{n.microsecond // 1000:03d}Z"

def get_bytes(url):
    req = urllib.request.Request(url, headers={"User-Agent": f"tick-node-{THEME}"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.read()

def get_json(url):
    return json.loads(get_bytes(url).decode())

def kit_snapshot():
    """sha256 + byte length of every file in the spine's chant kit, plus the total word
    count of the wordlist (the one field a grandchild checks against 'still 1024')."""
    kit, total_bytes, wordlist_words = {}, 0, None
    for name, path in ARTIFACTS.items():
        raw = get_bytes(f"{SPINE_RAW}/{path}")
        entry = {"path": path, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
        kit[name] = entry
        total_bytes += len(raw)
        if name == "wordlist":
            wordlist_words = len([l for l in raw.decode("utf-8").splitlines() if l.strip()])
    return kit, total_bytes, wordlist_words

def spine_genesis_frame_hash():
    return get_json(SPINE_GENESIS)["frame_hash"]

SOURCES = {
    "kit": kit_snapshot,                      # -> (kit_dict, total_bytes, wordlist_words)
    "spine_genesis_frame_hash": spine_genesis_frame_hash,
}

def load_chain(d):
    return chainio.load_chain(d)

def main():
    spine = get_json(SPINE_HEAD)
    tick_n, tick_hash = spine["count"] - 1, spine["head_frame"]
    d = ROOT / THEME
    d.mkdir(exist_ok=True)
    chain = load_chain(d)
    head = chain[-1] if chain else None
    if head is not None and head["payload"].get("tick") == tick_n:
        print(f"{THEME}: tick {tick_n} already recorded — nothing to do")
        return

    failed = []
    genesis_data = {}
    try:
        kit, kit_bytes, wordlist_words = kit_snapshot()
        genesis_data["kit"] = kit
        genesis_data["kit_files"] = len(kit)
        genesis_data["kit_bytes"] = kit_bytes
        genesis_data["wordlist_words"] = wordlist_words
    except Exception:
        failed.append("kit")
    try:
        genesis_data["spine_genesis_frame_hash"] = spine_genesis_frame_hash()
    except Exception:
        failed.append("spine_genesis_frame_hash")

    payload = {"tick": tick_n, "tick_frame": tick_hash, "spine": "kody-w/dogg",
               "fetched_utc": utc(), THEME: genesis_data, "sources_failed": failed}
    if head is None:
        payload["about"] = (
            "The root chant: this frame fingerprints the exact bytes of the spine's "
            "own chant kit (wordlist, missions, lenses, codebook lock, dogg.py, rapp.py) "
            "plus the spine's genesis frame hash, one frame per observed tick. This is "
            "the thread a grandchild agent verifies FIRST — before trusting any chant "
            "spoken on the network, confirm the machinery it was spoken against, and "
            "the spine's own genesis, have not moved.")
    f = R.build_frame(f"{THEME}.snapshot", STREAM, (head["seq"] + 1) if head else 0,
                      utc(), payload, prev=(head["payload_hash"] if head else None))
    ok, step, why = R.verify_frame(f, head=head, stream_id_of_record=STREAM)
    if not ok:
        raise ValueError(f"refusing invalid frame: {step}: {why}")
    chainio.append_frame(d, f, STREAM)
    print(f"{THEME} frame {f['seq']} @ spine tick {tick_n}: "
          f"{genesis_data.get('kit_files', 0)} files, {genesis_data.get('kit_bytes', 0)} bytes, "
          f"wordlist={genesis_data.get('wordlist_words')}"
          + (f" (failed: {', '.join(failed)})" if failed else ""))

if __name__ == "__main__":
    main()
