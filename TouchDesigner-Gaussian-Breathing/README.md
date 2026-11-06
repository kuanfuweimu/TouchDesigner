# Gaussian Breathing / 高斯呼吸

基于 Tim Gerritsen 原版 GaussianSplatting-1.0 组件，复刻 Lake Heckaman 教程的位置扰动与尺度呼吸。原渲染器保留，新增控制在 /project1/GaussianBreathing 的 Breathing 页。
Based on Tim Gerritsen's original renderer; adds the tutorial's position noise and scale breathing controls.

## 使用 / Open
1. 完整解压压缩包，保留 assets 子目录；双击 GaussianBreathing.toe。
2. 默认输出 3840 × 2160。开启 Preview 切到 1280 × 720，仍为 16:9。
3. 选 GaussianBreathing，在 Breathing 页调 Position motion、Scale breathing、两个 frequency 和 Noise travel speed。时间轴需播放。
4. null_output 是最终 TOP。cam_preview / null_target 控制机位和目标；原 cameraViewport 保留在内部。
5. GaussianBreathing.tox 可导入已有工程；导入到其他目录后，请在 Splat file 指向本包 assets/hornedlizard-preview.ply。

Unzip the entire package and open GaussianBreathing.toe. Keep assets beside the project. Preview switches between 4K and 720p. Import the TOX into another project and reselect the supplied PLY when its project folder differs.

## 参数 / Controls
- Position motion：位置扰动幅度，默认 0.035；设 0 关闭。Position noise amplitude.
- Scale breathing：对数尺度扰动，默认 0.5；设 0 关闭。Log-scale noise amplitude.
- Position / Scale frequency：两路独立呼吸频率，默认 0.073 / 0.11 Hz。
- Noise travel speed：噪声移动速度，默认 0.08。
- Alpha threshold / Splat size：透明度裁切 / 整体高斯尺寸。

## 素材与限制 / Assets and limits
这不是视频植物的逐像素复刻。植物扫描位于作者 Patreon，本包未访问、未购买或复制该付费素材。这里用 Derivative POPs 示例 hornedlizard.spz 转换为 Gaussian PLY，并抽样至 220,000 个 splat，适合验证动画机制；抽样与新机位会暴露扫描空洞和飞点。
The tutorial's plant scan is not included. The supplied lizard is a public Derivative example, sampled to 220,000 splats; scan holes and floaters remain visible. No frame-rate guarantee is made.

原版组件需要包含 opacity、f_dc_*、f_rest_*、scale_*、rot_* 的 Gaussian PLY；普通网格 PLY 不能直接替代。原生 SPZ 属性名称不同，不要直接选 SPZ。换自己的模型后，需调整 cam_preview、null_target 并触发内部 GaussianSplat 的 Reload。
This renderer expects Gaussian PLY, not mesh PLY or native SPZ. Reframe the camera after replacing the scan.

## 验证 / Validation
TouchDesigner 2025.32460：运行时节点错误为零；两路 LFO 数值与两帧图像均发生变化；实际读取到 3840 × 2160 输出及 1280 × 720 预览。Null 颜色为 #2F59AD。验证详情见 validation.json。
The final project uses relative asset paths and excludes the development filesystem command listener. No desktop UI automation was used. Interactive desktop usability and sustained FPS were not benchmarked.

## 来源 / Credits
- Tim Gerritsen Gaussian Splatting asset: https://derivative.ca/community-post/asset/gaussian-splatting/69107
- Lake Heckaman tutorial: https://www.youtube.com/watch?v=es5Vy0VTJ8M
- Sample: Derivative POPs examples, GaussianSplat/SPZ/hornedlizard.spz.
- Original component is retained in assets/GaussianSplatting-1.0-original.tox. Original authors retain their rights; consult original asset terms before redistribution.

## Requested alternative / 待替换素材
LIULI Year of the Dragon Glass Sculpture Splat — UniconeDesign: https://poly.cam/capture/73CF32ED-F550-492E-BAF3-C5FA5DE8845E

尚未下载或接入此琉璃龙模型；当前工程仍使用蜥蜴扫描。This requested dragon model has not been downloaded or integrated.
