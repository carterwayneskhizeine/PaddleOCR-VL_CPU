# PaddleOCR CPU 环境安装与配置指南

本文档介绍如何从零开始安装和配置 CPU 版 PaddleOCR 环境。

## 项目背景

在 Windows 环境下配置 PaddleOCR 的 Docker 遇到了一些问题，因此通过 Vibe Coding 创建了这个项目。

## 技术说明

- 所有代码都是使用 Cursor Vibe Coding 生成的
- **性能提示**：当前配置在 CPU 上运行速度不如官方的 PP-OCRv5 CPU 版本配合 PyTorch 等加速包
- 官方正确配置可以跑满 100% 的 CPU，但当前 Vibe 编码版本无法达到相同性能水平

## 性能表现

### 启动时间
- 每次启动时，加载模型和识别前的准备工作需要 **10-15 分钟**

### 识别速度
- **少量文字**：只有几句话的识别大约需要 **10 秒**
- **大量文字**：一页长文章的识别需要 **5 分钟左右**
- 识别速度与图片中的字数成正比

## 已知限制

曾尝试使用 CPU 版的 PyTorch 来加速，但由于报错过多而放弃。

## 后续改进

欢迎有兴趣的开发者继续通过 Vibe Coding 进行优化，特别是修改成支持 CPU 版的 PyTorch 加速。

## 📋 前置要求

- 已安装 Anaconda 或 Miniconda
- Python 3.12
- Windows/Linux/MacOS 操作系统

## 🚀 安装步骤

### 1. 创建 Conda 虚拟环境

打开命令行工具（Windows 用户推荐使用 Anaconda Prompt），执行以下命令创建名为 `paddle` 的 Python 3.12 环境：

```bash
conda create --name paddle python=3.12
```

按提示输入 `y` 确认安装。

### 2. 激活虚拟环境

创建完成后，激活该环境：

```bash
conda activate paddle
```

**注意**：后续所有操作都需要在激活 paddle 环境后进行。

### 3. 安装 PaddlePaddle

安装 PaddlePaddle 3.2.0 版本（CPU 版本）：

```bash
python -m pip install paddlepaddle==3.2.0 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/
```

**说明**：
- 使用 `-i` 参数指定国内镜像源，下载速度更快
- 此为 CPU 版本，适用于大多数场景
- 如需 GPU 版本，请参考 [PaddlePaddle 官方文档](https://www.paddlepaddle.org.cn/)

### 4. 安装 PaddleOCR

安装 PaddleOCR 及其所有依赖：

```bash
python -m pip install "paddleocr[all]"
```

**说明**：
- `[all]` 会安装所有可选依赖，包括 PDF 解析、表格识别等功能
- 如果只需基础功能，可以使用：`pip install paddleocr`

### 5. 验证安装

验证安装是否成功：

```bash
python -c "from paddleocr import PaddleOCR; print('PaddleOCR 安装成功！')"
```

如果没有报错，说明安装成功。

## 📚 本项目使用说明

本项目提供了批量 OCR 处理功能：

### 使用方法

1. 将需要识别的图片放入 `OCR_Flies` 文件夹
2. 双击运行 `批量OCR.bat`（Windows）
3. 等待处理完成，结果保存在 `output/batch_results` 文件夹

详细使用说明请参阅 [批量OCR使用说明.md](./批量OCR使用说明.md)

## 🔗 相关链接

### 官方资源

- **PaddleOCR GitHub**: https://github.com/PaddlePaddle/PaddleOCR
- **PaddleOCR 官网**: https://www.paddleocr.ai
- **PaddlePaddle 官网**: https://www.paddlepaddle.org.cn
- **官方文档**: https://github.com/PaddlePaddle/PaddleOCR/blob/main/README_ch.md

### 功能特性

- ✅ 支持 100+ 种语言的 OCR 识别
- ✅ PP-OCRv5 - 最新的高精度 OCR 模型
- ✅ PP-StructureV3 - 文档结构分析
- ✅ PP-ChatOCRv4 - 文档问答
- ✅ PaddleOCR-VL - 视觉语言模型
- ✅ 表格识别、版面分析、公式识别等

## 💡 技术支持

如遇到问题，可以通过以下方式获取帮助：

1. 查看 [PaddleOCR FAQ](https://github.com/PaddlePaddle/PaddleOCR/blob/main/doc/doc_ch/FAQ.md)
2. 在 [GitHub Issues](https://github.com/PaddlePaddle/PaddleOCR/issues) 搜索或提问
3. 加入 PaddlePaddle 技术交流群（见官网）

## 📝 更新日志

- **2025-10** - 创建本安装指导文档
- **2025-10** - PaddlePaddle 3.2.0 版本
- **2024-10** - PP-OCRv5 发布

---

**祝你使用愉快！** 🎉

如有任何问题或建议，欢迎反馈。

