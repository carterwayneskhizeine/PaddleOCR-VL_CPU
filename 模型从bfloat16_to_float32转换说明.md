# PaddleOCRVL bfloat16 到 float32 模型转换

## 问题
每次运行 `PaddleOCRVL_main.py` 都需要等待很长时间，因为需要将模型从 bfloat16 转换为 float32。

## 解决方案
**一次性转换模型，之后直接使用转换好的 float32 模型！**

## 使用步骤

### 第一步：运行转换工具（只需运行一次）

```bash
python convert_models_once.py
```

这个脚本会：
1. 🔍 自动查找所有 PaddleOCR 下载的模型文件（`.safetensors`）
2. 🔬 检测哪些模型包含 bfloat16 格式的张量
3. 🔄 将 bfloat16 模型转换为 float32 格式
4. 💾 备份原始文件为 `.bak` 文件
5. ✅ 保存转换后的模型到原位置

**示例输出：**
```
================================================================================
PaddleOCR 模型转换工具 - bfloat16 → float32
================================================================================

正在搜索 PaddleOCR 模型文件...
✓ 找到 3 个 safetensors 文件

需要转换 2 个包含 bfloat16 的文件：
  1. model.safetensors
  2. encoder.safetensors

开始转换...

处理文件: model.safetensors
  路径: C:\Users\xxx\.paddleocr\models\xxx\model.safetensors
  ✓ 读取了 285 个张量
  ✓ 转换了 285 个 bfloat16 张量到 float32
  ✓ 已保存到: C:\Users\xxx\.paddleocr\models\xxx\model.safetensors
  原始大小: 892.45 MB
  转换后大小: 1784.90 MB
  ✓ 原文件已备份为: model.safetensors.bak
  ✓ 转换完成！

================================================================================
✅ 转换完成！共转换了 2 个文件
   原始文件已备份为 .bak 文件
   现在运行 PaddleOCRVL_main.py 将直接使用 float32 模型，无需再转换！
================================================================================
```

### 第二步：正常运行主程序

```bash
python PaddleOCRVL_main.py
```

## 文件说明

| 文件 | 说明 |
|------|------|
| `convert_models_once.py` | 一次性模型转换工具 |
| `setup_safetensors.py` | safetensors 兼容性补丁（支持 bfloat16 转换） |
| `PaddleOCRVL_main.py` | 主程序（OCR 识别） |

## 注意事项

1. **磁盘空间**：转换后的 float32 模型会比 bfloat16 大约 2 倍（因为每个数从 2 字节变为 4 字节）
2. **备份文件**：原始 bfloat16 模型会被保存为 `.bak` 文件，如果确认转换成功，可以删除备份文件节省空间
3. **重新下载模型**：如果你删除了 PaddleOCR 缓存目录，需要重新下载模型，然后再次运行 `convert_models_once.py`

## 如何恢复原始模型

如果需要恢复原始的 bfloat16 模型：

```bash
# 找到备份文件（.bak），将其重命名回 .safetensors
# 例如在 Windows PowerShell 中：
cd C:\Users\你的用户名\.paddleocr\models\某个模型目录
move model.safetensors model.safetensors.f32
move model.safetensors.bak model.safetensors
```

## 常见问题

**Q: 为什么不默认就转换？**  
A: 因为转换需要额外的磁盘空间（约 2 倍），并且有些用户可能希望保持原始模型格式。

**Q: 转换后精度会下降吗？**  
A: 不会！bfloat16 → float32 是精度提升的转换，不会损失精度。

**Q: 我可以删除 .bak 备份文件吗？**  
A: 确认转换成功且程序运行正常后，可以删除备份文件节省空间。

