# SPDX-License-Identifier: GPL-3.0-or-later
"""Conservative shelf packing, independent of Blender and third-party packers."""
import math
import pathlib
import subprocess
import sys


def validate(boxes, margin):
    if not boxes or not math.isfinite(margin) or not 0 <= margin < .5:
        raise ValueError('Invalid boxes or margin')
    if any(not math.isfinite(v) or v <= 0 for b in boxes for v in b):
        raise ValueError('Degenerate or non-finite UV island')


def pack_python(boxes, margin=.002, rotate=True):
    validate(boxes, margin)
    best = None
    for key in (lambda i: boxes[i][0]*boxes[i][1], lambda i: max(boxes[i])):
        order = sorted(range(len(boxes)), key=key, reverse=True)
        def attempt(scale):
            x = y = row = 0.
            result = [None]*len(boxes)
            for i in order:
                w, h = (v*scale+2*margin for v in boxes[i])
                r = bool(rotate and h < w)
                if r:
                    w, h = h, w
                if x+w > 1:
                    x, y, row = 0., y+row, 0.
                if w > 1 or y+h > 1:
                    return None
                result[i] = (x+margin, y+margin, r)
                x += w
                row = max(row, h)
            return result
        if attempt(0) is None:
            raise ValueError('Margins cannot fit all islands')
        lo, hi = 0., 1.
        while attempt(hi) is not None and hi < 1e12:
            hi *= 2
        for _ in range(64):
            mid = (lo+hi)/2
            if attempt(mid) is None:
                hi = mid
            else:
                lo = mid
        scale = lo*(1-1e-12)
        candidate = (scale, attempt(scale), 'Python CPU')
        if best is None or scale > best[0]:
            best = candidate
    return best


def pack(boxes, margin=.002, rotate=True, backend='AUTO'):
    validate(boxes, margin)
    exe = pathlib.Path(__file__).resolve().parents[1]/'bin'/('openuv_engine.exe' if sys.platform == 'win32' else 'openuv_engine')
    if backend == 'NATIVE' or (backend == 'AUTO' and exe.exists()):
        if not exe.exists():
            raise ValueError('Native engine missing: build with scripts/build.ps1')
        data = f'{len(boxes)} {margin:.17g} {int(rotate)} 2\n'
        data += '\n'.join(f'{w:.17g} {h:.17g}' for w,h in boxes)
        proc = subprocess.run([str(exe)], input=data, text=True, capture_output=True, timeout=120,
                              creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
        if proc.returncode:
            raise ValueError(proc.stderr.strip())
        lines = proc.stdout.splitlines()
        scale = float(lines[0])
        places = [(float(x),float(y),bool(int(r))) for x,y,r in (line.split() for line in lines[1:])]
        check(boxes, margin, scale, places)
        return scale, places, 'C++ CPU (2 searches)'
    result = pack_python(boxes, margin, rotate)
    check(boxes, margin, result[0], result[1])
    return result


def check(boxes, margin, scale, places):
    if not math.isfinite(scale) or scale <= 0 or len(places) != len(boxes):
        raise ValueError('Invalid engine result')
    rects = []
    for (w,h),(x,y,r) in zip(boxes, places):
        if r:
            w,h = h,w
        rect = (x-margin,y-margin,x+w*scale+margin,y+h*scale+margin)
        if any(not math.isfinite(v) for v in rect) or min(rect[:2]) < -1e-9 or max(rect[2:]) > 1+1e-9:
            raise ValueError('Out of bounds')
        rects.append(rect)
    active = []
    for rect in sorted(rects):
        active = [other for other in active if other[2] > rect[0]+1e-9]
        for a,b,c,d in active:
            if min(c,rect[2])-max(a,rect[0]) > 1e-9 and min(d,rect[3])-max(b,rect[1]) > 1e-9:
                raise ValueError('Collision')
        active.append(rect)
