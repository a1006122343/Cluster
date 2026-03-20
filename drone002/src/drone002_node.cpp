#include <memory>
#include <chrono>
#include "rclcpp/rclcpp.hpp"
#include "drone_msg_pkg/msg/drone_state.hpp"

using namespace std::chrono_literals;

/**
 * @brief drone002无人机节点
 * 
 * 该节点定时向 "/drone_status" 话题发布无人机的 DroneState 消息
 * 包含无人机名称和位置坐标信息
 */
class Drone002Node : public rclcpp::Node
{
public:
  /**
   * @brief 构造函数，初始化节点和发布者
   * 
   * 创建 drone_state 发布者，设置定时器每100ms发布一次状态信息
   */
  Drone002Node()
  : Node("drone002_node")
  {
    // 创建发布者，发布到 "/drone_status" 话题，队列大小为10
    publisher_ = this->create_publisher<drone_msg_pkg::msg::DroneState>("drone_status", 10);
    
    // 初始化定时器，每100ms调用一次 timer_callback
    timer_ = this->create_wall_timer(
      1s, std::bind(&Drone002Node::timer_callback, this));
    
    // 初始化无人机状态数据
    drone_state_.drone_name = "drone002";
    drone_state_.x = 0.0;
    drone_state_.y = 0.0;
    drone_state_.z = 0.0;
    
    RCLCPP_INFO(this->get_logger(), "drone002_node 节点已启动");
  }

private:
  /**
   * @brief 定时器回调函数
   * 
   * 每100ms被调用一次，更新无人机状态并发布消息
   * 模拟无人机的飞行状态
   */
  void timer_callback()
  {
    // 更新无人机位置（模拟圆周飞行，相位与drone001相反）
    double time_now = this->now().seconds();
    drone_state_.x = -5.0 * sin(time_now);
    drone_state_.y = -5.0 * cos(time_now);
    drone_state_.z = 2.0 + 0.5 * sin(time_now * 2.0);
    
    // 发布无人机状态消息
    publisher_->publish(drone_state_);
    
    RCLCPP_INFO(this->get_logger(), "发布无人机状态: 名称=%s, 位置(%.2f, %.2f, %.2f)",
      drone_state_.drone_name.c_str(), drone_state_.x, drone_state_.y, drone_state_.z);
  }

  rclcpp::TimerBase::SharedPtr timer_;  // 定时器
  rclcpp::Publisher<drone_msg_pkg::msg::DroneState>::SharedPtr publisher_;  // 消息发布者
  drone_msg_pkg::msg::DroneState drone_state_;  // 无人机状态消息
};

/**
 * @brief 主函数
 * 
 * 初始化 ROS2 客户端库，创建 drone002_node 节点并 spin
 */
int main(int argc, char * argv[])
{
  // 初始化 ROS2 客户端库
  rclcpp::init(argc, argv);
  
  // 创建 drone002_node 节点实例
  auto node = std::make_shared<Drone002Node>();
  
  // 开始处理回调（spin）
  rclcpp::spin(node);
  
  // 关闭 ROS2 客户端库
  rclcpp::shutdown();
  
  return 0;
}
