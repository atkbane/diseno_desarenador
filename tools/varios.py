## IMPORTAR LOS MODULOS NECESARIOS

import math

## redondear decimales siempre a mas
# este script fue obtenido de la pagina https://kodify.net/python/math/round-decimals/ 

def round_decimals_up(number:float, decimals:int=2):
    """
    Retorna un valor redondeado a mas con una cantidad de decimales dados
    """
    
    # comprueba si el numero dado no es valido para el programa
    if not isinstance(decimals, int):
        raise TypeError("posicion de decimales debe ser un entero")
    elif decimals < 0:
        raise ValueError("posicion de decimales debe ser 0 o mas")
    elif decimals == 0:
        return math.ceil(number)

    factor = 10 ** decimals
    return math.ceil(number * factor) / factor
    