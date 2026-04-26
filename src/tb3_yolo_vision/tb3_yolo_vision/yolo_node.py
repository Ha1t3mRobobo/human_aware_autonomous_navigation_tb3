import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage
from std_msgs.msg import String  # <-- AJOUT pour envoyer les infos au 2eme fichier
from cv_bridge import CvBridge
from ultralytics import YOLO
import cv2
import os
import numpy as np
import json # <-- AJOUT pour formater les données
from ament_index_python.packages import get_package_share_directory
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

class YoloDetector(Node):
    def __init__(self):
        super().__init__('yolo_detector')
        self.bridge = CvBridge()
        
        # Load Model
        pkg_path = get_package_share_directory('tb3_yolo_vision')
        model_path = os.path.join(pkg_path, 'weights', 'best_100_violence.pt')
        self.model = YOLO(model_path)
        
        # --- AJOUT : Publisher pour envoyer les infos au 2ème fichier ---
        self.detection_pub = self.create_publisher(String, '/yolo/detections', 10)

        # --- CONFIGURATION ---
        self.target_thresholds = {
            'Person': 0.50,
            'NonViolence': 0.50,
            'Violence': 0.60
        }
        
        self.person_id = None
        for class_id, class_name in self.model.names.items():
            if class_name == 'Person':
                self.person_id = class_id
                break

        self.valid_class_ids = {}
        for class_id, class_name in self.model.names.items():
            if class_name in self.target_thresholds:
                self.valid_class_ids[class_id] = self.target_thresholds[class_name]
        
        self.get_logger().info(f"Filtre : Person/NonViolence (50%), Violence (60%)")

        custom_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        self.subscription = self.create_subscription(
            CompressedImage,
            '/image_raw/compressed', 
            self.image_callback,
            qos_profile=custom_qos)

    def image_callback(self, msg):
        try:
            np_arr = np.frombuffer(msg.data, np.uint8)
            cv_image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if cv_image is not None:
                image_width = cv_image.shape[1] # Largeur de l'image
                
                results = self.model(cv_image, verbose=False, conf=0.5, imgsz=320)
                boxes = results[0].boxes
                keep_indices = []
                
                # Liste pour stocker les infos à envoyer au 2eme fichier
                detections_to_send = [] 

                for i, box in enumerate(boxes):
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    
                    if cls_id in self.valid_class_ids:
                        threshold = self.valid_class_ids[cls_id]
                        
                        if conf >= threshold:
                            if self.model.names[cls_id] == 'NonViolence' and self.person_id is not None:
                                results[0].boxes.cls[i] = float(self.person_id)
                            
                            keep_indices.append(i)

                            # --- AJOUT : Préparer les données pour le Fichier 2 ---
                            x_center = float(box.xywh[0][0])
                            bbox_height = float(box.xywh[0][3])
                            class_name = self.model.names[cls_id]
                            
                            det_info = {
                                'class_name': class_name,
                                'x_center': x_center,
                                'bbox_height': bbox_height,
                                'image_width': image_width
                            }
                            detections_to_send.append(det_info)

                # --- AJOUT : Envoyer les données si on a détecté quelqu'un ---
                if len(detections_to_send) > 0:
                    msg_pub = String()
                    msg_pub.data = json.dumps(detections_to_send)
                    self.detection_pub.publish(msg_pub)

                results[0].boxes = boxes[keep_indices]
                annotated_frame = results[0].plot()

                cv2.imshow("YOLO Filtered & Merged", annotated_frame)
                cv2.waitKey(1)
                
        except Exception as e:
            self.get_logger().error(f'Error: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = YoloDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
