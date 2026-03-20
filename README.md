# 无人机状态监控系统 - 项目总结

## 项目概述

本项目实现了一个完整的无人机状态监控系统，包含自定义消息协议、多个无人机节点发布状态信息、以及 ROS Web 桥接服务，支持通过 WebSocket 在 Web 应用中实时监控无人机状态。

## 项目结构

```
Cluster/
├── drone_msg_pkg/              # 无人机自定义协议包
│   ├── msg/
│   │   └── DroneState.msg      # DroneState 消息定义
│   ├── CMakeLists.txt          # 构建配置
│   ├── package.xml             # 包配置
│   └── README.md               # 协议包说明
│
├── drone001/                   # 第一架无人机节点
│   ├── src/
│   │   └── drone001_node.cpp   # drone001 节点实现
│   ├── CMakeLists.txt          # 构建配置
│   ├── package.xml             # 包配置
│   └── README.md               # 节点说明
│
├── drone002/                   # 第二架无人机节点
│   ├── src/
│   │   └── drone002_node.cpp   # drone002 节点实现
│   ├── CMakeLists.txt          # 构建配置
│   ├── package.xml             # 包配置
│   └── README.md               # 节点说明
│
├── ros_bridge_server/          # ROS Web 桥接服务
│   ├── ros_bridge_server.launch.xml    # ROS2 启动脚本
│   ├── drone_status_subscriber.py      # Python WebSocket 订阅者
│   └── README.md               # 桥接服务说明
│
└── README.md                   # 本项目总览
```

## 1. drone_msg_pkg - 无人机自定义协议

### 功能说明
定义了无人机状态消息 `DroneState`，包含以下字段：
- `drone_name`: 无人机名称
- `x, y, z`: 位置坐标（米）

### 使用方法
```bash
# 编译
cd /home/fenghaoheng/Cluster
colcon build --packages-select drone_msg_pkg

# 设置环境
source install/setup.bash

# 查看消息类型
ros2 interface show drone_msg_pkg/msg/DroneState
```

### 消息格式
```msg
# 无人机状态信息消息
# 无人机名称
string drone_name 
# 位置坐标 (米)
float64 x
float64 y
float64 z
```

## 2. drone001 - 第一架无人机节点

### 功能说明
发布 drone001 无人机的实时状态信息：
- 无人机名称: "drone001"
- 飞行轨迹: 正向圆周运动
  - x = 5 × sin(t)
  - y = 5 × cos(t)
  - z = 2.0 + 0.5 × sin(2t)
- 发布频率: 1 Hz (每秒1次)
- 发布话题: `/drone_status`

### 使用方法
```bash
# 编译
cd /home/fenghaoheng/Cluster
colcon build --packages-select drone001

# 设置环境
source install/setup.bash

# 运行节点
ros2 run drone001 drone001_node

# 查看发布的消息
ros2 topic echo /drone_status
```

### 代码特点
- [Drone001Node](file:///home/fenghaoheng/Cluster/drone001/src/drone001_node.cpp#L14-L66) 类继承自 `rclcpp::Node`
- 使用定时器每秒更新无人机位置
- 实时打印无人机状态日志

## 3. drone002 - 第二架无人机节点

### 功能说明
发布 drone002 无人机的实时状态信息：
- 无人机名称: "drone002"
- 飞行轨迹: 反向圆周运动（与 drone001 相位相反）
  - x = -5 × sin(t)
  - y = -5 × cos(t)
  - z = 2.0 + 0.5 × sin(2t)
- 发布频率: 1 Hz (每秒1次)
- 发布话题: `/drone_status`

### 使用方法
```bash
# 编译
cd /home/fenghaoheng/Cluster
colcon build --packages-select drone002

# 设置环境
source install/setup.bash

# 运行节点
ros2 run drone002 drone002_node

# 查看发布的消息
ros2 topic echo /drone_status
```

### 与 drone001 的区别
- 相同的飞行半径和高度
- 相反的飞行方向（相位差180度）
- 可以同时运行，模拟多无人机协同

## 4. ros_bridge_server - ROS Web 桥接服务

### 功能说明
提供 WebSocket 接口，将 ROS2 话题暴露给 Web 应用：
- WebSocket 端口: 9090
- 话题白名单: 只允许 `/drone_status` 话题
- 地址绑定: 0.0.0.0 (允许外部连接)
- 支持多客户端同时连接

### 使用方法

#### 1. 启动 ROS Bridge 服务
```bash
# 方法1: 使用 launch 文件
ros2 launch ros_bridge_server ros_bridge_server.launch.xml

# 方法2: 手动启动
ros2 run rosbridge_server rosbridge_websocket --port 9090
```

#### 2. Python WebSocket 订阅者
```bash
# 安装依赖
pip install websockets

# 运行订阅者
cd /home/fenghaoheng/Cluster/ros_bridge_server
python3 drone_status_subscriber.py

# 指定 WebSocket 地址
python3 drone_status_subscriber.py ws://localhost:9090
```

#### 3. Web 应用集成
```html
<!DOCTYPE html>
<html>
<head>
    <title>无人机状态监控</title>
</head>
<body>
    <div id="status"></div>
    
    <script>
        const ws = new WebSocket('ws://localhost:9090');
        
        ws.onopen = function() {
            // 订阅 /drone_status 话题
            ws.send(JSON.stringify({
                op: 'subscribe',
                id: 'subscribe_1',
                type: 'drone_msg_pkg/msg/DroneState',
                topic: '/drone_status'
            }));
        };
        
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            if (data.op === 'publish') {
                document.getElementById('status').innerHTML = 
                    `无人机: ${data.msg.drone_name}<br>` +
                    `位置: (${data.msg.x}, ${data.msg.y}, ${data.msg.z})`;
            }
        };
    </script>
</body>
</html>
```

### WebSocket API

#### 订阅话题
```json
{
  "op": "subscribe",
  "id": "subscribe_1",
  "type": "drone_msg_pkg/msg/DroneState",
  "topic": "/drone_status"
}
```

#### 取消订阅
```json
{
  "op": "unsubscribe",
  "id": "unsubscribe_1",
  "topic": "/drone_status"
}
```

## 完整使用流程

### 1. 编译所有包
```bash
cd /home/fenghaoheng/Cluster
colcon build
source install/setup.bash
```

### 2. 运行无人机节点
```bash
# 终端1: 运行 drone001
ros2 run drone001 drone001_node

# 终端2: 运行 drone002
ros2 run drone002 drone002_node
```

### 3. 运行 ROS Bridge 服务
```bash
# 终端3: 启动 ROS Bridge
ros2 launch ros_bridge_server ros_bridge_server.launch.xml
```

### 4. 查看状态
```bash
# 终端4: 查看原始话题
ros2 topic echo /drone_status

# 终端5: 运行 Python 订阅者
cd /home/fenghaoheng/Cluster/ros_bridge_server
python3 drone_status_subscriber.py
```

## 技术特点

### 1. 模块化设计
- 消息定义、节点实现、桥接服务分离
- 每个包独立编译和部署
- 易于扩展和维护

### 2. 标准化协议
- 使用 ROS2 标准的消息格式
- 遵循 ROS2 C++ 节点开发规范
- 支持 ROS2 生态系统工具

### 3. 多无人机支持
- 支持多个无人机节点同时运行
- 每个无人机有独立的名称标识
- 可模拟多无人机协同场景

### 4. Web 集成
- 通过 WebSocket 暴露 ROS2 话题
- 支持 Web 应用实时监控
- 提供 Python 订阅者示例

## 故障排除

### 1. 编译错误
```bash
# 清理并重新编译
cd /home/fenghaoheng/Cluster
rm -rf build install log
colcon build
```

### 2. 无法连接 WebSocket
- 检查 rosbridge_server 是否运行
- 确认端口 9090 未被占用
- 检查防火墙设置

### 3. 无法接收消息
- 确认无人机节点正在运行
- 检查话题白名单配置
- 使用 `ros2 topic list` 查看可用话题

## 许可证

Apache-2.0

## 作者

Fenghaoheng <1006122343@qq.com>

## 更新日志

### v1.0.0 (2026-03-20)
- 初始版本发布
- 实现 drone_msg_pkg 自定义消息协议
- 实现 drone001 和 drone002 无人机节点
- 实现 ROS Web Bridge 服务
- 支持 WebSocket 订阅
