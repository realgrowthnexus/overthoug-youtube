"""Split a flat scene (white background) into movable element layers (RGBA cut-outs).
Transparent = backdrop connected to the image border (light shadows included); everything enclosed
by outlines (white heads too) stays opaque."""
import numpy as np
from PIL import Image
from scipy import ndimage

def split(im, tol=100, join=6, min_area=150):
    a = np.asarray(im.convert("RGB")).astype(np.int16)
    near_white = (255 - a).sum(2) <= tol
    lab, _ = ndimage.label(near_white)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])).tolist()) - {0}
    ink = ~np.isin(lab, list(border))
    ink = ndimage.binary_opening(ink, iterations=1)           # drop specks
    # close small gaps in thin outlines, then fill enclosed areas (white heads) so they stay opaque
    closed = ndimage.binary_closing(np.pad(ink, 6), iterations=5)[6:-6, 6:-6]
    ink = ndimage.binary_fill_holes(closed | ink)
    joined = ndimage.binary_dilation(ink, iterations=join)
    glab, _ = ndimage.label(joined)
    soft = ndimage.gaussian_filter(ink.astype(np.float32), 0.8)
    els = []
    for i, sl in enumerate(ndimage.find_objects(glab), 1):
        comp = glab[sl] == i
        area = int((ink[sl] & comp).sum())
        if area < min_area: continue
        alpha = soft[sl] * comp
        rgba = np.dstack([a[sl], alpha * 255]).clip(0, 255).astype(np.uint8)
        y0, x0 = sl[0].start, sl[1].start
        els.append(dict(img=Image.fromarray(rgba, "RGBA"), x=x0, y=y0,
                        w=sl[1].stop - x0, h=sl[0].stop - y0, area=area))
    els.sort(key=lambda e: -e["area"])
    return els
