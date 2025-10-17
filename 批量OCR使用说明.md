# 批量 OCR 使用说明

## 功能说明

本项目现在支持两种使用方式：

### 1. 单张图片 OCR（PaddleOCRVL_main.py）
- 对单张图片进行 OCR 识别
- 可以作为模块导入使用

### 2. 批量 OCR（batch_ocr.py）
- 自动识别 `OCR_Flies` 文件夹下的所有图片
- 批量进行 OCR 处理
- 结果保存到 `output/batch_results` 文件夹

## 使用方法

### 方法一：使用批处理文件（推荐）

1. 将需要识别的图片放入 `OCR_Flies` 文件夹
2. 双击运行 `批量OCR.bat`
3. 等待处理完成，结果会保存在 `output/batch_results` 文件夹

### 方法二：命令行运行

```bash
# 批量处理
python batch_ocr.py

# 单张图片处理
python PaddleOCRVL_main.py
```

### 方法三：作为模块使用

```python
from PaddleOCRVL_main import ocr_image
from batch_ocr import batch_ocr

# 处理单张图片
result = ocr_image("path/to/image.png")

# 批量处理
batch_ocr(input_folder="OCR_Flies", output_folder="output/batch_results")
```

## 支持的图片格式

- JPG / JPEG
- PNG
- BMP
- TIFF / TIF
- WEBP
- GIF

## 输出结果

每个图片的识别结果会保存在独立的文件夹中，包含：
- JSON 格式的结构化数据
- Markdown 格式的文本结果

结果目录结构：
```
output/
  └── batch_results/
      ├── 图片1/
      │   ├── result.json
      │   └── result.md
      ├── 图片2/
      │   ├── result.json
      │   └── result.md
      └── ...
```

## 配置修改

如果需要修改输入/输出文件夹，请编辑 `batch_ocr.py` 文件的底部：

```python
if __name__ == "__main__":
    INPUT_FOLDER = "OCR_Flies"  # 修改输入文件夹路径
    OUTPUT_FOLDER = "output/batch_results"  # 修改输出文件夹路径
    
    batch_ocr(INPUT_FOLDER, OUTPUT_FOLDER)
```

## 注意事项

1. 首次运行时，系统会自动初始化 PaddleOCRVL 模型，可能需要一些时间
2. 在批量处理过程中，模型只会初始化一次，提高处理效率
3. 处理大量图片时，请确保有足够的磁盘空间存储结果
4. 如果某个图片处理失败，程序会继续处理其他图片，并在最后显示失败列表

