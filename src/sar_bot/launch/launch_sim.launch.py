import os
from ament_index_python.packages import get_package_share_directory


from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():

    package_name = 'sar_bot' 

    world_path = os.path.join(
        get_package_share_directory(package_name),
        'worlds',
        'demoworld.sdf'
    )

    # Include your robot_state_publisher launch
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory(package_name),
                'launch',
                'rsp.launch.py'
            )
        ),
        launch_arguments={'use_sim_time': 'true'}.items()
    )

    # Launch Gazebo Sim 
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py'
            )
        ),
        launch_arguments={
            # -r: starts the simulation unpaused
            # -v 4: sets the verbose level to 4 for debugging
            'gz_args': f'-r -v 4 "{world_path}"'
        }.items()
    )
    # Spawn robot 
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'my_bot',
            '-topic', 'robot_description',
            '-x', '1.0',
            '-y', '0.0',
            '-z', '0.2',
        ],
        output='screen'
    )
    bridge_params = os.path.join(
        get_package_share_directory(package_name),
        'config',
        'gz_bridge.yaml'
    )

    # ros_gz_bridge
    gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{'config_file': bridge_params}],
        output='screen'
        )

    # Spawn joint state broadcaster
    load_joint_state_broadcaster = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_broad"],
        output="screen",
    )

    # Spawn diff drive controller
    load_diff_drive_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["diff_cont"],
        output="screen",
    )
    


    #noeud de converstion Twist vers TwistStamped de Nav2 
    convertisseur = Node(
        package='sar_bot',
        executable='twist_to_twistStamped.py',  
        name='conv_twist_TwistStamped',
        output='screen'
    ) 

    return LaunchDescription([
        rsp,
        gazebo_launch,
        spawn_entity,
        gz_bridge,
        load_diff_drive_controller,
        load_joint_state_broadcaster,
        convertisseur,
    ])