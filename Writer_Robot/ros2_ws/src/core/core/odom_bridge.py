import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
import serial
import time

class OdomBridgeNode(Node):
    def __init__(self):
        super().__init__('odom_bridge')
        self.subscription = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10)
        
        # Connect to the ESP32 Hardware Actuator
        try:
            self.esp32 = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
            self.get_logger().info('Connected to ESP32 on /dev/ttyUSB0')
        except serial.SerialException:
            self.get_logger().error('ESP32 not found. Check USB connection.')
            self.esp32 = None
            
        self.last_update = time.time()

    def odom_callback(self, msg):
        # Throttle updates to 5Hz to prevent flooding the ESP32 serial buffer
        if time.time() - self.last_update < 0.2:
            return
            
        # Extract X and Y from ROS2 Odometry (meters) and convert to centimeters
        x_cm = int(msg.pose.pose.position.x * 100)
        y_cm = int(msg.pose.pose.position.y * 100)
        
        if self.esp32:
            # Send formatted coordinate string to ESP32 (e.g., UPDATE_POSE,150,-320)
            pose_cmd = f"UPDATE_POSE,{x_cm},{y_cm}\n"
            self.esp32.write(pose_cmd.encode('utf-8'))
            
        self.last_update = time.time()

def main(args=None):
    rclpy.init(args=args)
    odom_bridge = OdomBridgeNode()
    rclpy.spin(odom_bridge)
    odom_bridge.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()