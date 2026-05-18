cmake_minimum_required(VERSION 3.5)
project(agv_ros)

# Chuẩn C/C++
if(NOT CMAKE_C_STANDARD)
  set(CMAKE_C_STANDARD 99)
endif()

if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()

# Tìm ament
find_package(ament_cmake REQUIRED)

# (Optional) env hook nếu bạn đang dùng FastDDS
ament_environment_hooks(
  "${CMAKE_CURRENT_SOURCE_DIR}/env-hooks/fastdds_udp.sh.in"
)

# Install các thư mục tài nguyên
install(
  DIRECTORY
    config
    launch
    meshes
    Rviz
    urdf
    worlds
    scripts
  DESTINATION share/${PROJECT_NAME}
)

# Install Python scripts (để dùng với ros2 run)
install(
  PROGRAMS
    scripts/arm_teleop.py
    scripts/joint_state_gui_bridge.py
    scripts/mecanum_keyboard_teleop.py
    scripts/mecanum_drive_controller.py
  DESTINATION lib/${PROJECT_NAME}
)

# BẮT BUỘC
ament_package()
