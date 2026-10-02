from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # 1. Boot the RPLiDAR A1
        Node(
            package='rplidar_ros',
            executable='rplidar_composition',
            name='rplidar_node',
            parameters=[{
                'serial_port': '/dev/ttyUSB1', # Assuming LiDAR is on USB1, ESP32 on USB0
                'frame_id': 'laser_frame',
                'angle_compensate': True,
                'scan_mode': 'Standard'
            }],
            output='screen'
        ),
        
        # 2. Boot the Custom Odometry-to-ESP32 Bridge
        Node(
            package='living_map_core',
            executable='odom_bridge',
            name='odom_bridge_node',
            output='screen'
        )
    ])