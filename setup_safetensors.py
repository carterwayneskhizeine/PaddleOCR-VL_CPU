"""
修复 PaddleOCRVL 的 safetensors 兼容性问题
使用猴子补丁（Monkey Patch）方式

修复内容：
1. 支持 framework="paddle" 参数
2. 手动解析 safetensors 文件格式
3. 自动转换 bfloat16 到 float32（纯 numpy 实现，无需 PyTorch）

技术细节：
- 直接读取 safetensors 二进制文件
- 解析 header 获取张量信息
- 使用位运算将 bfloat16 转换为 float32
- 转换为 Paddle tensor
"""

import sys
import numpy as np
import paddle
from safetensors import safe_open as original_safe_open


class SafeOpenWrapper:
    """兼容的 safe_open 包装器，支持 paddle 框架"""
    
    def __init__(self, filename, framework, device="cpu"):
        self.filename = filename
        self.framework = framework
        self.device = device
        self.tensors = None
        self._original = None
    
    def bfloat16_to_float32(self, data_bytes):
        """手动将 bfloat16 字节数据转换为 float32 numpy 数组"""
        # bfloat16 是 16 位，每个元素 2 字节
        # 将字节数据转换为 uint16
        bfloat16_data = np.frombuffer(data_bytes, dtype=np.uint16)
        
        # bfloat16 转 float32: 在 bfloat16 值的后面补 16 位 0
        # bfloat16: [sign(1bit)][exp(8bit)][mantissa(7bit)]
        # float32:  [sign(1bit)][exp(8bit)][mantissa(23bit)]
        float32_data = np.zeros(len(bfloat16_data), dtype=np.float32)
        # 将 bfloat16 (uint16) 左移 16 位，填充到 float32 的高 16 位
        float32_data.view(np.uint32)[:] = bfloat16_data.astype(np.uint32) << 16
        
        return float32_data
    
    def __enter__(self):
        # 如果是 paddle 框架，需要特殊处理
        if self.framework == "paddle":
            print(f"  [加载中] 加载模型权重: {self.filename}")
            
            # 直接读取 safetensors 文件并手动解析
            import struct
            import json
            
            with open(self.filename, 'rb') as f:
                # 读取 header 长度 (前 8 字节)
                header_size = struct.unpack('<Q', f.read(8))[0]
                
                # 读取 header JSON
                header_bytes = f.read(header_size)
                header = json.loads(header_bytes.decode('utf-8'))
                
                # 获取数据起始位置
                data_start = 8 + header_size
                
                self.tensors = {}
                tensor_count = 0
                bfloat16_count = 0
                
                # 移除 __metadata__ 如果存在
                tensor_info = {k: v for k, v in header.items() if k != '__metadata__'}
                
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
                        # 转换 bfloat16 到 float32
                        tensor_data = self.bfloat16_to_float32(tensor_bytes)
                        tensor_data = tensor_data.reshape(shape)
                    else:
                        # 其他类型直接使用 numpy dtype
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
                    
                    # 转换为 paddle tensor
                    if self.device != "cpu" and paddle.is_compiled_with_cuda():
                        self.tensors[key] = paddle.to_tensor(tensor_data).cuda()
                    else:
                        self.tensors[key] = paddle.to_tensor(tensor_data)
                
                if bfloat16_count > 0:
                    print(f"  [转换] {bfloat16_count}/{tensor_count} 个张量从 bfloat16 转换为 float32")
                else:
                    print(f"  [完成] 加载了 {tensor_count} 个张量")
            
            return self
        else:
            # 其他框架使用原始的 safe_open
            self._original = original_safe_open(self.filename, self.framework, self.device)
            return self._original.__enter__()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.framework == "paddle":
            self.tensors = None
            return False
        else:
            return self._original.__exit__(exc_type, exc_val, exc_tb)
    
    def keys(self):
        if self.framework == "paddle":
            return self.tensors.keys()
        else:
            return self._original.keys()
    
    def get_tensor(self, name):
        if self.framework == "paddle":
            return self.tensors[name]
        else:
            return self._original.get_tensor(name)
    
    def get_slice(self, name):
        """获取张量切片（返回整个张量的视图）"""
        if self.framework == "paddle":
            # 返回整个张量（模拟切片功能）
            return self.tensors[name]
        else:
            return self._original.get_slice(name)
    
    def __getitem__(self, name):
        return self.get_tensor(name)
    
    def metadata(self):
        """获取元数据"""
        if self.framework == "paddle":
            return {}  # safetensors.paddle.load_file 不返回元数据
        else:
            return self._original.metadata()


def setup_safetensors_patch():
    """应用 safetensors 兼容性补丁"""
    import safetensors
    safetensors.safe_open = SafeOpenWrapper
    
    print("[OK] 已应用 safetensors 兼容性补丁")
    print("     - 支持 framework='paddle' 参数")
    print("     - 自动转换 bfloat16 -> float32\n")
