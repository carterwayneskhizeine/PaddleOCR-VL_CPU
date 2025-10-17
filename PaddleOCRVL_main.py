"""
PaddleOCRVL 主程序
使用 setup_safetensors 中的兼容性补丁来支持 Paddle 框架
"""

# 第一步：应用 safetensors 兼容性补丁
from setup_safetensors import setup_safetensors_patch
setup_safetensors_patch()

# 现在可以正常使用 PaddleOCRVL 了
from paddleocr import PaddleOCRVL
import os

# 全局 pipeline 实例，避免重复初始化
_pipeline = None

def get_pipeline():
    """获取或创建 PaddleOCRVL pipeline 实例"""
    global _pipeline
    if _pipeline is None:
        print("正在初始化 PaddleOCRVL...")
        _pipeline = PaddleOCRVL()
    return _pipeline

def ocr_image(image_path, output_dir="output", print_result=True):
    """
    对单个图片进行 OCR 识别
    
    参数:
        image_path: 图片路径
        output_dir: 结果保存目录
        print_result: 是否打印识别结果
    
    返回:
        OCR 识别结果
    """
    pipeline = get_pipeline()
    
    if print_result:
        print(f"\n正在执行 OCR 识别: {image_path}")
    
    output = pipeline.predict(image_path)
    
    if print_result:
        print("="*80)
        print("识别结果:")
        print("="*80)
    
    # 为每个图片创建单独的输出文件夹
    image_name = os.path.splitext(os.path.basename(image_path))[0]
    save_path = os.path.join(output_dir, image_name)
    os.makedirs(save_path, exist_ok=True)
    
    for idx, res in enumerate(output):
        if print_result:
            print(f"\n页面 {idx + 1}:")
            res.print()
        res.save_to_json(save_path=save_path)
        res.save_to_markdown(save_path=save_path)
    
    if print_result:
        print(f"\n[完成] 结果已保存到 {save_path} 目录")
    
    return output

if __name__ == "__main__":
    # 单张图片测试示例
    test_image = r"C:\Users\gotmo\Pictures\Screenshots\Snipaste_2025-10-09_14-21-01.png"
    if os.path.exists(test_image):
        ocr_image(test_image)
    else:
        print(f"测试图片不存在: {test_image}")
        print("请使用 batch_ocr.py 进行批量处理，或修改此处的图片路径")
