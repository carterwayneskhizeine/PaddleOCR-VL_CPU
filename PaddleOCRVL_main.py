"""
PaddleOCRVL 主程序
使用 setup_safetensors 中的兼容性补丁来支持 Paddle 框架
"""

# 第一步：应用 safetensors 兼容性补丁
from setup_safetensors import setup_safetensors_patch
setup_safetensors_patch()

# 现在可以正常使用 PaddleOCRVL 了
from paddleocr import PaddleOCRVL

print("正在初始化 PaddleOCRVL...")
pipeline = PaddleOCRVL()

print("正在执行 OCR 识别...\n")
output = pipeline.predict(r"C:\Users\gotmo\Pictures\Screenshots\Snipaste_2025-10-09_14-21-01.png")

print("="*80)
print("识别结果:")
print("="*80)

for idx, res in enumerate(output):
    print(f"\n页面 {idx + 1}:")
    res.print()
    res.save_to_json(save_path="output")
    res.save_to_markdown(save_path="output")
    
print("\n[完成] 结果已保存到 output 目录")
