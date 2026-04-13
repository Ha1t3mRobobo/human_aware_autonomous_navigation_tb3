#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, TwistStamped

class TwistToTwistStamped(Node):
    def __init__(self):
        super().__init__('twist_converter_node')

        # 1. On écoute le Twist standard (Nav2 ou Teleop)
        # Par défaut Nav2 publie sur /cmd_vel
        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel', 
            self.listener_callback,
            10)

        # 2. On publie le TwistStamped pour ros2_control
        # Attention: changez le nom du topic ci-dessous si votre controlleur est différent
        self.publisher = self.create_publisher(
            TwistStamped,
            '/diff_cont/cmd_vel', 
            10)

        self.declare_parameter('frame_id', 'base_footprint')
        self.frame_id = self.get_parameter('frame_id').value

        self.get_logger().info('Convertisseur Twist -> TwistStamped démarré !')

    def listener_callback(self, msg_twist):
        msg_stamped = TwistStamped()
        
        # On remplit les données
        msg_stamped.twist = msg_twist
        msg_stamped.header.stamp = self.get_clock().now().to_msg()
        msg_stamped.header.frame_id = self.frame_id
        
        self.publisher.publish(msg_stamped)

def main(args=None):
    rclpy.init(args=args)
    node = TwistToTwistStamped()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()