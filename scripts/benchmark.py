# SPDX-License-Identifier: GPL-3.0-or-later
"""Reproducible synthetic benchmark; never compares competing products."""
import importlib.util
import json
import pathlib
import random
import time
spec = importlib.util.spec_from_file_location('packing', pathlib.Path(__file__).resolve().parents[1]/'addon/bridge/packing.py')
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)
rng = random.Random(42)
results = []
for n in (10,100,1000,10000):
    boxes = [(rng.uniform(.01,1),rng.uniform(.01,1)) for _ in range(n)]
    for backend in ('PYTHON','NATIVE'):
        start = time.perf_counter()
        try:
            scale, places, actual = p.pack(boxes,.0005,True,backend)
            elapsed = time.perf_counter()-start
            p.check(boxes,.0005,scale,places)
            results.append(dict(n=n,backend=actual,seconds=elapsed,bbox_area=sum(w*h for w,h in boxes)*scale**2))
        except (OSError,ValueError) as exc:
            results.append(dict(n=n,backend=backend,error=str(exc)))
print(json.dumps(results,indent=2))
