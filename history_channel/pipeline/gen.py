"""Generate scenes for the history channel on RunPod Flux dev (~$0.012 each).
Usage: python3 pipeline/gen.py scenes_file.txt OUTDIR [ids...]
scenes file: one 'id | description' per line. The key is injected by the network proxy."""
import json, sys, os, urllib.request, concurrent.futures as cf
EP="https://api.runpod.ai/v2/black-forest-labs-flux-1-dev/runsync"
STYLE=("minimalist flat 2D cartoon, very simple style like a webcomic, thick uniform black outlines, flat muted colors, "
       "no shading, no gradients, all people have perfectly round bald white heads with two black dot eyes and tiny mouths and simple stick-like limbs, "
       "plain white background, few simple props, lots of empty space, no text, no letters, no words, ")
HERO="the main character is a small boy wearing a tattered brown shirt and dark shorts, "
def load(path):
    out={}
    for l in open(path):
        if '|' in l and not l.startswith('#'):
            k,v=l.split('|',1); out[k.strip()]=v.strip()
    return out
def run(args):
    k,desc,outdir=args
    p=STYLE+(HERO if 'boy' in desc else '')+desc
    body=json.dumps({"input":{"prompt":p,"num_inference_steps":28,"guidance":3.5,"seed":int(os.environ.get("SEED",23))}}).encode()
    for attempt in range(3):
        try:
            d=json.load(urllib.request.urlopen(urllib.request.Request(EP,body,{"Content-Type":"application/json"}),timeout=280))
            urllib.request.urlretrieve(d["output"]["result"],os.path.join(outdir,k+".jpg")); return k
        except Exception as e: err=e
    return k+" FAILED "+str(err)
if __name__=="__main__":
    sc=load(sys.argv[1]); outdir=sys.argv[2]; ids=sys.argv[3:] or list(sc)
    with cf.ThreadPoolExecutor(6) as ex:
        for r in ex.map(run,[(k,sc[k],outdir) for k in ids]): print(r, flush=True)
