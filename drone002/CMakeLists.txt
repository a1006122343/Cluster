cmake_minimum_required(VERSION 3.8)
project(drone002)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# 查找必要的 ROS2 包
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(drone_msg_pkg REQUIRED)

# 创建 drone002_node 可执行文件
add_executable(drone002_node src/drone002_node.cpp)

# 链接依赖库
ament_target_dependencies(drone002_node
  rclcpp
  drone_msg_pkg
)

# 安装可执行文件
install(TARGETS
  drone002_node
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
