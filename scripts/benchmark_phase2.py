# SPDX-License-Identifier: GPL-3.0-or-later
"""Compare retained shelf baseline and new native portfolio on identical input.
No third-party packer, no Blender UV mutation. JSON to stdout.
"""
import argparse
import importlib.util
import json
import math
import pathlib
import random
import statistics
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('packing',ROOT/'addon/bridge/packing.py')
packing = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packing)


def compare(boxes, name, repeats=3, margin=.002):
    exe = ROOT/'addon/bin'/('openuv_engine.exe' if sys.platform == 'win32' else 'openuv_engine')
    text = f'{len(boxes)} {margin:.17g} 1 2 1\n'+'\n'.join(f'{w:.17g} {h:.17g}' for w,h in boxes)
    cases = {}
    for label,args in (('shelf',['--shelf']),('portfolio',[])):
        times=[]
        for _ in range(repeats):
            start=time.perf_counter()
            result=subprocess.run([str(exe)]+args,input=text,text=True,capture_output=True,timeout=120)
            if result.returncode:
                raise RuntimeError(result.stderr)
            lines=result.stdout.splitlines()
            scale=float(lines[0])
            places=[(float(x),float(y),bool(int(r))) for x,y,r in (line.split() for line in lines[1:])]
            packing.check(boxes,margin,scale,places)
            times.append(time.perf_counter()-start)
        cases[label]={'scale':scale,'bbox_area':sum(w*h for w,h in boxes)*scale**2,
                      'seconds':times,'median_seconds':statistics.median(times),
                      'engine_metadata':result.stderr.strip()}
    if cases['portfolio']['scale']+1e-9<cases['shelf']['scale']:
        raise AssertionError('Portfolio regressed against shelf')
    return {'name':name,'islands':len(boxes),'margin':margin,'rotate':True,'repeats':repeats,
            'linear_scale_gain_percent':100*(cases['portfolio']['scale']/cases['shelf']['scale']-1),
            'cases':cases}


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--input',help='JSON list of {name, boxes}, e.g. extracted Blender data')
    parser.add_argument('--repeats',type=int,default=3)
    args=parser.parse_args()
    if args.input:
        datasets=json.loads(pathlib.Path(args.input).read_text(encoding='utf-8-sig'))
    else:
        rng=random.Random(51)
        datasets=[{'name':f'synthetic-{n}','boxes':[(rng.uniform(.01,1),rng.uniform(.01,1)) for _ in range(n)]}
                  for n in (10,51,100,256,1000,10000)]
    print(json.dumps([compare(d['boxes'],d['name'],args.repeats,d.get('margin',.002)) for d in datasets],indent=2))
