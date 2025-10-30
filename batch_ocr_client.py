"""
基于客户端的批量OCR处理脚本
使用持久化OCR服务器进行批量识别
"""

import os
import time
from pathlib import Path
from ocr_client import PPOCRClient

# 支持的图片格式
SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp', '.gif'}


def get_image_files(folder_path):
    """获取文件夹下所有支持的图片文件"""
    image_files = []
    folder = Path(folder_path)

    if not folder.exists():
        print(f"警告: 文件夹不存在: {folder_path}")
        return image_files

    for file_path in folder.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_FORMATS:
            image_files.append(str(file_path))

    return sorted(image_files)


def batch_ocr_client(input_folder="OCR_Flies", output_folder="output/batch_results",
                    host='localhost', port=8888):
    """
    使用客户端进行批量OCR处理

    参数:
        input_folder: 输入图片文件夹路径
        output_folder: 输出结果文件夹路径
        host: 服务器地址
        port: 服务器端口
    """
    print("=" * 80)
    print("批量 OCR 处理开始 (客户端模式)")
    print("=" * 80)

    # 创建客户端
    client = PPOCRClient(host, port)

    # 检查服务器状态
    print("\n📡 正在连接OCR服务器...")
    status = client.get_server_status()

    if not status:
        print("❌ 无法连接到OCR服务器")
        print("请确保服务器已启动:")
        print("  python ocr_server.py")
        return

    print("✅ OCR服务器连接成功")
    print(f"   地址: {status['host']}:{status['port']}")
    print(f"   模型状态: {'🟢 已加载' if status['model_loaded'] else '🔴 未加载'}")

    if not status['model_loaded']:
        print("\n⚠ 警告: 服务器模型未加载完成")
        print("   请等待模型初始化完成后再试")
        return

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
    total_start_time = time.time()

    print(f"\n开始批量处理...")
    print("-" * 80)

    for i, image_path in enumerate(image_files, 1):
        try:
            print(f"\n[{i}/{len(image_files)}] 处理中: {os.path.basename(image_path)}")
            success = client.ocr_image(image_path, output_dir=output_folder, print_result=False)

            if success:
                success_count += 1
                print(f"  ✓ 完成")
            else:
                failed_files.append((image_path, "处理失败"))
                print(f"  ✗ 失败")

        except Exception as e:
            print(f"  ✗ 失败: {str(e)}")
            failed_files.append((image_path, str(e)))

    total_end_time = time.time()

    # 输出统计信息
    print("\n" + "=" * 80)
    print("批量处理完成")
    print("=" * 80)
    print(f"\n总文件数: {len(image_files)}")
    print(f"成功: {success_count}")
    print(f"失败: {len(failed_files)}")
    print(f"总耗时: {total_end_time - total_start_time:.2f} 秒")
    print(f"平均每张: {(total_end_time - total_start_time) / len(image_files):.2f} 秒")

    if failed_files:
        print("\n失败的文件:")
        for file_path, error in failed_files:
            print(f"  - {os.path.basename(file_path)}: {error}")

    print(f"\n结果保存在: {os.path.abspath(output_folder)}")


if __name__ == "__main__":
    # 配置参数
    INPUT_FOLDER = "OCR_Flies"  # 输入文件夹，可以修改为其他路径
    OUTPUT_FOLDER = "output/batch_results"  # 输出文件夹
    HOST = "localhost"  # 服务器地址
    PORT = 8888  # 服务器端口

    # 执行批量处理
    batch_ocr_client(INPUT_FOLDER, OUTPUT_FOLDER, HOST, PORT)