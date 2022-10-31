## MODULOS NECESARIOS
import math

# funcion para redondear a mas, obtenida por otro usuario

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
    


## calculando la velocidad del agua en el desarenador

def vel_CAMP(d):
    '''
    calculo de la velocidad del flujo dentro de un desarenador
    d : diametro de la particula en milimetros
    '''
    valor_a = 0
    
    if d >= 1:
        valor_a = 36
    elif d >= 0.2:
        valor_a = 44
    else:
        valor_a = 51

    raiz_diametro = d ** .5

    return round(raiz_diametro * valor_a, 0)


## formua de bestelli, sokolovm velikanov para calculo de longitud de sedimentacion

def l_sedim(h, v, w):
    '''
    calculo de la longitud de sedimentacion
    h = altuta en m
    v = velocidad del flujo m/seg
    w = velocidad de caida de la particula m/seg
    '''

    numera = (h ** (3/2)) * v
    denomi = (h ** .5) * w - 0.132 * v
    return round_decimals_up(numera / denomi, 0)


## velocidad de caida en aguas tranquilas

def v_caida_tranq(d):
    '''
    calculo de velocidad de caida de una particula en aguas tranquilas
    d = diametro de la particula en milimetros
    '''
    # constantes:
    g = 9.81 # gravedad
    ps = 2.650 # densidad del sedimento
    pw = 1.000 # densidad del agua
    vs = 1.3 * (10 ** (-6)) # viscosidad del agua
    dm = d / 1000 # diametro en metros

    # Primero calcularemos D
    # operacion entre corchetes
    numera_1 = (ps / pw - 1) * g
    denomi_1 = vs ** 2
    raiz_1 = (numera_1 / denomi_1) ** (1/3)

    D =  round(raiz_1 * dm, 3)

    # ahora calculamos el resto de operaciones
    divisi_1 = 11 * vs / dm
    raiz_2 = (1 + 0.01 * (D ** 3)) ** .5

    final = divisi_1 * (raiz_2 - 1)

    # se retorna la velocidad en centimetros por segundo
    return round_decimals_up(final * 100, 2)


## velocidad maxima admisible o velocidad critica

def v_cri_desar(d, b, h):
    '''
    calculo de velocidad critica o velocidad maxima admisible
    d = diametro de particula en milimetros
    b = ancho de la nave
    h = alto de la nave
    '''

    # Constantes
    ps = 2.650 # densidad del sedimento
    pw = 1.000 # densidad del agua
    n = 0.013 # rugosidad de maning
    ks = 1 / n # factor de rugosidad, 0.013 es el numero de maning

    # empezamos calculando la raiz
    divisi_1 = (ps / pw) - 1
    diamet_1 = d / 1000 # pasamos el diametro a metros
    raiz_1 = (divisi_1 * diamet_1 * 0.03) ** .5

    # calcular el radio hidraulico
    area = b * h
    peri = b + 2 * h
    rh = area / peri
    # calculo del R a la 1/6
    rh_6 = rh ** (1 / 6)

    # juntamos todo
    v_final = ks * rh_6 * raiz_1

    return round_decimals_up(v_final, 2)