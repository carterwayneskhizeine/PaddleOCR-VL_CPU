"""
批量 OCR 处理脚本
自动识别 OCR_Flies 文件夹下的所有图片文件并进行 OCR 识别
"""

import os
from pathlib import Path
from PaddleOCRVL_main import ocr_image

# 支持的图片格式
SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp', '.gif'}

def get_image_files(folder_path):
    """
    获取文件夹下所有支持的图片文件
    
    参数:
        folder_path: 文件夹路径
    
    返回:
        图片文件路径列表
    """
    image_files = []
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"警告: 文件夹不存在: {folder_path}")
        return image_files
    
    for file_path in folder.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_FORMATS:
            image_files.append(str(file_path))
    
    return sorted(image_files)

def batch_ocr(input_folder="OCR_Flies", output_folder="output/batch_results"):
    """
    批量处理文件夹中的所有图片
    
    参数:
        input_folder: 输入图片文件夹路径
        output_folder: 输出结果文件夹路径
    """
    print("="*80)
    print("批量 OCR 处理开始")
    print("="*80)
    
    # 获取所有图片文件
    image_files = get_image_files(input_folder)
    
    if not image_files:
        print(f"\n在 {input_folder} 文件夹中没有找到支持的图片文件")
        print(f"支持的格式: {', '.join(SUPPORTED_FORMATS)}")
        return
    
    print(f"\n找到 {len(image_files)} 个图片文件:")
    for i, img_path in enumerate(image_files, 1):
        print(f"  {i}. {os.path.basename(img_path)}")
    
    # 创建输出文件夹
    os.makedirs(output_folder, exist_ok=True)
    
    # 批量处理
    success_count = 0
    failed_files = []
    
    print(f"\n开始批量处理...")
    print("-"*80)
    
    for i, image_path in enumerate(image_files, 1):
        try:
            print(f"\n[{i}/{len(image_files)}] 处理中: {os.path.basename(image_path)}")
            ocr_image(image_path, output_dir=output_folder, print_result=False)
            success_count += 1
            print(f"  ✓ 完成")
        except Exception as e:
            print(f"  ✗ 失败: {str(e)}")
            failed_files.append((image_path, str(e)))
    
    # 输出统计信息
    print("\n" + "="*80)
    print("批量处理完成")
    print("="*80)
    print(f"\n总文件数: {len(image_files)}")
    print(f"成功: {success_count}")
    print(f"失败: {len(failed_files)}")
    
    if failed_files:
        print("\n失败的文件:")
        for file_path, error in failed_files:
            print(f"  - {os.path.basename(file_path)}: {error}")
    
    print(f"\n结果保存在: {os.path.abspath(output_folder)}")

if __name__ == "__main__":
    # 配置参数
    INPUT_FOLDER = "OCR_Flies"  # 输入文件夹，可以修改为其他路径
    OUTPUT_FOLDER = "output/batch_results"  # 输出文件夹
    
    # 执行批量处理
    batch_ocr(INPUT_FOLDER, OUTPUT_FOLDER)

