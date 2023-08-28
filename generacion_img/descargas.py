import GOES

def descarga_Rad(fecha_inicial, fecha_final, canales, path):
    """
    Parámetros: fecha_inicial (str) - formato: %Y%m%d%H%M%S ejemplo 20200320-060000
                fecha_final (str) - formato: %Y%m%d%H%M%S ejemplo 20200320-070000
                canales (list, str) ejemplo ['13','14','15']
                path (str) - path de salida
    """
    lista_descarga = GOES.download('goes16', 'ABI-L1b-RadF',
              DateTimeIni = fecha_inicial, DateTimeFin = fecha_final,
                channel = canales, rename_fmt = '%Y%m%d%H%M%S', path_out=path)
    
    
def descarga_TPW_LST(fecha_inicial, fecha_final, variable, path):
    """
    Parámetros: fecha_inicial (str) - formato: %Y%m%d%H%M%S ejemplo 20200320-060000
                fecha_final (str) - formato: %Y%m%d%H%M%S ejemplo 20200320-070000
                variable (str): si es LST = 'ABI-L2-LSTF'
                                si es TPW = 'ABI-L2-TPWF'
                path (str) - path de salida
    """
    lista_descarga = GOES.download('goes16',variable,DateTimeIni=fecha_inicial,DateTimeFin=fecha_final, 
                                   path_out=path)