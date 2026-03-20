cmake_minimum_required(VERSION 3.8)
project(drone_msg_pkg)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# 查找必要的 ROS2 包
find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

# 生成自定义消息接口
# 注意: 这个函数会自动生成 DroneState 消息的 C++ 代码
# 生成的目标包括:
#   - drone_msg_pkg__rosidl_generator_cpp: 消息生成器
#   - drone_msg_pkg__rosidl_typesupport_cpp: 类型支持
#   - drone_msg_pkg__rosidl_generator_c: C 接口
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/DroneState.msg"
)

# 安装消息文件
install(DIRECTORY msg/
  DESTINATION share/${PROJECT_NAME}/msg
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
