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

    # CÁCH LỌC URDF VÔ ĐỊCH: Bỏ qua mọi lỗi encoding và ký tự ẩn
    with open(urdf_file, 'r', encoding='utf-8', errors='ignore') as infp:
        robot_desc = infp.read()
        
    # Tìm chính xác vị trí bắt đầu của thẻ <robot và cắt bỏ mọi thứ trước đó
    start_idx = robot_desc.find('<robot')
    if start_idx != -1:
        robot_desc = robot_desc[start_idx:]
        
    # Cập nhật đường dẫn controller
    robot_desc = robot_desc.replace('__ARM_CONTROLLER_CONFIG__', controller_file)

    set_gazebo_model_path = SetEnvironmentVariable(
        name='GAZEBO_MODEL_PATH',
        value=[os.path.dirname(pkg_share), os.pathsep, turtlebot3_model_dir, os.pathsep, EnvironmentVariable('GAZEBO_MODEL_PATH', default_value='')]
    )
    set_ros_domain_id = SetEnvironmentVariable('ROS_DOMAIN_ID', '69')

    rsp_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc, 'use_sim_time': True}]
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(gazebo_pkg_dir, 'launch', 'gazebo.launch.py')),
        launch_arguments={'world': default_world}.items()
    )

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
        load_wheel_velocity_controller,
        node_gmapping,
        rviz_node
    ])
