# SPDX-License-Identifier: GPL-3.0-or-later
import importlib.util
import pathlib
import random
import unittest
import subprocess
import sys

path = pathlib.Path(__file__).resolve().parents[1]/'addon'/'bridge'/'packing.py'
spec = importlib.util.spec_from_file_location('packing', path)
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)


class PackingTests(unittest.TestCase):
    def test_random_geometry(self):
        rng = random.Random(981)
        for n in (1,2,5,10,100,1000,10000):
            for rotate in (False,True):
                boxes = [(rng.uniform(.001,10),rng.uniform(.001,10)) for _ in range(n)]
                for backend in ('PYTHON', 'AUTO'):
                    scale,places,_ = p.pack(boxes,.001,rotate,backend)
                    p.check(boxes,.001,scale,places)
                    if not rotate:
                        self.assertFalse(any(r for x,y,r in places))

    def test_rejections(self):
        for boxes, margin in (([],0), ([(0,1)],0), ([(float('nan'),1)],0), ([(1,1)],-.1), ([(1,1)],.5)):
            with self.assertRaises(ValueError):
                p.pack(boxes,margin)
        with self.assertRaises(ValueError):
            p.pack_python([(1,1)]*10,.25)

    def test_deterministic(self):
        self.assertEqual(p.pack_python([(1,2)]*20),p.pack_python([(1,2)]*20))

    def test_collision_validator(self):
        with self.assertRaises(ValueError):
            p.check([(1,1)]*2,0,.5,[(0,0,False)]*2)

    def test_native_protocol_rejects_bad_input(self):
        exe = path.parents[1]/'bin'/('openuv_engine.exe' if sys.platform == 'win32' else 'openuv_engine')
        if not exe.exists():
            self.skipTest('Native engine not installed')
        for data in ('0 .001 1 2\n', '1 .5 1 2\n1 1', '1 .001 1 2\n0 1', '1 .001 1 2\nnan 1'):
            result = subprocess.run([str(exe)], input=data, capture_output=True, text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertEqual(result.stdout,'')


if __name__ == '__main__':
    unittest.main()
