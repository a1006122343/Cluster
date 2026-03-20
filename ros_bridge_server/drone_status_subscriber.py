#!/usr/bin/env python3
"""
ROS2 WebSocket 订阅者脚本

该脚本通过 WebSocket 连接到 rosbridge_server，订阅 /drone_status 话题
并实时显示接收到的无人机状态信息。

使用方法:
    python3 drone_status_subscriber.py [websocket_url]

参数:
    websocket_url: WebSocket 服务器地址 (默认: ws://localhost:9090)

依赖:
    - websockets: Python WebSocket 库
    - asyncio: Python 异步 I/O 框架

安装依赖:
    pip install websockets
"""

import asyncio
import json
import sys
import websockets
from typing import Dict, Any, Optional


class DroneStatusSubscriber:
    """
    无人机状态 WebSocket 订阅者类
    
    通过 WebSocket 连接到 rosbridge_server，订阅并处理 /drone_status 话题消息
    """
    
    def __init__(self, websocket_url: str = "ws://localhost:9090"):
        """
        初始化订阅者
        
        参数:
            websocket_url: WebSocket 服务器地址
        """
        self.websocket_url = websocket_url
        self.websocket = None
        self.subscriber_id = 0
        self.running = False
        
    async def connect(self) -> bool:
        """
        连接到 WebSocket 服务器
        
        返回:
            bool: 连接成功返回 True，否则返回 False
        """
        try:
            self.websocket = await websockets.connect(self.websocket_url)
            print(f"✓ 已连接到 WebSocket 服务器: {self.websocket_url}")
            return True
        except Exception as e:
            print(f"✗ 连接失败: {e}")
            return False
    
    async def close(self):
        """关闭 WebSocket 连接"""
        if self.websocket:
            await self.websocket.close()
            print("\n✓ WebSocket 连接已关闭")
    
    async def send_message(self, message: Dict[str, Any]) -> Optional[int]:
        """
        发送消息到 WebSocket 服务器
        
        参数:
            message: 要发送的消息字典
            
        返回:
            int 或 None: 消息 ID，如果发送失败返回 None
        """
        try:
            if self.websocket:
                await self.websocket.send(json.dumps(message))
                return message.get('id')
        except Exception as e:
            print(f"✗ 发送消息失败: {e}")
        return None
    
    async def subscribe_topic(self, topic_name: str = "/drone_status") -> bool:
        """
        订阅指定话题
        
        参数:
            topic_name: 要订阅的话题名称
            
        返回:
            bool: 订阅成功返回 True，否则返回 False
        """
        self.subscriber_id += 1
        subscribe_msg = {
            "op": "subscribe",
            "id": f"subscribe_{self.subscriber_id}",
            "type": "drone_msg_pkg/msg/DroneState",
            "topic": topic_name
        }
        
        result = await self.send_message(subscribe_msg)
        if result:
            print(f"✓ 已订阅话题: {topic_name}")
            return True
        return False
    
    async def process_message(self, message: str):
        """
        处理接收到的消息
        
        参数:
            message: 接收到的 JSON 字符串消息
        """
        try:
            data = json.loads(message)
            
            # 检查是否为发布消息
            if data.get('op') == 'publish':
                topic = data.get('topic')
                msg = data.get('msg', {})
                
                if topic == '/drone_status':
                    self.print_drone_status(msg)
                    
        except json.JSONDecodeError as e:
            print(f"✗ 消息解析失败: {e}")
    
    def print_drone_status(self, msg: Dict[str, Any]):
        """
        打印无人机状态信息
        
        参数:
            msg: 包含无人机状态的字典
        """
        drone_name = msg.get('drone_name', 'Unknown')
        x = msg.get('x', 0.0)
        y = msg.get('y', 0.0)
        z = msg.get('z', 0.0)
        
        # 格式化输出
        timestamp = asyncio.get_event_loop().time()
        print(f"\n[{timestamp:.2f}] 无人机状态更新")
        print(f"  无人机名称: {drone_name}")
        print(f"  位置坐标: ({x:.2f}, {y:.2f}, {z:.2f})")
        print("-" * 50)
    
    async def receive_messages(self):
        """接收并处理 WebSocket 消息"""
        try:
            async for message in self.websocket:
                await self.process_message(message)
        except websockets.exceptions.ConnectionClosed:
            print("\n✗ WebSocket 连接已断开")
        except Exception as e:
            print(f"✗ 接收消息时出错: {e}")
    
    async def run(self):
        """运行订阅者主循环"""
        # 连接到 WebSocket 服务器
        if not await self.connect():
            return
        
        # 订阅 /drone_status 话题
        if not await self.subscribe_topic("/drone_status"):
            await self.close()
            return
        
        self.running = True
        print("\n✓ 开始接收无人机状态消息...")
        print("按 Ctrl+C 退出\n")
        
        # 持续接收消息
        await self.receive_messages()


async def main():
    """主函数"""
    # 获取 WebSocket URL 参数
    websocket_url = sys.argv[1] if len(sys.argv) > 1 else "ws://localhost:9090"
    
    print("=" * 60)
    print("ROS2 WebSocket 无人机状态订阅者")
    print("=" * 60)
    print(f"WebSocket 服务器: {websocket_url}")
    print(f"订阅话题: /drone_status")
    print("=" * 60)
    
    subscriber = DroneStatusSubscriber(websocket_url)
    
    try:
        await subscriber.run()
    except KeyboardInterrupt:
        print("\n\n用户中断程序")
    except Exception as e:
        print(f"\n程序异常退出: {e}")
    finally:
        await subscriber.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序已退出")
