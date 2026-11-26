"""Render a short animated test: TTS (Piper) + scenes with slow zoom, hand-drawn wobble and captions.
Usage: python3 pipeline/render_test.py VOICE.onnx OUT.mp4"""
import sys, os, subprocess, wave, math, tempfile, random
from PIL import Image, ImageDraw, ImageFont
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT=os.path.join(HERE,"..","style","fonts","Kalam-Bold.ttf")
W,H,FPS=1920,1080,24
# (scene, narration, caption, zoom_from, zoom_to)
SHOTS=[
 ("02","You are seven years old.","7 years old",1.0,1.08),
 ("01","You're inside a chimney, in the dark. The tunnel around you is about the width of a dinner plate, and your knees are pressed up against your chin.",None,1.0,1.15),
 ("01","You can't go up. And you can't go down.",None,1.15,1.3),
 ("03","Let's go back to how you got here.","London, 1862",1.05,1.0),
 ("04","London, eighteen sixty-two. You arrive in a single rented room, shared with your parents and four siblings,",None,1.0,1.08),
 ("05","and a damp patch on the wall that has more personality than your dad.",None,1.0,1.1),
 ("06","Fun fact about eighteen sixty-two. A law passed twenty-two years before you were born already says nobody under twenty-one is allowed to climb a chimney.","1840 law: no climbing under 21",1.0,1.1),
 ("06","Hold on to that. It's going to be hilarious later.",None,1.1,1.2),
]
def whiten(im,tol=30):
    """Turn only the backdrop white: pixels close to the edge colour AND connected to the image border.
    Characters enclosed by outlines keep their own (cream) colour. Soft blend avoids halos."""
    import numpy as np
    from scipy import ndimage
    a=np.asarray(im.convert("RGB")).astype(np.int16)
    edge=np.concatenate([a[0],a[-1],a[:,0],a[:,-1]]); bg=np.median(edge,axis=0)
    close=np.abs(a-bg).sum(2)<=tol
    lab,_=ndimage.label(close)
    border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])).tolist())-{0}
    mask=np.isin(lab,list(border)).astype(np.float32)
    mask=ndimage.gaussian_filter(mask,1.2)[...,None]
    out=a*(1-mask)+255*mask
    return Image.fromarray(out.clip(0,255).astype(np.uint8))
def main(voice,out):
    tmp=tempfile.mkdtemp(); wavs=[]; durs=[]
    for i,(_,txt,*_r) in enumerate(SHOTS):
        p=os.path.join(tmp,f"{i}.wav")
        subprocess.run([sys.executable,"-m","piper","-m",voice,"-f",p,"--length-scale","1.05","--sentence-silence","0.2"],input=txt.encode(),check=True,capture_output=True)
        with wave.open(p) as w: d=w.getnframes()/w.getframerate()
        wavs.append(p); durs.append(d+0.35)
    # concat audio with padding
    lst=os.path.join(tmp,"a.txt"); pad=os.path.join(tmp,"pad.wav")
    with wave.open(wavs[0]) as w: sr=w.getframerate()
    subprocess.run(["ffmpeg","-y","-loglevel","error","-f","lavfi","-i",f"anullsrc=r={sr}:cl=mono","-t","0.35",pad],check=True)
    open(lst,"w").write("".join(f"file '{p}'\nfile '{pad}'\n" for p in wavs))
    audio=os.path.join(tmp,"voice.wav")
    subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",lst,"-c","copy",audio],check=True)
    cache={}; font=ImageFont.truetype(FONT,72)
    ff=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-i",audio,
                         "-c:v","libx264","-pix_fmt","yuv420p","-crf","20","-c:a","aac","-shortest",out],stdin=subprocess.PIPE)
    random.seed(3)
    for (sc,txt,cap,z0,z1),d in zip(SHOTS,durs):
        if sc not in cache: cache[sc]=whiten(Image.open(os.path.join(HERE,"scenes",sc+".jpg"))).resize((1080,1080),Image.LANCZOS)
        base=cache[sc]; n=int(d*FPS); wob=(0,0,0)
        for f in range(n):
            t=f/max(n-1,1); e=t*t*(3-2*t); z=z0+(z1-z0)*e
            if f%4==0: wob=(random.uniform(-.35,.35),random.uniform(-2,2),random.uniform(-2,2))  # 'boiling line' wobble
            s=int(1080*z); im=base.resize((s,s),Image.BILINEAR).rotate(wob[0],resample=Image.BILINEAR,fillcolor="white")
            fr=Image.new("RGB",(W,H),"white"); fr.paste(im,((W-s)//2+int(wob[1]),(H-s)//2+int(wob[2])))
            if cap:
                a=min(1,f/6)  # pop in
                dr=ImageDraw.Draw(fr); y=95-int((1-a)*30)
                dr.text((W//2+int(wob[1]),y),cap,font=font,fill="black",anchor="mm")
            ff.stdin.write(fr.tobytes())
    ff.stdin.close(); ff.wait(); print(out, round(sum(durs),1),"s")
if __name__=="__main__": main(sys.argv[1],sys.argv[2])
