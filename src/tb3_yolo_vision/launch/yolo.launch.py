from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='tb3_yolo_vision',
            executable='yolo_node',
            name='yolo_detector',
            output='screen'
        )
    ])