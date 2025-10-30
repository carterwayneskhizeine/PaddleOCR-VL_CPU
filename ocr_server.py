"""
PaddleOCRVL 持久化服务端
模型加载后持续运行，直到手动停止
"""

import os
import json
import time
import signal
import socket
import threading
from typing import Dict, List, Any
import traceback

# 应用 safetensors 兼容性补丁
from setup_safetensors import setup_safetensors_patch
setup_safetensors_patch()

from paddleocr import PaddleOCRVL


class PPOCRServer:
    """PaddleOCRVL 持久化服务器"""

    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.pipeline = None
        self.server_socket = None
        self.running = False

        # 注册信号处理器
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """处理终止信号"""
        print(f"\n收到信号 {signum}，正在优雅关闭服务...")
        self.stop()

    def initialize_model(self):
        """初始化PaddleOCRVL模型"""
        print("=" * 60)
        print("正在初始化 PaddleOCRVL 模型...")
        print("这通常需要 2 分钟，请耐心等待...")
        print("=" * 60)

        start_time = time.time()

        try:
            self.pipeline = PaddleOCRVL()
            end_time = time.time()

            print("=" * 60)
            print(f"✅ 模型初始化完成！")
            print(f"   耗时: {end_time - start_time:.2f} 秒")
            print("   模型已加载并保持挂载状态")
            print("   可以随时通过客户端进行OCR识别")
            print("=" * 60)

        except Exception as e:
            print(f"❌ 模型初始化失败: {e}")
            print(traceback.format_exc())
            return False

        return True

    def start_server(self):
        """启动服务器"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)

            self.running = True
            print(f"\n🚀 PPOCR 服务已启动")
            print(f"   把需要批处理的图片文件放到 OCR_Flies 目录下")
            print(f"   然后双击 batch_ocr_client_run.bat - 批量处理")
            print(f"   监听地址: {self.host}:{self.port}")
            print(f"   等待客户端连接...")
            print(f"   按 Ctrl+C 停止服务\n")

            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    print(f"📡 客户端连接: {client_address}")

                    # 为每个客户端创建新线程处理
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()

                except socket.error as e:
                    if self.running:
                        print(f"❌ 服务器错误: {e}")
                    break

        except Exception as e:
            print(f"❌ 服务器启动失败: {e}")
            print(traceback.format_exc())

    def handle_client(self, client_socket, client_address):
        """处理客户端请求"""
        try:
            # 设置超时时间为30分钟
            client_socket.settimeout(1800)

            while self.running:
                # 接收请求数据
                data = client_socket.recv(4096)
                if not data:
                    break

                try:
                    request = json.loads(data.decode('utf-8'))
                    response = self.process_request(request)

                    # 发送响应
                    response_data = json.dumps(response, ensure_ascii=False).encode('utf-8')
                    client_socket.send(response_data)

                    if request.get('type') == 'status':
                        break  # 状态查询后断开连接

                except json.JSONDecodeError as e:
                    error_response = {
                        'success': False,
                        'error': f'JSON解析错误: {e}'
                    }
                    client_socket.send(json.dumps(error_response).encode('utf-8'))

        except Exception as e:
            print(f"❌ 客户端处理错误: {e}")
        finally:
            client_socket.close()
            print(f"🔌 客户端断开连接: {client_address}")

    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理OCR请求"""
        request_type = request.get('type')

        if request_type == 'ocr':
            return self.handle_ocr_request(request)
        elif request_type == 'status':
            return self.handle_status_request()
        elif request_type == 'shutdown':
            return self.handle_shutdown_request()
        else:
            return {
                'success': False,
                'error': f'未知请求类型: {request_type}'
            }

    def handle_ocr_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理OCR识别请求"""
        if not self.pipeline:
            return {
                'success': False,
                'error': '模型未初始化'
            }

        image_path = request.get('image_path')
        output_dir = request.get('output_dir', 'output')

        if not image_path or not os.path.exists(image_path):
            return {
                'success': False,
                'error': f'图片文件不存在: {image_path}'
            }

        try:
            print(f"🔍 开始OCR识别: {os.path.basename(image_path)}")
            start_time = time.time()

            # 执行OCR
            output = self.pipeline.predict(image_path)

            end_time = time.time()

            # 保存结果
            image_name = os.path.splitext(os.path.basename(image_path))[0]
            save_path = os.path.join(output_dir, image_name)
            os.makedirs(save_path, exist_ok=True)

            results = []
            for idx, res in enumerate(output):
                result_data = {
                    'page_idx': idx + 1,
                    'json_path': os.path.join(save_path, f'result.json'),
                    'md_path': os.path.join(save_path, f'result.md')
                }
                res.save_to_json(save_path=save_path)
                res.save_to_markdown(save_path=save_path)
                results.append(result_data)

            print(f"✅ OCR完成，耗时: {end_time - start_time:.2f} 秒")

            return {
                'success': True,
                'processing_time': end_time - start_time,
                'results': results,
                'save_path': save_path
            }

        except Exception as e:
            error_msg = f"OCR处理失败: {e}"
            print(f"❌ {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'details': traceback.format_exc()
            }

    def handle_status_request(self) -> Dict[str, Any]:
        """处理状态查询请求"""
        return {
            'success': True,
            'server_running': self.running,
            'model_loaded': self.pipeline is not None,
            'host': self.host,
            'port': self.port
        }

    def handle_shutdown_request(self) -> Dict[str, Any]:
        """处理关闭服务请求"""
        print("🛑 收到关闭服务请求")
        self.running = False
        return {
            'success': True,
            'message': '服务正在关闭'
        }

    def stop(self):
        """停止服务器"""
        self.running = False

        if self.server_socket:
            self.server_socket.close()

        print("🔌 PPOCR 服务已停止")

        # 清理资源
        if self.pipeline:
            del self.pipeline
            self.pipeline = None

        print("🧹 模型资源已释放")


def main():
    """主函数"""
    print("=" * 60)
    print("PaddleOCRVL 持久化服务器")
    print("=" * 60)

    server = PPOCRServer()

    # 初始化模型
    if not server.initialize_model():
        print("❌ 模型初始化失败，服务器退出")
        return

    # 启动服务器
    try:
        server.start_server()
    except KeyboardInterrupt:
        print("\n⚠ 收到中断信号")
    except Exception as e:
        print(f"❌ 服务器运行错误: {e}")
    finally:
        server.stop()


if __name__ == "__main__":
    main()