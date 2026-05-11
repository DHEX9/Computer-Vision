import cv2
import mediapipe as mp
import requests
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time
from gestos import gestos

# Variaveis para checar ultimo comando e tempo do ultimo comando
last_print_action = ""
last_send = 0
last_unknown = False
last_no_hand = False
last_connection_error = False

ESP32_IP = "192.168.0.135"  # ← IP do esp

base_options = python.BaseOptions(
    model_asset_path="utils/hand_landmarker.task"
)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_hands=1,                        
    min_hand_detection_confidence=0.5,  # confiança mínima pra detectar
    min_tracking_confidence=0.3         # confiança mínima pra rastrear
)

webcam = cv2.VideoCapture(0) # Abre a webcam. 0 = câmera padrão do sistema
webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

with vision.HandLandmarker.create_from_options(options) as landmarker:
    while webcam.isOpened():

        action = None

        ret, frame = webcam.read() # ret → booleano: True se o frame foi capturado com sucesso,  frame → a imagem em si (ndarray NumPy de shape (altura, largura, 3))

        if not ret:
            print("Captura não encontrada")
            break
        
        frame = cv2.flip(frame, 1)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        timestamp = int(time.time() * 1000)

        resultado = landmarker.detect_for_video(mp_image, timestamp)

        if resultado.hand_landmarks:

            last_no_hand = False

            for i, hand in enumerate(resultado.hand_landmarks):

                lado = resultado.handedness[i][0].category_name
                g = gestos(hand, lado)

                # DESENHA landmarks
                for landmark in hand:
                    h, w, _ = frame.shape
                    cx, cy = int(landmark.x * w), int(landmark.y * h)
                    cv2.circle(frame, (cx, cy), 10, (0, 255, 0), -1)

                # DETECTA gesto (FORA do loop dos landmarks) (estava checando 21 vezes por frame o que crashava o programa)
                if g.frente():
                    action = "frente"
                    last_unknown = False

                elif g.parado():
                    action = "parar"
                    last_unknown = False

                elif g.re():
                    action = "re"
                    last_unknown = False

                elif g.direita():
                    action = "direita"
                    last_unknown = False

                elif g.esquerda():
                    action = "esquerda"
                    last_unknown = False

                else:

                    if not last_unknown:
                        print("Gesto não reconhecido")
                        last_unknown = True

                #printa não repetidamente cada comando
                if action != last_print_action and action is not None:
                    last_print_action = action
                    print(action)

                #checa ultimo action e tempo do ultimo comando para não sobrecarregar
                if action is not None:
                     if time.time() - last_send > 0.1:

                        try:
                            requests.get(f"http://{ESP32_IP}/cmd?action={action}", timeout=0.1)
                            last_send = time.time()
                            last_connection_error = False
                        except requests.exceptions.RequestException as e:
                            if not last_connection_error:
                                print(f"Erro ao enviar: {e}")
                                last_connection_error = True
        
        #printa não repetidamente se mao não for encontrada
        else:

            if not last_no_hand:
                print("Mão não detectada")
                last_no_hand = True
        
        #bloco abaixo movido para esquerda para não crashar quando não há mao detectada
        cv2.imshow("Feed", frame) # Exibe o frame numa janela chamada "Feed", Se a janela não existir, cria automaticamente
        cv2.waitKey(1) # Processa eventos

        if cv2.getWindowProperty("Feed", cv2.WND_PROP_VISIBLE) < 1:
            break

webcam.release() # Libera a câmera para outros programas poderem usá-la
cv2.destroyAllWindows() # Fecha todas as janelas abertas pelo OpenCV
