import math

def distancia(p1, p2):
    return math.hypot(p2.x - p1.x, p2.y - p1.y)

def indicador_levantado(hand) -> bool:
    palma = distancia(hand[0], hand[5])
    dedo = distancia(hand[0], hand[8])
    
    return dedo > palma * 1.3

def medio_levantado(hand) -> bool:
    palma = distancia(hand[0], hand[9])
    dedo = distancia(hand[0], hand[12])

    return dedo > palma * 1.3

def anelar_levantado(hand) -> bool: 
    palma = distancia(hand[0], hand[13])
    dedo = distancia(hand[0], hand[16])

    return dedo > palma * 1.3

def mindinho_levantado(hand) -> bool:
    palma = distancia(hand[0], hand[17])
    dedo = distancia(hand[0], hand[20])

    return dedo > palma * 1.3

def polegar_levantado(hand, lado) -> bool:
    ponta = hand[4]
    mcp   = hand[2]
    pulso = hand[0]
    
    # Base do indicador, se o dedão estiver colado aqui, está fechado
    base_indicador = hand[5]

    palma = distancia(pulso, mcp)
    dedo  = distancia(pulso, ponta)

    # Dedão colado na lateral do punho
    colado = distancia(ponta, base_indicador) < palma * 0.52

    direcao = ponta.x > mcp.x if lado == "Right" else ponta.x < mcp.x

    return dedo > palma * 1.3 and direcao and not colado