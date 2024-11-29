import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import cv2
from cv_bridge import CvBridge
import os
from datetime import datetime
from threading import Timer

class IRImageAutoSaver(Node):
    def __init__(self):
        super().__init__('ir_image_auto_saver')
        self.bridge = CvBridge()
        
        # 設定: 保存間隔（秒）
        self.save_interval = 5.0  # 5秒ごとに保存
        self.save_directory = "ir_images"  # 保存先ディレクトリ
        
        # 保存ディレクトリを作成
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)
            self.get_logger().info(f"Created directory: {self.save_directory}")

        # トピック購読
        self.subscription = self.create_subscription(
            Image,
            '/<camera_name>/ir/image_raw',  # IRカメラのトピック名に変更
            self.image_callback,
            10
        )

        # 最新画像データ
        self.latest_image = None
        self.get_logger().info('IR Image Auto Saver Node started.')

        # 自動保存の開始
        self.start_timer()

    def start_timer(self):
        """一定間隔で画像を保存するタイマーを設定"""
        Timer(self.save_interval, self.save_image).start()

    def image_callback(self, msg):
        """最新の画像を更新"""
        try:
            self.latest_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
        except Exception as e:
            self.get_logger().error(f"Failed to process image: {e}")

    def save_image(self):
        """最新の画像を保存"""
        if self.latest_image is not None:
            try:
                # タイムスタンプでファイル名を作成
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(self.save_directory, f'ir_image_{timestamp}.png')
                
                # 画像を保存
                cv2.imwrite(filename, self.latest_image)
                self.get_logger().info(f"Saved image: {filename}")
            except Exception as e:
                self.get_logger().error(f"Failed to save image: {e}")
        else:
            self.get_logger().warning("No image received yet.")

        # 次回のタイマーを設定
        self.start_timer()

def main(args=None):
    rclpy.init(args=args)
    node = IRImageAutoSaver()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
