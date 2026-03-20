# ROS Bridge Server 使用指南

## 项目结构

```
ros_bridge_server/
├── ros_bridge_server.launch.xml    # ROS2 启动脚本
├── drone_status_subscriber.py      # Python WebSocket 订阅者
└── README.md                       # 本说明文档
```

## 功能说明

### 1. ROS Bridge 启动脚本

**文件**: `ros_bridge_server.launch.xml`

该脚本启动 rosbridge_websocket 服务，配置如下：
- WebSocket 端口: 9090
- 话题白名单: 只允许 `/drone_status` 话题
- 地址绑定: 0.0.0.0 (允许外部连接)

### 2. Python WebSocket 订阅者

**文件**: `drone_status_subscriber.py`

该脚本通过 WebSocket 连接到 rosbridge_server，订阅 `/drone_status` 话题并实时显示无人机状态信息。

## 安装依赖

### 1. 安装 rosbridge_server

```bash
# Ubuntu/Debian
sudo apt-get install ros-<distro>-rosbridge-suite

# 替换 <distro> 为你的 ROS2 发行版 (如 humble, foxy, ironic)
```

### 2. 安装 Python 依赖

```bash
pip install websockets
```

## 使用方法

### 方法 1: 使用启动脚本

```bash
# 1. 编译项目
cd /home/fenghaoheng/Cluster
colcon build

# 2. 设置环境
source install/setup.bash

# 3. 运行 drone001 节点
ros2 run drone001 drone001_node

# 4. 运行 rosbridge 服务
ros2 launch ros_bridge_server ros_bridge_server.launch.xml
```

### 方法 2: 手动启动

```bash
# 1. 启动 drone001 节点
ros2 run drone001 drone001_node

# 2. 启动 rosbridge_websocket
ros2 run rosbridge_server rosbridge_websocket --port 9090

# 3. 运行 Python 订阅者
python3 drone_status_subscriber.py ws://localhost:9090
```

### 方法 3: 使用 ros2 launch

```bash
# 直接使用 ros2 launch 运行
ros2 launch ros_bridge_server ros_bridge_server.launch.xml
```

## WebSocket API

### 订阅话题

```json
{
  "op": "subscribe",
  "id": "subscribe_1",
  "type": "drone_msg_pkg/msg/DroneState",
  "topic": "/drone_status"
}
```

### 取消订阅

```json
{
  "op": "unsubscribe",
  "id": "unsubscribe_1",
  "topic": "/drone_status"
}
```

### 发布消息

```json
{
  "op": "publish",
  "topic": "/drone_status",
  "msg": {
    "drone_name": "drone001",
    "x": 0.0,
    "y": 0.0,
    "z": 0.0
  }
}
```

## DroneState 消息格式

```json
{
  "drone_name": "drone001",
  "x": 0.0,
  "y": 0.0,
  "z": 0.0
}
```

## 运行示例

### 终端 1: 启动 drone001 节点

```bash
cd /home/fenghaoheng/Cluster
source install/setup.bash
ros2 run drone001 drone001_node
```

### 终端 2: 启动 rosbridge 服务

```bash
cd /home/fenghaoheng/Cluster
source install/setup.bash
ros2 launch ros_bridge_server ros_bridge_server.launch.xml
```

### 终端 3: 运行 Python 订阅者

```bash
cd /home/fenghaoheng/Cluster/ros_bridge_server
python3 drone_status_subscriber.py
```

### 终端 4: 查看原始话题数据

```bash
source install/setup.bash
ros2 topic echo /drone_status
```

## 配置选项

### 修改 WebSocket 端口

在 `ros_bridge_server.launch.xml` 中修改:

```xml
<param name="port" value="9090"/>
```

### 添加更多话题到白名单

```xml
<param name="topic_whitelist" value="['/drone_status', '/other_topic']"/>
```

### 启用 SSL

```xml
<param name="ssl" value="true"/>
<param name="certfile" value="/path/to/cert.pem"/>
<param name="keyfile" value="/path/to/key.pem"/>
```

## 故障排除

### 1. 连接失败

检查:
- rosbridge_server 是否正在运行
- 防火墙设置
- WebSocket 地址是否正确

### 2. 无法接收消息

检查:
- 话题是否在白名单中
- drone001 节点是否正在发布消息
- 订阅消息格式是否正确

### 3. 消息类型错误

确保:
- drone_msg_pkg 已编译
- 消息类型名称正确: `drone_msg_pkg/msg/DroneState`

## Web 应用集成

### HTML + JavaScript 示例

```html
<!DOCTYPE html>
<html>
<head>
    <title>无人机状态监控</title>
</head>
<body>
    <h1>无人机状态监控</h1>
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

## 许可证

Apache-2.0
