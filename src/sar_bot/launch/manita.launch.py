import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # 1. Chemin vers le fichier de configuration de la manette
    xbox_config_path = os.path.join(
        get_package_share_directory('sar_bot'),
        'config',
        'manita.yaml'
    )

    # 2. Le nœud Joy (lit le matériel /dev/input/jsX)
    joy_node = Node(
        package='joy',
        executable='joy_node',
        name='joy_node',
        output='screen'
    )

    # 3. Le nœud Teleop (convertit les boutons en TwistStamped)
    teleop_node = Node(
        package='teleop_twist_joy',
        executable='teleop_node',
        name='teleop_twist_joy_node',
        output='screen',
        parameters=[
            xbox_config_path, 
            {
                'publish_stamped_twist': True,  # Active la sortie TwistStamped
                'frame': 'base_footprint',           # Le frame_id pour le header
            }
        ],
        remappings=[
            # C'est ici que la magie opère :
            # On redirige la sortie standard '/cmd_vel' vers l'entrée de votre contrôleur
            ('/cmd_vel', '/diff_cont/cmd_vel')
        ]
    )

    return LaunchDescription([
        joy_node,
        teleop_node
    ])