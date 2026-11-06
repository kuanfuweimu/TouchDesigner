# TouchDesigner

TouchDesigner 工程与实验 / Projects and experiments.

## Gaussian Breathing / 高斯呼吸

[打开工程目录与说明](TouchDesigner-Gaussian-Breathing/README.md)

基于 Tim Gerritsen Gaussian Splatting 组件与 Lake Heckaman 教程，增加独立的位置扰动和尺度呼吸控制。包含可编辑 `.toe` / `.tox`、示例模型、预览及运行验证记录。

下载本仓库 ZIP 并完整解压，打开 `TouchDesigner-Gaussian-Breathing/GaussianBreathing.toe`。保留 `assets` 文件夹。默认 3840 × 2160；Preview 可切换至 1280 × 720。

Download the repository ZIP, extract all files, and open the TOE. Keep the assets folder beside it. Tested in TouchDesigner 2025.32460.

**当前素材为蜥蜴扫描，不是视频植物或用户提出的 LIULI 琉璃龙；琉璃龙尚未下载。**

![720p preview](TouchDesigner-Gaussian-Breathing/preview-1280x720.png)

Original component and sample remain credited to their authors; no blanket license is granted over third-party assets. See the project README for sources and validation limits.

## Mesh to GS / 普通 3D 转高斯

[工具与操作说明](Mesh-to-GS/README.md)：GLB / GLTF / OBJ / mesh PLY / STL → Gaussian PLY。包含 Windows 文件选择启动器、转换源码、示例和 TD 查看器。采用网格表面采样，非训练重建；不转换动画。FBX 先导出 GLB。

同时修复 GaussianBreathing 容器宽高的相对路径表达式错误。
