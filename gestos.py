from dedos import indicador_levantado, medio_levantado, anelar_levantado, mindinho_levantado, polegar_levantado

class gestos:
    def __init__(self, hand, lado):
        self.hand = hand
        self.lado = lado

    def frente(self) -> bool:
        return indicador_levantado(self.hand) and medio_levantado(self.hand) and anelar_levantado(self.hand) and mindinho_levantado(self.hand) and polegar_levantado(self.hand, self.lado)
    
    def  parado(self):
        return not indicador_levantado(self.hand) and not medio_levantado(self.hand) and not anelar_levantado(self.hand) and not mindinho_levantado(self.hand) and not polegar_levantado(self.hand, self.lado)
    
    def re(self):
        return indicador_levantado(self.hand) and medio_levantado(self.hand) and not anelar_levantado(self.hand) and not mindinho_levantado(self.hand) and not polegar_levantado(self.hand, self.lado)
    
    def direita(self):
        return not indicador_levantado(self.hand) and not medio_levantado(self.hand) and not anelar_levantado(self.hand) and mindinho_levantado(self.hand) and not polegar_levantado(self.hand, self.lado)
    
    def esquerda(self):
        return not indicador_levantado(self.hand) and not medio_levantado(self.hand) and not anelar_levantado(self.hand) and not mindinho_levantado(self.hand) and polegar_levantado(self.hand, self.lado)