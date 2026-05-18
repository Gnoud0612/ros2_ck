import os
import re
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import EnvironmentVariable
from launch_ros.actions import Node

def generate_launch_description():
    # 1. Khai báo các đường dẫn
    package_name = 'agv_ros'
    pkg_share = get_package_share_directory(package_name)
    urdf_file = os.path.join(pkg_share, 'urdf', 'demo2.urdf')
    controller_file = os.path.join(pkg_share, 'config', 'arm_controllers.yaml')
    
    gazebo_pkg_dir = get_package_share_directory('gazebo_ros')
    turtlebot3_gazebo_dir = get_package_share_directory('turtlebot3_gazebo')
    turtlebot3_model_dir = os.path.join(turtlebot3_gazebo_dir, 'models')
    
    # TRỎ VÀO FILE HOUSE MAP CỦA BẠN
    # Đảm bảo bạn đã lưu file house_scan.world vào thư mục worlds của agv_ros
    world_path = os.path.join(pkg_share, 'worlds', 'house_scan.world')

    # 2. Xử lý URDF (Lấy logic từ gazebo_display để ổn định nhất)
    with open(urdf_file, 'r', encoding='utf-8', errors='ignore') as infp:
        robot_desc = infp.read()
    start_idx = robot_desc.find('<robot')
    if start_idx != -1:
        robot_desc = robot_desc[start_idx:]
    robot_desc = robot_desc.replace('__ARM_CONTROLLER_CONFIG__', controller_file)

    # 3. Biến môi trường
    set_gazebo_model_path = SetEnvironmentVariable(
        name='GAZEBO_MODEL_PATH',
        value=[os.path.dirname(pkg_share), os.pathsep, turtlebot3_model_dir, os.pathsep, EnvironmentVariable('GAZEBO_MODEL_PATH', default_value='')]
    )
    set_ros_domain_id = SetEnvironmentVariable(name='ROS_DOMAIN_ID', value='69')

    # 4. Các Node vận hành
    rsp_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc, 'use_sim_time': True}]
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(gazebo_pkg_dir, 'launch', 'gazebo.launch.py')),
        launch_arguments={'world': world_path}.items()
    )

    # Tọa độ spawn cho map House (0, 2.0 là vị trí trống ở sảnh)
    spawn_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', 'agv_ros', '-x', '0.0', '-y', '2.0', '-z', '0.06'],
        output='screen'
    )

    # Spawners cho Controller
    jsb_spawner = Node(package='controller_manager', executable='spawner', arguments=['joint_state_broadcaster'])
    load_jsb = RegisterEventHandler(OnProcessExit(target_action=spawn_node, on_exit=[jsb_spawner]))

    wheel_spawner = Node(
        package='controller_manager', executable='spawner', arguments=['wheel_velocity_controller', '--param-file', controller_file]
    )
    load_wheel = RegisterEventHandler(OnProcessExit(target_action=jsb_spawner, on_exit=[wheel_spawner]))

    # Khai báo đường dẫn đến file yaml
    gmapping_yaml = os.path.join(
        get_package_share_directory('slam_gmapping'), 
        'config', 
        'slam_gmapping.yaml'
    )

    # Node Gmapping SLAM
    node_gmapping = Node(
        package='slam_gmapping',
        executable='slam_gmapping_node',
        name='slam_gmapping',
        output='screen',
        parameters=[gmapping_yaml, {'use_sim_time': True}]
    )

    rviz_node = Node(package='rviz2', executable='rviz2', output='screen', parameters=[{'use_sim_time': True}])

    return LaunchDescription([
        set_gazebo_model_path,
        set_ros_domain_id,
        rsp_node,
        gazebo,
        spawn_node,
        load_jsb,
        load_wheel,
        node_gmapping,
        rviz_node
    ])
