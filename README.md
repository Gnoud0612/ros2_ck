#  Dự án ROS 2: Xe AGV Mecanum - SLAM & Navigation 2

Dự án mô phỏng xe tự hành AGV sử dụng cơ cấu bánh Mecanum trên ROS 2 Humble và Gazebo. Bao gồm hai chức năng chính: Quét bản đồ (Gmapping) và Điều hướng tự động (Nav2).

---

##  1. Cài đặt và Biên dịch ban đầu
Tải thư mục agv_ros và slam_gmapping_Humble rồi đưa vào src: ros2_ws/src

Mỗi khi mở một Terminal mới, hoặc sau khi chỉnh sửa code, cần chạy các lệnh sau để nạp môi trường và biên dịch gói:

```bash
# Di chuyển vào thư mục workspace
cd ~/ros2_ws

# Biên dịch gói agv_ros
colcon build --packages-select agv_ros

# Nạp môi trường ROS 2
source install/setup.bash

# [Quan Trọng] Cấu hình Domain ID để các Node kết nối được với nhau
export ROS_DOMAIN_ID=69
##  2. Xây dựng bản đồ
# map1
ros2 launch agv_ros gmapping_launch.py
# map2
ros2 launch agv_ros gmapping_launch2.py
# Lệnh điều khiển
ros2 run agv_ros mecanum_keyboard_teleop.py
## 3. Thực hiện navigation
# ap1
ros2 launch agv_ros nav1.launch.py
# map2
ros2 launch agv_ros nav2_house.launch.py
