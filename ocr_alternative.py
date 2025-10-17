from paddleocr import PaddleOCR
import requests
from PIL import Image
from io import BytesIO

# 初始化 PaddleOCR（使用新的参数名称）
ocr = PaddleOCR(use_textline_orientation=True, lang='ch')

# 下载测试图片
url = "https://paddle-model-ecology.bj.bcebos.com/paddlex/imgs/demo_image/paddleocr_vl_demo.png"
response = requests.get(url)
img = Image.open(BytesIO(response.content))
img.save("temp_image.png")

# 执行 OCR（使用新的 predict API）
result = ocr.predict('temp_image.png')

# 输出结果
print(f"\n{'='*80}")
print(f"OCR 识别结果")
print(f"{'='*80}\n")

# result 是一个包含 OCRResult 对象的列表
for page_idx, page_result in enumerate(result):
    print(f"页面 {page_idx + 1}:")
    print(f"输入图片: {page_result['input_path']}")
    print(f"检测到 {len(page_result['rec_texts'])} 个文本区域\n")
    
    # 遍历所有识别出的文本
    for idx, (text, score) in enumerate(zip(page_result['rec_texts'], page_result['rec_scores'])):
        print(f"  [{idx + 1}] 文本: {text}")
        print(f"      置信度: {score:.4f} ({score*100:.2f}%)")
        print()
    
    print(f"\n{'='*80}\n")

# 将结果保存到文件
output_file = "output/ocr_result.txt"
import os
os.makedirs("output", exist_ok=True)

with open(output_file, 'w', encoding='utf-8') as f:
    for page_result in result:
        f.write(f"输入图片: {page_result['input_path']}\n")
        f.write(f"检测到 {len(page_result['rec_texts'])} 个文本区域\n\n")
        
        for idx, (text, score) in enumerate(zip(page_result['rec_texts'], page_result['rec_scores'])):
            f.write(f"[{idx + 1}] {text} (置信度: {score:.4f})\n")
        
        f.write("\n" + "="*80 + "\n")

print(f"结果已保存到: {output_file}")
print(f"图片已下载到: temp_image.png")

