"""Run: python -m unittest test_converter.py"""
import tempfile
import unittest
from pathlib import Path
import numpy as np
import trimesh
from scipy.spatial.transform import Rotation
from mesh_to_gs import convert


class ConverterTests(unittest.TestCase):
    def test_instances_normals_color_and_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            mesh = trimesh.creation.box()
            mesh.visual.vertex_colors = [230, 30, 20, 255]
            scene = trimesh.Scene()
            scene.add_geometry(mesh)
            transform = np.eye(4); transform[0, 3] = 4
            scene.add_geometry(mesh, transform=transform)
            scene.export(root/'input.glb')
            result = convert(root/'input.glb', root/'out.ply', 2000)
            self.assertEqual(result['parts'], 2)
            self.assertGreater(result['bounds'][1][0], 4)
            payload = (root/'out.ply').read_bytes().split(b'end_header\n',1)[1]
            a = np.frombuffer(payload, '<f4').reshape(-1,62)
            self.assertEqual(a.shape, (2000,62))
            self.assertTrue(np.isfinite(a).all())
            np.testing.assert_allclose(np.linalg.norm(a[:,58:62],axis=1),1,atol=1e-6)
            z = Rotation.from_quat(a[:,[59,60,61,58]]).apply([0,0,1])
            np.testing.assert_allclose(z,a[:,3:6],atol=1e-6)
            rgb = a[:,6:9] * .28209479177387814 + .5
            np.testing.assert_allclose(rgb[0],[230/255,30/255,20/255],atol=1e-5)
            self.assertTrue(np.all(a[:,57] < a[:,55]))
            with self.assertRaises(FileExistsError):
                convert(root/'input.glb',root/'out.ply',2000)

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            convert('unsupported.fbx','unused.ply')


if __name__ == '__main__':
    unittest.main()
