import sys

# Verifica si la librería pyscard está instalada

try:
    from smartcard.System import readers
except ImportError:
    print("La librería 'pyscard' no está instalada.")
    print("Para instalarla, ejecuta el siguiente comando en tu terminal:")
    print("pip install pyscard")
    sys.exit()

def detectar_dnie():
    
    #Función que detecta si un lector de tarjetas y un DNIe están conectados.
    try:
        # Obtener la lista de lectores de tarjetas disponibles
        lista_lectores = readers()
        
        # Si no se detecta ningún lector, muestra un mensaje y termina
        if not lista_lectores:
            #print("No se ha detectado ningún lector de tarjetas.")
            return False

        #print(f" Lector de tarjetas detectado: {lista_lectores[0]}")
        #print("Esperando la inserción del DNIe...")
        
        # Obtener el primer lector disponible
        lector = lista_lectores[0]
        
        # Conectarse al lector
        conexion = lector.createConnection()
        
        try:
            # Intentar conectarse a la tarjeta (DNIe)
            conexion.connect()
            
            # Si la conexión es exitosa, se ha detectado un DNIe
            #print("¡DNIe detectado!")
            return True
            
        except Exception as e:
            # Si no se puede conectar, es probable que no haya un DNIe insertado
            #print("No se ha detectado el DNIe en el lector.")
            return False
            
    except Exception as e:
        #print(f"Se ha producido un error")
        return False

