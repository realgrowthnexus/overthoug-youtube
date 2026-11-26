"""Generate woodcut scenes for The Ward Book on RunPod Flux dev (~$0.012 each).
Usage: python3 pipeline/gen.py scenes_file.txt OUTDIR [ids...]
scenes file: one 'id | description' per line. The API key is injected by the network proxy."""
import json, sys, os, urllib.request, concurrent.futures as cf
EP = "https://api.runpod.ai/v2/black-forest-labs-flux-1-dev/runsync"
STYLE = ("old european woodcut print, 16th century broadsheet engraving style, bold black ink lines, crosshatching, "
         "black ink only with a few small accents of deep red ochre, isolated figure on a plain pure white background, "
         "lots of empty white space around it, no frame, no border, no text, no letters, no words, ")
HERO = ""
def load(path):
    out = {}
    for l in open(path):
        if '|' in l and not l.startswith('#'):
            k, v = l.split('|', 1); out[k.strip()] = v.strip()
    return out
def run(args):
    k, desc, outdir = args
    body = json.dumps({"input": {"prompt": STYLE + HERO + desc, "num_inference_steps": 28, "guidance": 3.5,
                                 "seed": int(os.environ.get("SEED", 31))}}).encode()
    err = None
    for attempt in range(3):
        try:
            d = json.load(urllib.request.urlopen(urllib.request.Request(EP, body, {"Content-Type": "application/json"}), timeout=280))
            urllib.request.urlretrieve(d["output"]["result"], os.path.join(outdir, k + ".jpg")); return k
        except Exception as e: err = e
    return k + " FAILED " + str(err)
if __name__ == "__main__":
    sc = load(sys.argv[1]); outdir = sys.argv[2]; ids = sys.argv[3:] or list(sc)
    os.makedirs(outdir, exist_ok=True)
    with cf.ThreadPoolExecutor(6) as ex:
        for r in ex.map(run, [(k, sc[k], outdir) for k in ids]): print(r, flush=True)
