# Projeto ERUS — Carro Controlado por Gestos

Controle de um carro físico via gestos da mão, usando visão computacional em tempo real.

---

## Visão Geral

O projeto captura o vídeo da webcam, detecta a mão do usuário com MediaPipe, interpreta gestos e envia comandos via porta serial para o microcontrolador do carro.

Apenas a parte de Computer Vision disponibilizada nesse repositório, contribuído por Daniel Rodrigues, para projeto completo do grupo, procure o repositório "fusca-azul".

---

## Stack

|     Componente      |     Tecnologia     |
|---------------------|--------------------|
|     Linguagem       | Python 3.12        |
| Visão computacional | OpenCV + Mediapipe |
| Detecção de mãos    | MediaPipe 0.10.35  |
| Comunicação         |       Wi-fi        |
| Microcontrolador    |       ESP32        |

---

## Estrutura do Projeto

```
Projeto ERUS/
├── main.py          # câmera, mediapipe, loop principal
├── gestos.py        # classe de gestos (mão aberta, fechada, etc.)
├── dedos.py         # funções de detecção por dedo
├── carro.py         # lógica de controle e comunicação serial
└── utils/
    └── hand_landmarker.task  # modelo MediaPipe
```

---

## Instalação

```bash
pip install opencv-python mediapipe numpy
```

---

## Como Funciona

### 1. Captura de Vídeo (`main.py`)

- Abre a webcam com `cv2.VideoCapture(0)`
- Espelha o frame horizontalmente (`cv2.flip`) para experiência mais natural
- Converte BGR → RGB para o MediaPipe
- Envia o frame com timestamp via `detect_for_video` (modo vídeo, mais preciso que `detect`)
- Saída pelo X da janela


### 2. Detecção de Mãos (MediaPipe)

Utiliza a API `HandLandmarker` com o modelo `hand_landmarker.task`.

```python
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.5,
    min_tracking_confidence=0.3
)
```

O MediaPipe retorna **21 landmarks** por mão, cada um com coordenadas normalizadas (0 a 1):

```
Pontas:   4  8  12  16  20
Juntas:   3  6  10  14  18
Palma:    0 (pulso)
```

Converter para pixels:
```python
cx = int(landmark.x * largura)
cy = int(landmark.y * altura)
```

### 3. Detecção de Dedos (`dedos.py`)

Usa **distância euclidiana** em vez de comparação simples de Y — funciona com a mão em qualquer ângulo:

```python
import math

def distancia(p1, p2):
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

def indicador_levantado(hand) -> bool:
    palma = distancia(hand[0], hand[5])  # referência de escala
    dedo  = distancia(hand[0], hand[8])  # distância pulso → ponta
    return dedo > palma * 1.3
```

A palma serve como régua relativa — funciona com a mão perto ou longe da câmera.

O polegar é especial (dobra lateralmente, eixo X):
```python
def polegar_levantado(hand, mao_direita=True) -> bool:
    if mao_direita:
        return hand[4].x < hand[3].x
    else:
        return hand[4].x > hand[3].x
```

### 4. Gestos (`gestos.py`)

```python
class gestos:
    def __init__(self, hand):
        self.hand = hand

    def mao_aberta(self):
        return (indicador_levantado(self.hand) and
                medio_levantado(self.hand) and
                anelar_levantado(self.hand) and
                mindinho_levantado(self.hand))

    def mao_fechada(self):
        return (not indicador_levantado(self.hand) and
                not medio_levantado(self.hand) and
                not anelar_levantado(self.hand) and
                not mindinho_levantado(self.hand))
```

Na `main.py`:
```python
if resultado.hand_landmarks:
    for hand in resultado.hand_landmarks:
        g = gestos(hand)
        if g.mao_aberta():
            print("Aberta")
        elif g.mao_fechada():
            print("Fechada")
else:
    print("Mão não detectada")
```

### 5. Controle do Carro (`carro.py`)


```

---

## Landmarks de Referência

| Índice |       Parte        |
|--------|--------------------|
|    0   |       Pulso        |
|    4   |  Ponta do polegar  |
|    5   | Base do indicador  |
|    8   | Ponta do indicador |
|    12  |   Ponta do médio   |
|    16  |  Ponta do anelar   |
|    20  |  Ponta do mindinho |

---

## Decisões Técnicas

**Por que distância euclidiana e não comparação de Y?**
A comparação de Y falha quando a mão está inclinada ou de lado — todos os dedos ficam na mesma altura e parecem dobrados. A distância euclidiana funciona em qualquer orientação.

**Por que normalizar pela palma?**
A distância em pixels muda conforme a mão se aproxima ou afasta da câmera. Usar a palma como referência garante que a proporção seja sempre a mesma, independente da distância.

---