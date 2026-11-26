"""Generate pictures for Your Vitals on RunPod Flux dev (~$0.012 each). The key is injected by the network proxy.
Usage: python3 pipeline/gen.py scenes_file.txt OUTDIR [ids...]   (scenes file: 'id | description' per line)"""
import json, sys, os, urllib.request, concurrent.futures as cf
EP = "https://api.runpod.ai/v2/black-forest-labs-flux-1-dev/runsync"
STYLE = ("glowing neon line art illustration on a pure solid black background, like a medical hologram or x-ray scan, "
         "thin luminous cyan outlines, simple clean shapes, minimal detail, flat, no shading, no gradients on the background, "
         "danger spots glow hot orange and red, everything else cyan and white, lots of empty black space, "
         "no text, no letters, no numbers, no words, ")
HERO = ("the person is a simple translucent glowing cyan cartoon human figure with a faint visible skeleton and a small glowing orange heart, "
        "bald round head with two big round white cartoon eyes, ")
SPRITE = "a single isolated object or creature alone in the middle of an empty pure black background, shown whole with empty margin around it, no human body unless described, no floor, no scenery, "
def load(path):
    out = {}
    for l in open(path, encoding="utf-8"):
        if '|' in l and not l.startswith('#'):
            k, v = l.split('|', 1); out[k.strip()] = v.strip()
    return out
def run(args):
    k, desc, outdir = args
    p = STYLE + (HERO if '{you}' in desc else '') + desc.replace('{you}', 'the person')
    body = json.dumps({"input": {"prompt": p, "num_inference_steps": 28, "guidance": 3.5, "seed": int(os.environ.get("SEED", 41))}}).encode()
    err = None
    for attempt in range(3):
        try:
            d = json.load(urllib.request.urlopen(urllib.request.Request(EP, body, {"Content-Type": "application/json"}), timeout=280))
            urllib.request.urlretrieve(d["output"]["result"], os.path.join(outdir, k + ".jpg")); return k
        except Exception as e: err = e
    return k + " FAILED " + str(err)
if __name__ == "__main__":
    sc = load(sys.argv[1]); outdir = sys.argv[2]; ids = sys.argv[3:] or list(sc); os.makedirs(outdir, exist_ok=True)
    with cf.ThreadPoolExecutor(6) as ex:
        for r in ex.map(run, [(k, sc[k], outdir) for k in ids]): print(r, flush=True)
