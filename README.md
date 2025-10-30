# PaddleOCR CPU 环境安装与配置指南

## 项目概述

CPU 版 PaddleOCR-VL 项目，使用客户端-服务器架构，模型只需一次加载，避免重复初始化。

## 安装步骤

### 1. 创建 Conda 环境
```bash
conda create --name paddle python=3.12
conda activate paddle
```

### 2. 安装依赖
```bash
python -m pip install paddlepaddle==3.2.1 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/
python -m pip install "paddleocr[all]"
```

### 3. 验证安装
```bash
python -c "from paddleocr import PaddleOCR; print('PaddleOCR 安装成功！')"
```

## 使用方式

### 启动服务
```bash
# 命令行启动
python ocr_server.py

# 或双击批处理文件
start_ocr_service.bat
```

### 使用OCR
```bash
# 单张图片识别
python ocr_client.py 图片路径.jpg

# 批量处理，把需要处理的图片都放在OCR_Flies文件夹中
python batch_ocr_client.py

# 查看服务状态
python ocr_client.py --status

# 停止服务
python ocr_client.py --shutdown
```

### 批处理文件使用
- 启动服务：双击 `start_ocr_service.bat`
- 批量处理：双击 `batch_ocr_client_run.bat`
- 停止服务：双击 `stop_ocr_service.bat`

## 性能数据

**实际测试结果：**
- 模型初始化：121.66秒（约2分钟）
- 单张图片处理：80-260秒（1-4分钟，根据内容复杂度）
- 如果被识别成带图片的类型的：平均10分钟

**优势：** 模型只需一次加载，后续识别无需重复初始化

## 模型转换

### 一键转换 bfloat16 到 float32

```bash
python convert_models_once.py
```

**转换效果：**
- 消除运行时转换开销
- 提升后续加载速度
- 原始文件自动备份为 `.bak`

## 文件结构

```
项目根目录/
├── ocr_server.py              # 持久化服务端
├── ocr_client.py              # OCR客户端
├── batch_ocr_client.py        # 批量处理客户端
├── start_ocr_service.bat      # 启动服务脚本
├── stop_ocr_service.bat       # 停止服务脚本
├── batch_ocr_client_run.bat   # 批量处理脚本
├── convert_models_once.py     # 模型转换工具
├── setup_safetensors.py       # 兼容性补丁
└── OCR_Flies/                 # 待识别图片目录
```

## 输出结果

每个图片的识别结果保存在独立文件夹中：
```
output/batch_results/图片名称/
├── result.json  # 结构化数据
└── result.md    # 文本结果
```

## 注意事项

1. **内存占用**：服务运行期间持续占用约4GB内存
2. **单实例**：同一台电脑只能运行一个OCR服务实例
3. **网络连接**：客户端和服务端需要网络连接
4. **性能提示**：当前配置在CPU上运行速度不如官方PP-OCRv5 CPU版

## 相关链接

- [PaddleOCR GitHub](https://github.com/PaddlePaddle/PaddleOCR)
- [PaddleOCR 官网](https://www.paddleocr.ai)
- [PaddlePaddle 官网](https://www.paddlepaddle.org.cn)