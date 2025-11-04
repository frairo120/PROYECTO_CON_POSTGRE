import cv2
import numpy as np
import os
import time
from ultralytics import YOLO

class DroidCamera:
    def __init__(self, model_path=None, ip_address="192.168.1.100", port="4747"):
        self.video = None
        self.is_running = False
        self.ip_address = ip_address
        self.port = port
        self.out = None
        self.is_recording = False
        self.last_detection_time = None
        self.no_detection_threshold = 5  # segundos sin detección antes de detener la grabación
        self.current_recording_filename = None
        self.last_alert_time = None

        # Ruta absoluta al modelo
        # NOTA: Asegúrate de que esta ruta sea correcta en tu sistema.
        model_path = r'C:\Users\jonat\Desktop\modelo_entrenado\sistema\models2\Models\best.pt'

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Error loading model: {model_path} not found")

        try:
            print(f"Attempting to load YOLOv8 model from: {model_path}")
            self.model = YOLO(model_path)
            print("YOLOv8 model loaded successfully")

            self.model.conf = 0.25
            self.model.iou = 0.45
            self.model.classes = None
            
            print("Model successfully loaded")
            print(f"Detectable classes: {self.model.names}")
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            raise

    def __del__(self):
        if self.video:
            self.video.release()
        if self.out:
            self.out.release()

    def start_recording(self, frame):
        if not self.is_recording:
            os.makedirs('grabaciones', exist_ok=True)
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f'grabaciones/recording_{timestamp}.avi'
            self.current_recording_filename = filename
            height, width = frame.shape[:2]
            fourcc = cv2.VideoWriter_fourcc(*'MJPG') 
            self.out = cv2.VideoWriter(filename, fourcc, 20.0, (width, height))
            self.is_recording = True
            print(f"Starting recording: {filename}")

    def stop_recording(self):
        if self.is_recording:
            self.out.release()
            self.out = None
            self.is_recording = False
            print("Recording stopped")

    def start(self):
        if not self.is_running:
            try:
                # 1. Si por alguna razón self.video no se liberó correctamente, lo liberamos aquí
                if self.video:
                    self.video.release()
                    self.video = None

                droidcam_url = f"http://{self.ip_address}:{self.port}/video"
                print(f"Attempting to connect to DroidCam at: {droidcam_url}")
                
                # 2. Intentar crear el nuevo objeto VideoCapture
                self.video = cv2.VideoCapture(droidcam_url) 

                if not self.video.isOpened():
                    print("Error: Could not connect to DroidCam. Please check the IP/Port or DroidCam app.")
                    # Si falla la apertura, liberamos y limpiamos
                    self.video.release()
                    self.video = None
                    return

                ret, frame = self.video.read()
                if not ret:
                    print("Error: Could not read first frame from DroidCam.")
                    self.video.release()
                    self.video = None
                    return

                print("DroidCam initialized successfully")
                self.is_running = True

            except Exception as e:
                print(f"Error starting DroidCam: {str(e)}")
                self.is_running = False
                if self.video:
                    self.video.release()
                    self.video = None

    def stop(self):
        if self.is_running:
            # 1. Asegurar la liberación del recurso de video
            if self.video:
                self.video.release()
                self.video = None # Importante: restablecer a None para que start() sepa que debe crear uno nuevo
            
            # 2. Detener la grabación si está activa
            self.stop_recording() 
            
            self.is_running = False
            print("DroidCam successfully stopped and resources released.")

    def get_frame(self):
        if not self.is_running or self.video is None or not self.video.isOpened():
            return None

        try:
            success, image = self.video.read()
            if not success:
                return None
            
            original_image = image.copy() 

            # 🔹 YOLOv8 Prediction
            results = self.model.predict(image, conf=0.25, verbose=False)

            if results and len(results) > 0:
                result = results[0]
                num_detections = len(result.boxes)
                
                # Get detected class names (e.g., 'helmet', 'vest')
                detected_classes = [self.model.names[int(cls)] for cls in result.boxes.cls]

                # 🔹 Required PPE (Key: YOLO Class Name, Value: Spanish Label for display)
                required_items = {
                    "helmet": "Casco",
                    "vest": "Chaleco",
                    "boots": "Botas"
                }

                alert_message = None
                epp_status = {}
                
                # ❗ CORRECCIÓN CLAVE: Usar 'human' en lugar de 'person'
                has_person = "human" in detected_classes 

                # ⚙️ PPE Detection and Status Logic
                for item_class, item_label in required_items.items():
                    if has_person:
                        # Check if the PPE is worn
                        if item_class in detected_classes:
                            # PPE found and person present
                            epp_status[item_label] = True
                        else:
                            # PPE missing and person present
                            epp_status[item_label] = False
                            
                            # Generate alert message only for the first missing item
                            if alert_message is None: 
                                alert_message = f"⚠️ ALARM: Person missing {item_label.upper()}"
                            
                            # ⚠️ Alert Logging Logic (Django/DB)
                            try:
                                # Handling optional Django imports
                                from django.utils import timezone 
                                from .models import Alert
                                now = time.time()
                                if not self.last_alert_time or (now - self.last_alert_time) > 10:
                                    video = self.current_recording_filename or ''
                                    Alert.objects.create(
                                        message=f"Person missing {item_label}",
                                        missing=item_class,
                                        level='high',
                                        video=video,
                                    )
                                    self.last_alert_time = now
                            except (ImportError, NameError):
                                pass 
                            except Exception as e:
                                print(f"Could not save alert to DB: {e}")
                    else:
                        # No person detected, status is 'Not Applicable'
                        epp_status[item_label] = None 


                # 🔹 Update time and start/continue recording
                if num_detections > 0:
                    self.last_detection_time = time.time()
                    self.start_recording(image)
                    if self.is_recording:
                        self.out.write(image)

                # 🔹 Draw bounding boxes and labels
                annotated_frame = result.plot()

                # 🎨 DISPLAY PPE STATUS (Using English/Universal Status Labels)
                y_offset = 40
                
                # Iterate over the Spanish names (values) which are the keys in epp_status
                for item_label in required_items.values():
                    current_status = epp_status.get(item_label, None)
                    
                    if current_status is True:
                        color = (0, 255, 0)  # Green for OK
                        estado = "OK"
                    elif current_status is False:
                        color = (0, 0, 255)  # Red for MISSING
                        estado = "MISSING" 
                    else:
                        color = (255, 255, 0) # Yellow for N/A
                        estado = "N/A"
                    
                    cv2.putText(
                        annotated_frame,
                        f"{item_label}: {estado}",
                        (10, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        color,
                        2
                    )
                    y_offset += 35

                # 🔹 Display number of detections and alerts
                cv2.putText(annotated_frame, f"Detections: {num_detections}", (10, y_offset),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                y_offset += 30

                if alert_message:
                    cv2.putText(annotated_frame, alert_message, (10, y_offset),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    y_offset += 40

                if self.is_recording:
                    # Display REC status in English
                    cv2.putText(annotated_frame, "REC", (10, y_offset), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                ret, jpeg = cv2.imencode('.jpg', annotated_frame)
                return jpeg.tobytes()

            else:
                # If no detections
                if self.is_recording and self.last_detection_time:
                    current_time = time.time()
                    if current_time - self.last_detection_time > self.no_detection_threshold:
                        self.stop_recording()

                if self.is_recording:
                    self.out.write(original_image)
                
                # Display no-detection status
                cv2.putText(original_image, "Detections: 0", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(original_image, "No relevant objects detected", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

                ret, jpeg = cv2.imencode('.jpg', original_image)
                return jpeg.tobytes()

        except Exception as e:
            print(f"Error processing frame: {str(e)}")
            if 'original_image' in locals():
                ret, jpeg = cv2.imencode('.jpg', original_image)
                return jpeg.tobytes()
            return None


# 🧠 Main Usage Example
if __name__ == "__main__":
    # Ensure you use the correct DroidCam IP and Port
    camera = DroidCamera(ip_address="192.168.0.100", port="4747") 
    try:
        camera.start()
        cv2.namedWindow("DroidCam PPE Detection", cv2.WINDOW_NORMAL)
        while True:
            frame_data = camera.get_frame()
            if frame_data is None:
                print("Could not get frame. Retrying...")
                time.sleep(1)
                continue
            nparr = np.frombuffer(frame_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            cv2.imshow("DroidCam PPE Detection", frame)
            # Press 'q' to exit
            if cv2.waitKey(1) & 0xFF == ord('q'): 
                break
    except KeyboardInterrupt:
        print("Stopping application due to keyboard interruption...")
    finally:
        camera.stop()
        cv2.destroyAllWindows()