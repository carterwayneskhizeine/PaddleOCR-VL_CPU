"""
一次性转换工具：将 bfloat16 模型转换为 float32 并保存
运行一次后，之后就可以直接使用转换好的模型，无需每次都转换

使用方法：
1. 运行此脚本一次：python convert_models_once.py
2. 之后使用 PaddleOCRVL_main.py 时会自动使用转换好的模型
"""

import os
import sys
import json
import struct
import numpy as np
import paddle
from pathlib import Path
from safetensors import safe_open as original_safe_open
from safetensors.numpy import save_file


def find_safetensors_files():
    """查找 PaddleOCR 模型目录中的所有 safetensors 文件"""
    # 获取用户主目录下的 PaddleOCR 缓存目录
    home = Path.home()
    paddle_cache_dirs = [
        home / ".paddlex" / "official_models",  # PaddleX 官方模型目录
    ]
    
    safetensors_files = []
    for cache_dir in paddle_cache_dirs:
        if cache_dir.exists():
            print(f"  搜索目录: {cache_dir}")
            for file in cache_dir.rglob("*.safetensors"):
                safetensors_files.append(file)
    
    return safetensors_files


def check_if_bfloat16(filename):
    """检查 safetensors 文件是否包含 bfloat16 张量"""
    with open(filename, 'rb') as f:
        header_size = struct.unpack('<Q', f.read(8))[0]
        header_bytes = f.read(header_size)
        header = json.loads(header_bytes.decode('utf-8'))
        
        tensor_info = {k: v for k, v in header.items() if k != '__metadata__'}
        
        for key, info in tensor_info.items():
            if info['dtype'] == 'BF16':
                return True
    
    return False


def bfloat16_to_float32(data_bytes):
    """手动将 bfloat16 字节数据转换为 float32 numpy 数组"""
    bfloat16_data = np.frombuffer(data_bytes, dtype=np.uint16)
    float32_data = np.zeros(len(bfloat16_data), dtype=np.float32)
    float32_data.view(np.uint32)[:] = bfloat16_data.astype(np.uint32) << 16
    return float32_data


def convert_safetensors_to_float32(input_file, output_file):
    """转换 safetensors 文件从 bfloat16 到 float32"""
    print(f"\n处理文件: {input_file.name}")
    print(f"  路径: {input_file}")
    
    tensors_dict = {}
    
    with open(input_file, 'rb') as f:
        # 读取 header
        header_size = struct.unpack('<Q', f.read(8))[0]
        header_bytes = f.read(header_size)
        header = json.loads(header_bytes.decode('utf-8'))
        data_start = 8 + header_size
        
        tensor_info = {k: v for k, v in header.items() if k != '__metadata__'}
        
        tensor_count = 0
        bfloat16_count = 0
        
        for key, info in tensor_info.items():
            dtype_str = info['dtype']
            shape = info['shape']
            data_offsets = info['data_offsets']
            
            tensor_count += 1
            
            # 读取张量数据
            f.seek(data_start + data_offsets[0])
            tensor_bytes = f.read(data_offsets[1] - data_offsets[0])
            
            # 根据 dtype 解析数据
            if dtype_str == 'BF16':
                bfloat16_count += 1
                tensor_data = bfloat16_to_float32(tensor_bytes)
                tensor_data = tensor_data.reshape(shape)
            else:
                dtype_map = {
                    'F32': np.float32,
                    'F64': np.float64,
                    'I32': np.int32,
                    'I64': np.int64,
                    'U8': np.uint8,
                    'F16': np.float16,
                }
                np_dtype = dtype_map.get(dtype_str, np.float32)
                tensor_data = np.frombuffer(tensor_bytes, dtype=np_dtype).reshape(shape)
            
            tensors_dict[key] = tensor_data
        
        print(f"  ✓ 读取了 {tensor_count} 个张量")
        if bfloat16_count > 0:
            print(f"  ✓ 转换了 {bfloat16_count} 个 bfloat16 张量到 float32")
    
    # 保存为新的 safetensors 文件
    save_file(tensors_dict, output_file)
    print(f"  ✓ 已保存到: {output_file}")
    
    # 验证文件大小
    input_size = input_file.stat().st_size / (1024 * 1024)
    output_size = output_file.stat().st_size / (1024 * 1024)
    print(f"  原始大小: {input_size:.2f} MB")
    print(f"  转换后大小: {output_size:.2f} MB")
    
    return bfloat16_count > 0


def main():
    print("="*80)
    print("PaddleOCR 模型转换工具 - bfloat16 → float32")
    print("="*80)
    print()
    
    # 查找所有 safetensors 文件
    print("正在搜索 PaddleOCR 模型文件...")
    safetensors_files = find_safetensors_files()
    
    if not safetensors_files:
        print("❌ 未找到任何 safetensors 文件")
        print("   请先运行一次 PaddleOCRVL_main.py 让它下载模型")
        return
    
    print(f"✓ 找到 {len(safetensors_files)} 个 safetensors 文件\n")
    
    # 筛选包含 bfloat16 的文件
    bf16_files = []
    for file in safetensors_files:
        if check_if_bfloat16(file):
            bf16_files.append(file)
    
    if not bf16_files:
        print("✓ 所有模型已经是 float32 格式，无需转换！")
        return
    
    print(f"需要转换 {len(bf16_files)} 个包含 bfloat16 的文件：")
    for i, file in enumerate(bf16_files, 1):
        print(f"  {i}. {file.name}")
    
    print("\n开始转换...")
    
    converted_count = 0
    for file in bf16_files:
        # 备份原文件
        backup_file = file.with_suffix('.safetensors.bak')
        
        # 如果已经有备份，说明已经转换过了
        if backup_file.exists():
            print(f"\n⚠ 跳过 {file.name} (已有备份文件)")
            continue
        
        # 转换并保存到临时文件
        temp_file = file.with_suffix('.safetensors.tmp')
        
        try:
            if convert_safetensors_to_float32(file, temp_file):
                # 备份原文件
                file.rename(backup_file)
                print(f"  ✓ 原文件已备份为: {backup_file.name}")
                
                # 将转换后的文件重命名为原文件名
                temp_file.rename(file)
                print(f"  ✓ 转换完成！")
                converted_count += 1
            else:
                # 如果没有 bfloat16，删除临时文件
                temp_file.unlink()
                print(f"  ⚠ 此文件不包含 bfloat16，跳过")
        
        except Exception as e:
            print(f"  ❌ 转换失败: {e}")
            if temp_file.exists():
                temp_file.unlink()
            continue
    
    print("\n" + "="*80)
    if converted_count > 0:
        print(f"✅ 转换完成！共转换了 {converted_count} 个文件")
        print(f"   原始文件已备份为 .bak 文件")
        print(f"   现在运行 PaddleOCRVL_main.py 将直接使用 float32 模型，无需再转换！")
    else:
        print("✅ 所有需要的模型已经是 float32 格式")
    print("="*80)


if __name__ == "__main__":
    main()

