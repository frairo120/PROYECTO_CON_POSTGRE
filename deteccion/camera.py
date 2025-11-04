import cv2
import numpy as np
import os
from ultralytics import YOLO

class VideoCamera:
    def __init__(self, model_path=None):
        self.video = None
        self.is_running = False
        self.out = None
        self.is_recording = False
        self.last_detection_time = None
        self.no_detection_threshold = 5  # segundos sin detección antes de detener la grabación
        self.current_recording_filename = None
        self.last_alert_time = None
        
        # Ruta absoluta al modelo
        model_path = r'C:\Users\jonat\Desktop\modelo_entrenado\sistema\epp\Models\best.pt'
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"No se encontró el modelo en: {model_path}")
            
        try:
            print(f"Intentando cargar modelo YOLOv8 desde: {model_path}")
            self.model = YOLO(model_path)  # Carga el modelo YOLOv8
            print("Modelo YOLOv8 cargado exitosamente")
            
            # Configuramos el modelo para inferencia
            self.model.conf = 0.25  # Umbral de confianza
            self.model.iou = 0.45   # Umbral IoU
            self.model.classes = None  # Detectar todas las clases
            self.model.eval()  # Modo evaluación
            
            print("Modelo cargado exitosamente")
            print(f"Clases detectables: {self.model.names}")
        except Exception as e:
            print(f"Error al cargar el modelo: {str(e)}")
            raise
    def __del__(self):
        if self.video:
            self.video.release()
        if self.out:
            self.out.release()
            
    def start_recording(self, frame):
        if not self.is_recording:
            # Crear directorio de grabaciones si no existe
            os.makedirs('grabaciones', exist_ok=True)
            
            # Generar nombre de archivo con timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'grabaciones/recording_{timestamp}.avi'
            # Guardar filename para enlazar en alertas
            self.current_recording_filename = filename
            
            # Obtener dimensiones del frame
            height, width = frame.shape[:2]
            
            # Inicializar el escritor de video
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self.out = cv2.VideoWriter(filename, fourcc, 20.0, (width, height))
            self.is_recording = True
            print(f"Iniciando grabación: {filename}")
            
    def stop_recording(self):
        if self.is_recording:
            self.out.release()
            self.out = None
            self.is_recording = False
            print("Grabación detenida")
    
    def start(self):
        if not self.is_running:
            # Intentar diferentes índices de cámara
            camera_indices = [0, 1, -1]  # Probar índice 0, 1 y el default
            
            for idx in camera_indices:
                print(f"Intentando abrir cámara con índice {idx}")
                self.video = cv2.VideoCapture(idx)
                
                if self.video is None:
                    print(f"Error: No se pudo crear el objeto VideoCapture para índice {idx}")
                    continue
                
                if not self.video.isOpened():
                    print(f"Error: No se pudo abrir la cámara con índice {idx}")
                    self.video.release()
                    continue
                
                # Verificar si podemos leer un frame
                ret, frame = self.video.read()
                if not ret:
                    print(f"Error: No se pudo leer frame de la cámara con índice {idx}")
                    self.video.release()
                    continue
                
                print(f"Cámara inicializada exitosamente con índice {idx}")
                self.is_running = True
                return
            
            # Si llegamos aquí, no se pudo inicializar ninguna cámara
            print("Error: No se pudo inicializar ninguna cámara disponible")
            self.is_running = False
    
    def stop(self):
        if self.is_running:
            self.video.release()
            self.video = None
            self.is_running = False
    
    def get_frame(self):
        if not self.is_running:
            print("Error: La cámara no está iniciada")
            return None
            
        if self.video is None:
            print("Error: Objeto de video no inicializado")
            return None
            
        if not self.video.isOpened():
            print("Error: La cámara está cerrada")
            self.is_running = False
            return None
            
        try:
            success, image = self.video.read()
            if not success:
                print("Error al leer frame de la cámara. Verificando estado:")
                print(f"- Is Opened: {self.video.isOpened()}")
                print(f"- Frame Width: {self.video.get(cv2.CAP_PROP_FRAME_WIDTH)}")
                print(f"- Frame Height: {self.video.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
                print(f"- FPS: {self.video.get(cv2.CAP_PROP_FPS)}")
                return None
            
            # Realizar predicción con YOLOv8
            results = self.model.predict(image, conf=0.25, show=False)
            
            # Obtener el primer resultado
            if results and len(results) > 0:
                result = results[0]
                num_detections = len(result.boxes)
                
                # Si hay detecciones de personas
                if num_detections > 0:
                    # Actualizar tiempo de última detección
                    import time
                    self.last_detection_time = time.time()
                    
                    # Iniciar grabación si no está grabando
                    self.start_recording(image)
                    
                    # Grabar el frame si está grabando
                    if self.is_recording:
                        self.out.write(image)
                
                # Dibujar las detecciones en la imagen
                annotated_frame = result.plot()
                # Detectar clases y guardar alertas si falta algún elemento
                try:
                    detected_classes = [self.model.names[int(cls)] for cls in result.boxes.cls]
                    required_items = ["person", "helmet", "vest", "boots"]
                    if "person" in detected_classes:
                        missing = [item for item in required_items[1:] if item not in detected_classes]
                        import time
                        now = time.time()
                        if missing:
                            # Crear alerta en DB (si está disponible)
                            try:
                                from .models import Alert
                                if not self.last_alert_time or (now - self.last_alert_time) > 10:
                                    Alert.objects.create(
                                        message=f"Persona sin {', '.join(missing)}",
                                        missing=', '.join(missing),
                                        level='high',
                                        video=self.current_recording_filename or ''
                                    )
                                    self.last_alert_time = now
                            except Exception as e:
                                print(f"No se pudo guardar alerta: {e}")
                        else:
                            # Todos los elementos presentes: alerta positiva (opcional)
                            try:
                                from .models import Alert
                                if not self.last_alert_time or (now - self.last_alert_time) > 10:
                                    Alert.objects.create(
                                        message="Persona con EPP completo",
                                        missing='',
                                        level='positive',
                                        video=self.current_recording_filename or ''
                                    )
                                    self.last_alert_time = now
                            except Exception as e:
                                print(f"No se pudo guardar alerta positiva: {e}")
                except Exception:
                    pass
                
                # Añadir contador de detecciones y estado de grabación
                cv2.putText(annotated_frame, f"Detecciones: {num_detections}", (10, 30),
                          cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                if self.is_recording:
                    cv2.putText(annotated_frame, "REC", (10, 70),
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                
                # Convertir a JPEG
                ret, jpeg = cv2.imencode('.jpg', annotated_frame)
                if not ret:
                    print("Error al codificar imagen a JPEG")
                    return None
                
                return jpeg.tobytes()
            else:
                # Si no hay detecciones, verificar si debemos detener la grabación
                if self.is_recording and self.last_detection_time:
                    import time
                    current_time = time.time()
                    if current_time - self.last_detection_time > self.no_detection_threshold:
                        self.stop_recording()
                
                # Si está grabando, grabar el frame aunque no haya detecciones
                if self.is_recording:
                    self.out.write(image)
                
                # Mostrar el frame original
                if self.is_recording:
                    cv2.putText(image, "REC", (10, 70),
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                ret, jpeg = cv2.imencode('.jpg', image)
                return jpeg.tobytes()
            
        except Exception as e:
            print(f"Error al procesar el frame: {str(e)}")
            if 'image' in locals():
                # Si hay error pero tenemos la imagen, al menos mostramos la imagen sin procesar
                ret, jpeg = cv2.imencode('.jpg', image)
                return jpeg.tobytes()
            return None