"""Mesh to anisotropic surface Gaussians / 网格转表面高斯（非训练重建）."""
import argparse
import json
from pathlib import Path
import numpy as np
import trimesh
from scipy.spatial.transform import Rotation


def convert(source, output, count=150000, seed=7, coverage=0.8, thickness=0.12):
    source, output = Path(source), Path(output)
    if output.exists():
        raise FileExistsError(f'Output exists / 输出已存在: {output}')
    if source.suffix.lower() not in {'.glb', '.gltf', '.obj', '.ply', '.stl'}:
        raise ValueError('Use GLB, GLTF, OBJ, mesh PLY or STL. Export FBX/Blend to GLB first.')
    if count < 100 or count > 5000000 or coverage <= 0 or thickness <= 0:
        raise ValueError('count: 100..5000000; coverage and thickness must be positive')
    scene = trimesh.load_scene(source, process=False)
    parts = []
    for node in scene.graph.nodes_geometry:
        transform, geom_name = scene.graph[node]
        mesh = scene.geometry[geom_name].copy()
        if not isinstance(mesh, trimesh.Trimesh) or not len(mesh.faces):
            continue
        mesh.apply_transform(transform)
        if not np.isfinite(mesh.vertices).all():
            raise ValueError('Nonfinite input geometry')
        if mesh.area > 0:
            parts.append(mesh)
    if not parts:
        raise ValueError('No triangle mesh found / 未找到三角网格；GS PLY 不是网格输入')
    areas = np.array([m.area for m in parts])
    rng = np.random.default_rng(seed)
    counts = rng.multinomial(count, areas / areas.sum())
    chunks = []
    warnings = []
    for mesh, n in zip(parts, counts):
        if not n:
            continue
        face = rng.choice(len(mesh.faces), n, p=mesh.area_faces / mesh.area)
        triangles = mesh.triangles[face]
        uv = rng.random((n, 2))
        a = np.sqrt(uv[:, 0])
        weights = np.column_stack((1-a, a*(1-uv[:, 1]), a*uv[:, 1]))
        pos = np.einsum('ni,nij->nj', weights, triangles)
        normal = mesh.face_normals[face]
        rgba = np.ones((n, 4))
        rgba[:, :3] = .65
        visual = mesh.visual
        if visual.kind == 'texture' and visual.uv is not None:
            tex_uv = np.einsum('ni,nij->nj', weights, visual.uv[mesh.faces[face]])
            materials = getattr(visual.material, 'materials', None)
            face_mats = getattr(visual, 'face_materials', None)
            if materials is not None and face_mats is not None:
                ids = np.asarray(face_mats)[face]
                for idx in np.unique(ids):
                    mask = ids == idx
                    rgba[mask] = materials[int(idx)].to_color(tex_uv[mask]) / 255.
            else:
                sampled = visual.material.to_color(tex_uv)
                if sampled is None:
                    warnings.append('Texture material has no base color; neutral gray used')
                else:
                    rgba = np.broadcast_to(np.asarray(sampled, dtype=float), (n, 4)).copy() / 255.
            # PBR baseColorFactor multiplies a baseColorTexture.
            mat = visual.material
            if getattr(mat, 'baseColorTexture', None) is not None and getattr(mat, 'baseColorFactor', None) is not None:
                rgba *= np.asarray(mat.baseColorFactor, dtype=float) / 255.
        elif visual.kind == 'vertex':
            rgba = np.einsum('ni,nij->nj', weights, visual.vertex_colors[mesh.faces[face]]) / 255.
        elif visual.kind == 'face':
            rgba = visual.face_colors[face].astype(float) / 255.
        else:
            warnings.append('Material without sampled color: neutral gray / 无采样颜色材质使用灰色')
        tangent = triangles[:, 1] - triangles[:, 0]
        tangent /= np.maximum(np.linalg.norm(tangent, axis=1, keepdims=True), 1e-20)
        bitangent = np.cross(normal, tangent)
        basis = np.stack((tangent, bitangent, normal), axis=2)
        quat_xyzw = Rotation.from_matrix(basis).as_quat()
        radius = np.sqrt(mesh.area / n) * coverage
        data = np.zeros((n, 62), dtype='<f4')
        data[:, :3] = pos
        data[:, 3:6] = normal
        data[:, 6:9] = (np.clip(rgba[:, :3], 0, 1) - .5) / .28209479177387814
        alpha = np.clip(rgba[:, 3] * .95, 1e-5, 1-1e-5)
        data[:, 54] = np.log(alpha / (1-alpha))
        data[:, 55:58] = np.log([radius, radius, radius * thickness])
        data[:, 58:62] = quat_xyzw[:, [3, 0, 1, 2]]
        chunks.append(data)
    data = np.concatenate(chunks)
    if not np.isfinite(data).all():
        raise ValueError('Nonfinite Gaussian data')
    fields = ['x','y','z','nx','ny','nz'] + [f'f_dc_{i}' for i in range(3)] + [f'f_rest_{i}' for i in range(45)] + ['opacity'] + [f'scale_{i}' for i in range(3)] + [f'rot_{i}' for i in range(4)]
    header = 'ply\nformat binary_little_endian 1.0\ncomment Mesh-to-GS surface sampling; not trained 3DGS\nelement vertex '+str(len(data))+'\n'+''.join(f'property float {k}\n' for k in fields)+'end_header\n'
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('xb') as f:
        f.write(header.encode('ascii'))
        f.write(data.tobytes())
    report = {'input':source.name, 'output':output.name, 'method':'anisotropic surface sampling, not trained 3DGS', 'points':len(data), 'parts':len(parts), 'bounds':[data[:,:3].min(0).tolist(),data[:,:3].max(0).tolist()], 'seed':seed, 'warnings':sorted(set(warnings)), 'limitations':['No reflection/refraction or lighting baking','No animation','FBX/Blend must be exported to GLB','Alpha blending and material extensions are approximated']}
    output.with_suffix('.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', nargs='?')
    parser.add_argument('-o', '--output')
    parser.add_argument('--count', type=int, default=150000)
    parser.add_argument('--seed', type=int, default=7)
    parser.add_argument('--coverage', type=float, default=.8)
    parser.add_argument('--thickness', type=float, default=.12)
    args = parser.parse_args()
    if not args.input:
        import tkinter as tk
        from tkinter import filedialog, messagebox
        root = tk.Tk(); root.withdraw()
        args.input = filedialog.askopenfilename(title='Select 3D model / 选择模型', filetypes=[('3D models','*.glb *.gltf *.obj *.ply *.stl')])
        if not args.input:
            return
        args.output = filedialog.asksaveasfilename(title='Save Gaussian PLY / 保存高斯', initialfile=Path(args.input).stem+'-gs.ply', defaultextension='.ply', filetypes=[('Gaussian PLY','*.ply')])
        if not args.output:
            return
        try:
            result = convert(args.input,args.output,args.count,args.seed,args.coverage,args.thickness)
            messagebox.showinfo('Complete / 完成', f"{result['points']} Gaussians\n{args.output}")
        except Exception as error:
            messagebox.showerror('Conversion failed / 转换失败', str(error))
            raise
    else:
        output = args.output or str(Path(args.input).with_name(Path(args.input).stem+'-gs.ply'))
        print(json.dumps(convert(args.input,output,args.count,args.seed,args.coverage,args.thickness),ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
