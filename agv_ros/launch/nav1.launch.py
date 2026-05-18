import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import EnvironmentVariable
from launch_ros.actions import Node

def generate_launch_description():
    pkg_share = get_package_share_directory('agv_ros')
    urdf_file = os.path.join(pkg_share, 'urdf', 'demo2.urdf')
    controller_file = os.path.join(pkg_share, 'config', 'arm_controllers.yaml')
    
    gazebo_pkg_dir = get_package_share_directory('gazebo_ros')
    turtlebot3_gazebo_dir = get_package_share_directory('turtlebot3_gazebo')
    turtlebot3_model_dir = os.path.join(turtlebot3_gazebo_dir, 'models')
    default_world = os.path.join(turtlebot3_gazebo_dir, 'worlds', 'turtlebot3_world.world')

    # Bộ lọc đọc file cấu hình URDF
    with open(urdf_file, 'r', encoding='utf-8', errors='ignore') as infp:
        robot_desc = infp.read()
        
    start_idx = robot_desc.find('<robot')
    if start_idx != -1:
        robot_desc = robot_desc[start_idx:]
        
    robot_desc = robot_desc.replace('__ARM_CONTROLLER_CONFIG__', controller_file)

    set_gazebo_model_path = SetEnvironmentVariable(
        name='GAZEBO_MODEL_PATH',
        value=[os.path.dirname(pkg_share), os.pathsep, turtlebot3_model_dir, os.pathsep, EnvironmentVariable('GAZEBO_MODEL_PATH', default_value='')]
    )
    set_ros_domain_id = SetEnvironmentVariable('ROS_DOMAIN_ID', '69')

    # Node quản lý hệ tọa độ robot
    rsp_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{"robot_description": robot_desc, "use_sim_time": True}]
    )

    # Khởi chạy Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(gazebo_pkg_dir, 'launch', 'gazebo.launch.py')),
        launch_arguments={'world': default_world}.items()
    )

    # Sản sinh robot vào Gazebo
    spawn_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', 'agv_ros', '-x', '-2.0', '-y', '-0.5', '-z', '0.06'],
        output='screen'
    )

    # Khởi động các bộ điều khiển Controller
    jsb_spawner = Node(package='controller_manager', executable='spawner', arguments=['joint_state_broadcaster'])
    load_jsb = RegisterEventHandler(OnProcessExit(target_action=spawn_node, on_exit=[jsb_spawner]))

    wheel_velocity_controller_spawner = Node(
        package='controller_manager', executable='spawner', arguments=['wheel_velocity_controller', '--param-file', controller_file]
    )
    load_wheel_velocity_controller = RegisterEventHandler(OnProcessExit(target_action=jsb_spawner, on_exit=[wheel_velocity_controller_spawner]))

    # Cầu nối TF chuẩn xác: base_link (Cha) sinh ra base_footprint (Con)
    tf_footprint_to_link = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='footprint_to_link',
        arguments=[
            '--x', '0', '--y', '0', '--z', '0',
            '--yaw', '0', '--pitch', '0', '--roll', '0',
            '--frame-id', 'base_link',
            '--child-frame-id', 'base_footprint'
        ],
        parameters=[{'use_sim_time': True}]
    )

    # ==================== KHỐI NAV2 VÀ RVIZ ĐỘC LẬP ====================
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')
    
    # Khai báo ĐỦ 3 đường dẫn cốt lõi để Nav2 không bị crash báo lỗi chuỗi rỗng ''
    nav2_launch_file = os.path.join(nav2_bringup_dir, 'launch', 'bringup_launch.py')
    nav2_params_file = os.path.join(nav2_bringup_dir, 'params', 'nav2_params.yaml')
    nav2_rviz_config = os.path.join(nav2_bringup_dir, 'rviz', 'nav2_default_view.rviz')
    
    # Đường dẫn bản đồ
    map_path = '/home/duong2005/ros2_ws/map1_3.yaml' 

    # Node gọi Nav2
    nav2_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(nav2_launch_file),
        launch_arguments={
            'use_sim_time': 'True',
            'map': map_path,
            'params_file': nav2_params_file,
            'autostart': 'True'
        }.items()
    )

    # Node gọi RViz giao diện xịn của Nav2
    rviz_cmd = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', nav2_rviz_config],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    # Sự kiện kích hoạt: Ngay sau khi bánh xe khởi động xong, bật luôn Nav2 và RViz
    start_nav2_and_rviz = RegisterEventHandler(
        OnProcessExit(
            target_action=wheel_velocity_controller_spawner,
            on_exit=[nav2_cmd, rviz_cmd]
        )
    )

    return LaunchDescription([
        set_gazebo_model_path,
        set_ros_domain_id,
        rsp_node,
        gazebo,
        spawn_node,
        load_jsb,
        load_wheel_velocity_controller,
        tf_footprint_to_link,
        start_nav2_and_rviz   # Bắn lệnh gọi tự lái
    ])
