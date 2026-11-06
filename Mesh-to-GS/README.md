# Mesh to GS / 普通 3D 转高斯

将 GLB、GLTF、OBJ、网格 PLY、STL 转为 Gaussian PLY：面积加权采样三角面，读取贴图或顶点颜色，生成沿表面排列的扁椭球高斯。支持场景实例与变换，固定随机种子可复现。

输出包含 SH DC 颜色、不透明度 logit、对数尺度和 wxyz 四元数，兼容随附 TD 渲染器；这是直接表面采样，不是多视角训练重建。

This is **direct anisotropic surface sampling**, not multi-view trained 3D Gaussian Splatting. It produces a real Gaussian PLY with SH DC colors, opacity logits, log scales and wxyz quaternions, compatible with the bundled TouchDesigner renderer.

## Windows 使用 / Windows usage

1. 完整解压，双击 `Start-Mesh-to-GS.cmd`。需要 Python 3.12（包含 Tk）；首次启动会联网安装本目录的隔离依赖，不改系统 Python 包。
2. 选择模型，然后选择输出 PLY 文件名。默认 150,000 个高斯；不覆盖已存在文件，重新运行请换输出名。
3. 打开 `MeshToGSViewer.toe` 查看随包提供的纹理球示例。
4. 在 `/project1/GaussianBreathing` 的 **Breathing → Splat file** 选择新 PLY，内部 GaussianSplat → Reload 可重新加载。
5. 修改 `cam_preview` / `null_target` 适配模型尺度和位置。默认 3840×2160；开启 Preview 为 1280×720。
6. Position motion / Scale breathing 默认关闭以检查模型，调高即可添加之前的呼吸效果。

The launcher installs local dependencies, opens input/output dialogs and converts on CPU. Opening the viewer alone does not convert a model. Select the resulting PLY in Splat file and reframe the camera as needed. The exported TOX can be imported into another project; reselect the PLY if the project folder differs.

### English steps

1. Extract all files and double-click `Start-Mesh-to-GS.cmd`. Python 3.12 with Tk is required. First launch installs isolated dependencies in this folder using the internet, without changing system Python packages.
2. Select an input model and an output PLY filename. The default is 150,000 Gaussians. Existing outputs are never overwritten; choose a new name when repeating a conversion.
3. Open `MeshToGSViewer.toe` to inspect the supplied textured sphere.
4. Select the generated PLY under `/project1/GaussianBreathing` → Breathing → Splat file; use the internal GaussianSplat → Reload when necessary.
5. Adjust `cam_preview` and `null_target` for the model’s size and location. Default output is 3840 × 2160; Preview switches to 1280 × 720.
6. Position motion and Scale breathing start at zero for model inspection; increase them to add animation.

命令行可自定义数量 / CLI:

```powershell
.venv\Scripts\python.exe mesh_to_gs.py "model.glb" -o "model-gs.ply" --count 300000
```

`--coverage` 控制椭球覆盖，默认 0.8；`--thickness` 控制法线方向厚度比例，默认 0.12。增大覆盖可减少孔洞，也可能增加边缘模糊。保留输入的坐标和单位，不自动归一化。

English: `--coverage` controls tangent-plane coverage (default 0.8); `--thickness` controls normal-axis thickness relative to radius (default 0.12). More coverage can reduce holes but blur edges. Input coordinates and units are preserved without normalization.

## 输入与效果限制 / Input and visual limitations

- **FBX / Blend：先导出 GLB，当前不直接读取。动画不转换。**
- OBJ/GLTF 需保留 MTL、图片或 BIN 等关联文件；优先用单文件 GLB。
- 只近似基础颜色和透明度，不烘焙灯光、玻璃折射、金属反射、程序材质或法线贴图。材质扩展、复杂多材质与纹理平铺效果未全面验证。
- 表面采样不是训练重建；局部可能有孔洞、接缝或模糊。不承诺等同照片训练的 3DGS。
- 薄片与透明模型可能出现排序或背面颜色混合问题。输出分辨率不代表采样细节自动增加。
- 未下载 LIULI 琉璃龙；示例为本工具生成的纹理球。

### English limitations

- Export FBX or Blend to GLB first; neither is read directly. Animation is not converted.
- Keep OBJ/GLTF companion MTL, image and BIN files. Prefer a self-contained GLB.
- Only base color and opacity are approximated. Lighting, glass refraction, metallic reflections, procedural materials and normal maps are not baked. Material extensions, complex multi-material assets and texture wrapping are not fully validated.
- This is surface sampling, not trained reconstruction. Holes, seams or blur may remain; photo-trained 3DGS quality is not promised.
- Thin or transparent models may show sorting or backface color mixing. Higher output resolution does not automatically increase sampling detail.
- The LIULI dragon is not downloaded. The example is a generated textured sphere.

## 验证 / Verification

已验证纹理 GLB → 100,000 Gaussian PLY → TouchDesigner 2025.32460 实际渲染。验证实例变换、顶点颜色、四元数归一化、椭球法线方向、有限数值及禁止覆盖输出；可运行 `python -m unittest test_converter.py`。

截图所示容器 width/height 错误修复为直接读取自身 Preview 参数，不再依赖 `op('render1')` 的相对寻址。UI 文件选择窗口未通过自动化操作测试。没有使用屏幕自动化或 Blender 渲染。

English: A textured GLB was converted to 100,000 Gaussians and actually rendered in TouchDesigner 2025.32460. Tests cover scene instance transforms, vertex colors, unit quaternions, normal alignment, finite numbers and overwrite protection. Run `python -m unittest test_converter.py` to repeat unit tests. The container width/height fix reads its own Preview parameter instead of resolving `op('render1')` relatively. The file-picker UI was not automation-tested. No screen automation or Blender rendering was used.

## 来源 / Credits

- Gaussian renderer: Tim Gerritsen, https://derivative.ca/community-post/asset/gaussian-splatting/69107
- Breathing animation reference: Lake Heckaman, https://www.youtube.com/watch?v=es5Vy0VTJ8M
- Mesh IO / texture sampling: https://trimesh.org/formats.html and https://trimesh.org/trimesh.visual.texture.html

原组件作者权利保留；本工具的加入不改变第三方组件授权。No blanket relicensing of the bundled third-party renderer.
