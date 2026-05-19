# Đồ án ROS 2: Mô phỏng AGV Mecanum - SLAM & Navigation 2

Dự án này triển khai hệ thống xe tự hành (AGV) sử dụng cơ cấu 4 bánh Mecanum đa hướng trong môi trường mô phỏng Gazebo. Dự án được xây dựng trên nền tảng **ROS 2 Humble** (Ubuntu 22.04), bao gồm việc tích hợp bộ điều khiển ROS 2 Control, xây dựng bản đồ bằng thuật toán SLAM Gmapping và điều hướng tự động bằng Navigation 2 (Nav2).

---

## 1. Yêu cầu hệ thống & Cài đặt thư viện

Trước khi chạy dự án, bạn cần đảm bảo đã cài đặt ROS 2 Humble. Sau đó, mở Terminal và chạy lệnh sau để cài đặt các thư viện (packages) phụ thuộc cần thiết:

```bash
sudo apt update
sudo apt install -y \
  ros-humble-gazebo-ros-pkgs \
  ros-humble-ros2-control \
  ros-humble-ros2-controllers \
  ros-humble-gazebo-ros2-control \
  ros-humble-navigation2 \
  ros-humble-nav2-bringup \
  ros-humble-teleop-twist-keyboard \
  ros-humble-xacro
```
Lưu ý: Thuật toán Gmapping không hỗ trợ cài đặt trực tiếp qua apt trên ROS 2 Humble. Do đó, mã nguồn của openslam_gmapping và slam_gmapping đã được tích hợp sẵn trong thư mục src của dự án này để biên dịch trực tiếp.
## 2. Biên dịch Workspace (Build)
Mở Terminal và thực hiện các lệnh sau để tải và biên dịch dự án:
```bash
# 1. Di chuyển vào thư mục workspace
cd ~/ros2_ws

# 2. Biên dịch toàn bộ các gói trong src
colcon build

# 3. Nạp môi trường hệ thống
source install/setup.bash

# 4. Cấp quyền thực thi cho file điều khiển bằng bàn phím
chmod +x ~/ros2_ws/src/agv_ros/scripts/mecanum_keyboard_teleop.py
```
QUAN TRỌNG: Dự án này sử dụng tần số giao tiếp riêng biệt để tránh nhiễu tín hiệu. Mỗi khi mở một Terminal mới, bạn bắt buộc phải chạy lệnh cấu hình Domain ID:
```bash
export ROS_DOMAIN_ID=69
```
## 3. Chạy SLAM (Xây dựng bản đồ với Gmapping)
Để xe di chuyển và quét bản đồ môi trường, bạn cần mở 2 Terminal song song:
Terminal 1: Khởi động mô phỏng và Gmapping
```bash
cd ~/ros2_ws
source install/setup.bash
export ROS_DOMAIN_ID=69
ros2 launch agv_ros gmapping_launch.py
```
Terminal 2: Bật điều khiển bằng bàn phím (Teleop)
```bash
cd ~/ros2_ws
source install/setup.bash
export ROS_DOMAIN_ID=69
ros2 run agv_ros mecanum_keyboard_teleop.py
```
Sử dụng các phím (u, i, o, j, k, l, m, , , .) trên Terminal 2 để lái xe đa hướng quanh mô hình 3D cho đến khi bản đồ trên RViz được hoàn thiện.
Terminal 3: Lưu bản đồ (Map Saver)
Sau khi đã quét xong, giữ nguyên các Terminal đang chạy. Mở Terminal thứ 3 để lưu bản đồ thành file .yaml và .pgm:
```bash
cd ~/ros2_ws
source install/setup.bash
export ROS_DOMAIN_ID=69
# Cú pháp: ros2 run nav2_map_server map_saver_cli -f <đường_dẫn_lưu_map/tên_map>
ros2 run nav2_map_server map_saver_cli -f ~/ros2_ws/map_hoan_thien
```
## 4. Chạy Navigation 2 (Điều hướng tự động)
Dự án đã được cấu hình file Launch "All-in-one", khởi động đồng loạt Gazebo, RViz, nạp bản đồ tĩnh và kích hoạt hệ thống tự lái chỉ bằng 1 lệnh duy nhất.
Mở 1 Terminal mới:
```bash
cd ~/ros2_ws
source install/setup.bash
export ROS_DOMAIN_ID=69
```
Test trên sa bàn lục giác (Map 1): 
```bash
ros2 launch agv_ros nav1.launch.py
```
Test trên sa bàn ngôi nhà chữ T (Map 2):
```bash
ros2 launch agv_ros nav2_house.launch.py
```
