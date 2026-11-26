"""Split a neon scene (glowing line art on a dark backdrop) into movable element layers (RGBA cut-outs).
Backdrop = pixels close to the edge colour AND connected to the image border. The soft glow around each
element is kept as partial alpha, so cut-outs keep their halo when they move."""
import numpy as np
from PIL import Image
from scipy import ndimage

def split(im, tol=38, join=10, min_area=300):
    a = np.asarray(im.convert("RGB")).astype(np.int16)
    edge = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]]); bg = np.median(edge, axis=0)
    dist = np.abs(a - bg).sum(2)
    close = dist <= tol
    lab, _ = ndimage.label(close)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])).tolist()) - {0}
    ink = ~np.isin(lab, list(border))
    ink = ndimage.binary_opening(ink, iterations=1)
    ink = ndimage.binary_fill_holes(ndimage.binary_closing(np.pad(ink, 6), iterations=4)[6:-6, 6:-6] | ink)
    joined = ndimage.binary_dilation(ink, iterations=join)
    glab, _ = ndimage.label(joined)
    # alpha: solid inside the element, a soft ramp over the glow just outside it
    glow = np.clip((dist - 8) / 60.0, 0, 1)
    soft = np.maximum(ndimage.gaussian_filter(ink.astype(np.float32), 1.0), glow * ndimage.binary_dilation(ink, iterations=8))
    els = []
    for i, sl in enumerate(ndimage.find_objects(glab), 1):
        comp = glab[sl] == i
        area = int((ink[sl] & comp).sum())
        if area < min_area: continue
        alpha = soft[sl] * comp
        rgba = np.dstack([a[sl], alpha * 255]).clip(0, 255).astype(np.uint8)
        y0, x0 = sl[0].start, sl[1].start
        els.append(dict(img=Image.fromarray(rgba, "RGBA"), x=x0, y=y0, w=sl[1].stop - x0, h=sl[0].stop - y0, area=area))
    els.sort(key=lambda e: -e["area"])
    return els, tuple(int(v) for v in bg)
