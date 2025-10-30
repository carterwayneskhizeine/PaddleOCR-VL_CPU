"""
PaddleOCRVL 客户端
用于与持久化OCR服务器交互
"""

import json
import socket
import time
import os
import sys
from typing import Dict, Any, Optional


class PPOCRClient:
    """PaddleOCRVL 客户端"""

    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.timeout = 300  # 5分钟超时

    def _send_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """发送请求到服务器"""
        try:
            # 创建socket连接
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.timeout)
                sock.connect((self.host, self.port))

                # 发送请求
                request_data = json.dumps(request, ensure_ascii=False).encode('utf-8')
                sock.send(request_data)

                # 接收响应
                response_data = sock.recv(8192 * 10)  # 增大缓冲区
                if not response_data:
                    return None

                return json.loads(response_data.decode('utf-8'))

        except socket.error as e:
            print(f"❌ 连接错误: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ 响应解析错误: {e}")
            return None
        except Exception as e:
            print(f"❌ 请求失败: {e}")
            return None

    def is_server_running(self) -> bool:
        """检查服务器是否运行"""
        response = self._send_request({'type': 'status'})
        return response and response.get('success')

    def get_server_status(self) -> Optional[Dict[str, Any]]:
        """获取服务器状态"""
        response = self._send_request({'type': 'status'})
        return response if response and response.get('success') else None

    def ocr_image(self, image_path: str, output_dir: str = 'output', print_result: bool = True) -> bool:
        """
        对单个图片进行OCR识别

        参数:
            image_path: 图片路径
            output_dir: 结果保存目录
            print_result: 是否打印结果

        返回:
            bool: 是否成功
        """
        if not os.path.exists(image_path):
            if print_result:
                print(f"❌ 图片文件不存在: {image_path}")
            return False

        if print_result:
            print(f"\n🔍 发送OCR请求: {os.path.basename(image_path)}")

        request = {
            'type': 'ocr',
            'image_path': os.path.abspath(image_path),
            'output_dir': output_dir
        }

        start_time = time.time()
        response = self._send_request(request)
        end_time = time.time()

        if not response:
            if print_result:
                print("❌ 无法连接到OCR服务器")
                print("   请确保服务器已启动: python ocr_server.py")
            return False

        if response.get('success'):
            if print_result:
                print("=" * 80)
                print(f"✅ OCR识别完成")
                print(f"   处理时间: {end_time - start_time:.2f} 秒")
                print(f"   服务器处理时间: {response.get('processing_time', 0):.2f} 秒")
                print(f"   结果保存到: {response.get('save_path')}")
                print("=" * 80)
            return True
        else:
            if print_result:
                print(f"❌ OCR识别失败: {response.get('error')}")
            return False

    def shutdown_server(self) -> bool:
        """关闭服务器"""
        print("🛑 正在发送关闭请求...")
        response = self._send_request({'type': 'shutdown'})

        if response and response.get('success'):
            print("✅ 服务器已关闭")
            return True
        else:
            print("❌ 无法关闭服务器")
            return False


def main():
    """命令行客户端"""
    import argparse

    parser = argparse.ArgumentParser(description='PaddleOCRVL 客户端')
    parser.add_argument('image', nargs='?', help='要识别的图片路径')
    parser.add_argument('--host', default='localhost', help='服务器地址')
    parser.add_argument('--port', type=int, default=8888, help='服务器端口')
    parser.add_argument('--output', default='output', help='结果输出目录')
    parser.add_argument('--status', action='store_true', help='查看服务器状态')
    parser.add_argument('--shutdown', action='store_true', help='关闭服务器')

    args = parser.parse_args()

    client = PPOCRClient(args.host, args.port)

    # 检查服务器状态
    if args.status:
        print("📡 正在检查服务器状态...")
        status = client.get_server_status()
        if status:
            print("=" * 60)
            print("🟢 服务器状态:")
            print(f"   地址: {status['host']}:{status['port']}")
            print(f"   运行状态: {'🟢 运行中' if status['server_running'] else '🔴 已停止'}")
            print(f"   模型状态: {'🟢 已加载' if status['model_loaded'] else '🔴 未加载'}")
            print("=" * 60)
        else:
            print("🔴 服务器未运行或无法连接")
        return

    # 关闭服务器
    if args.shutdown:
        client.shutdown_server()
        return

    # OCR识别
    if args.image:
        success = client.ocr_image(args.image, args.output)
        sys.exit(0 if success else 1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()