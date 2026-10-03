---
license: other
license_link: LICENSE
license_name: qwen-research
library_name: videox_fun
tags:
- controlnet
- controlnet-union
- text-to-image
- image-to-image
- image-inpainting
tasks:
- text-to-image-synthesis
---

# Qwen-Image-2.1-Fun-Controlnet-Union

[![Github](https://img.shields.io/badge/🎨%20Code-VideoX_Fun-blue)](https://github.com/aigc-apps/VideoX-Fun)

## 概述

Qwen-Image-2.1-Fun-Controlnet-Union 是面向 **[Qwen-Image 2.1](https://github.com/aigc-apps/VideoX-Fun)**（flow-matching 文生图 DiT）的 **ControlNet-Union 控制分支**。单个 checkpoint 即可驱动 **8 种结构控制条件**（Canny、深度、灰度、HED、Lineart、MLSD、姿态、涂鸦）*以及*图像修复，无需为每种条件单独准备权重。checkpoint **仅包含控制分支**（`control_img_in` 与 16 个 `control_blocks`，约 7.0 GB），需叠加加载到 Qwen-Image 2.1 基础 transformer 之上。

## 模型文件说明

| 文件名 | 说明 |
|--|--|
| Qwen-Image-2.1-Fun-Controlnet-Union.safetensors | Qwen-Image 2.1 的 ControlNet-Union 分支权重，仅包含控制分支（`control_img_in` + 16 个 `control_blocks`，约 7.0 GB），以 `strict=False` 叠加加载到 Qwen-Image 2.1 基础 transformer 之上。单个 checkpoint 覆盖 8 种控制条件及图像修复。 |

## 模型特性
- **一个 checkpoint 统管 8 种控制条件**：Canny、深度、灰度、HED、Lineart、MLSD、姿态、涂鸦控制图的文生图，无需为每种条件单独切换 checkpoint。
- **更密集的控制注入**：控制分支在 32 个 transformer 块中每 2 层接入一个跳接（`control_layers = [0, 2, 4, …, 30]`，共 16 个注入点）。每条控制跳接都经零初始化的 `before_proj` / `after_proj` 门控投影后叠加回主分支，在基础模型保持冻结的同时实现严格的结构还原。
- **控制与修复共用同一分支**：控制输入拓宽至 `control_in_dim = 129` —— `控制潜变量(64) | 掩码(1) | 掩码后图像潜变量(64)`。纯控制时掩码/掩码图像通道补零；修复时同一分支根据 prompt 重绘掩码区域。二者还可**叠加使用**——同时输入一张控制图与掩码，被重绘的区域会同时跟随 prompt 与给定的结构。
- **CFG 蒸馏快速采样**：独立的示例脚本以 `guidance_scale = 1.0` 推理（每步仅一次前向计算，无需 classifier-free guidance）。
- `control_context_scale` 在控制跳接叠加回主分支前对其进行缩放：`1.0` 为最强控制（下方所有结果均用此值），调低可减弱结构约束，`0.0` 则完全关闭控制分支。
- **提示词写法**：prompt 应描述**整张目标图像**；被打掩码的区域由掩码通道表达，而非文字。提示词越详细，生成越稳定。
- Qwen-Image 2.1 使用 **Qwen3-VL** 文本编码器 + processor 编码 prompt（及条件图），其 VAE 解码为 **RGBA**，因此所有预览图均以 PNG 保存。

## 支持的控制条件

| 条件 | 控制信号 |
|--|--|
| Canny | Canny 边缘图 |
| Depth | 单目深度图 |
| Grayscale | 灰度（亮度）图 |
| HED | HED 边缘检测图 |
| Lineart | 线稿提取图 |
| MLSD | 直线段检测图 |
| Pose | DWPose 人体骨架 |
| Scribble | 手绘 / 草图线条 |

任何与目标画布尺寸一致的普通 RGB 控制图均可使用；模型对不同线条粗细、阈值与裁剪都有很好的容忍度。

## 生成效果

以下所有样例均在 `num_inference_steps = 40`、`control_context_scale = 1.0`、随机种子 43 的条件下生成。每列中，上排为控制图，下排为生成结果。

<table border="0" style="width: 100%; text-align: left; margin-top: 20px;">
  <tr><td>Canny</td><td>Depth</td><td>Grayscale</td><td>HED</td><td>Lineart</td><td>MLSD</td><td>Pose</td><td>Scribble</td></tr>
  <tr>
    <td><img src="https://huggingface.co/alibaba-pai/Qwen-Image-2.1-Fun-Controlnet-Union/resolve/main/asset/control_2_00025069.png" width="100%"></td>
    <td><img src="https://huggingface.co/alibaba-pai/Qwen-Image-2.1-Fun-Controlnet-Union/resolve/main/asset/control_5_00005389.png" width="100%"></td>
    <td><img src="https://huggingface.co/alibaba-pai/Qwen-Image-2.1-Fun-Controlnet-Union/resolve/main/asset/control_1_00014291.png" width="100%"></td>
    <td><img src="https://huggingface.co/alibaba-pai/Qwen-Image-2.1-Fun-Controlnet-Union/resolve/main/asset/control_6_00009388.png" width="100%"></td>
    <td><img src="https://huggingface.co/alibaba-pai/Qwen-Image-2.1-Fun-Controlnet-Union/resolve/main/asset/control_4_00003435.png" width="100%"></td>
    <td><img src="https://huggingface.co/alibaba-pai/Qwen-Image-2.1-Fun-Controlnet-Union/resolve/main/asset/control_4_00027496.png" width="100%"></td>
    <td><img src="https://huggingface.co/alibaba-pai/Qwen-Image-2.1-Fun-Controlnet-Union/resolve/main/asset/control_4_00000931.png" width="100%"></td>
    <td><img src="https://huggingface.co/alibaba-pai/Qwen-Image-2.1-Fun-Controlnet-Union/resolve/main/asset/control_13_00000494.png" width="100%"></td>
  </tr>
  <tr>
    <td><img src="https://huggingface.co/alibaba-pai/Qwen-Image-2.1-Fun-Controlnet-Union/resolve/main/results/control_2_00025069.png" width="100%"></td>
    <td><img src="https://huggingface.co/alibaba-pai/Qwen-Image-2.1-Fun-Controlnet-Union/resolve/main/results/control_5_00005389.png" width="100%"></td>
    <td><img src="https://huggingface.co/alibaba-pai/Qwen-Image-2.1-Fun-Controlnet-Union/resolve/main/results/control_1_00014291.png" width="100%"></td>
    <td><img src="https://huggingface.co/alibaba-pai/Qwen-Image-2.1-Fun-Controlnet-Union/resolve/main/results/control_6_00009388.png" width="100%"></td>
    <td><img src="https://huggingface.co/alibaba-pai/Qwen-Image-2.1-Fun-Controlnet-Union/resolve/main/results/control_4_00003435.png" width="100%"></td>
    <td><img src="https://huggingface.co/alibaba-pai/Qwen-Image-2.1-Fun-Controlnet-Union/resolve/main/results/control_4_00027496.png" width="100%"></td>
    <td><img src="https://huggingface.co/alibaba-pai/Qwen-Image-2.1-Fun-Controlnet-Union/resolve/main/results/control_4_00000931.png" width="100%"></td>
    <td><img src="https://huggingface.co/alibaba-pai/Qwen-Image-2.1-Fun-Controlnet-Union/resolve/main/results/control_13_00000494.png" width="100%"></td>
  </tr>
</table>

### 图像修复（+ 控制）

源图中被打上掩码的区域会根据 prompt 重新绘制，画面其余部分原样保留。掩码图中，**需要重新生成的区域为白色**，**需要保留的区域为黑色**。由于控制与修复共用同一分支，这里在掩码之外还同时输入了一张控制图（DWPose 骨架），被重绘的区域因此也会跟随给定的姿态。

<table border="0" style="width: 100%; text-align: left; margin-top: 20px;">
  <tr><td>源图</td><td>掩码</td><td>姿态控制</td><td>修复输出</td></tr>
  <tr>
    <td><img src="https://huggingface.co/alibaba-pai/Qwen-Image-2.1-Fun-Controlnet-Union/resolve/main/asset/inpaint_source.png" width="100%"></td>
    <td><img src="https://huggingface.co/alibaba-pai/Qwen-Image-2.1-Fun-Controlnet-Union/resolve/main/asset/inpaint_mask.png" width="100%"></td>
    <td><img src="https://huggingface.co/alibaba-pai/Qwen-Image-2.1-Fun-Controlnet-Union/resolve/main/asset/inpaint_control.jpg" width="100%"></td>
    <td><img src="https://huggingface.co/alibaba-pai/Qwen-Image-2.1-Fun-Controlnet-Union/resolve/main/results/inpaint.png" width="100%"></td>
  </tr>
</table>

## 推理

更多细节请参见 VideoX-Fun 代码仓库。

首先克隆 VideoX-Fun 仓库并创建模型目录：

```sh
# 克隆代码
git clone https://github.com/aigc-apps/VideoX-Fun.git

# 进入 VideoX-Fun 目录
cd VideoX-Fun

# 创建模型目录
mkdir -p models/Diffusion_Transformer
```

随后将 Qwen-Image 2.1 基础模型与本 checkpoint 下载至 `models/Diffusion_Transformer` 下：

```
📦 models/
├──  Diffusion_Transformer/
│   ├── 📂 Qwen-Image-2.1/
│   └── 📂 Qwen-Image-2.1-Fun-Controlnet-Union/
│       └──  Qwen-Image-2.1-Fun-Controlnet-Union.safetensors
```

接着修改 `examples/qwenimage21_fun/predict_t2i_control.py`（图像修复用 `predict_i2i_inpaint.py`）顶部的配置项，然后运行：

```python
model_name          = "models/Diffusion_Transformer/Qwen-Image-2.1"
config_path         = "config/qwenimage21/qwenimage21_control.yaml"
transformer_path    = "models/Diffusion_Transformer/Qwen-Image-2.1-Fun-Controlnet-Union/Qwen-Image-2.1-Fun-Controlnet-Union.safetensors"
control_image       = "asset/pose.jpg"
# 仅修复任务需要：
inpaint_image       = "asset/8.png"
mask_image          = "asset/mask.png"
prompt              = "描述整张目标图像的 prompt"
```

```sh
python examples/qwenimage21_fun/predict_t2i_control.py
```

注意事项：
- `config_path` **必须**是 `config/qwenimage21/qwenimage21_control.yaml`：只有它能按 checkpoint 期望的结构完整搭建控制分支（`control_layers: [0, 2, 4, …, 30]`、`control_in_dim: 129`）；配置不匹配会静默丢弃或错位加载控制权重，产出错误结果。
- 纯控制（不做修复输入）时，pipeline 会自动把掩码 / 掩码图像通道补零，因此这个支持修复的 checkpoint 一样能正确跑普通的 Canny/深度/… 控制任务。
- 控制 checkpoint 只含控制分支，`model_name` 目录中必须有 Qwen-Image 2.1 基础权重。
- `control_context_scale = 1.0` 是适配器期望的取值；调低可减弱结构约束。
- `sample_size` 设定输出画布（如 `[1728, 992]`）；请将宽高均保持为 32 的倍数，以免控制图被拉伸变形。
- `use_kv_cache = True` 会在首个去噪步后缓存文本 / 条件图的 key/value，在固定分辨率下加速推理。
- 显存：transformer 加 Qwen3-VL 文本编码器无法在单张消费级显卡上全量驻留；单卡大显存请使用 `model_group_offload`（速度最快）或 `model_cpu_offload_and_qfloat8`。

## 许可证

本模型为 Qwen-Image 2.1 的衍生模型，依据 [Qwen Research License](https://modelscope.cn/models/Qwen/Qwen-Image-2.1/file/view/master/LICENSE) 发布。使用前请仔细阅读许可条款。
