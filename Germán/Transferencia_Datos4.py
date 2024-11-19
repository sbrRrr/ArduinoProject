import paho.mqtt.client as paho
import time
import signal
import mysql.connector
from mysql.connector import errorcode

# Dirección y puerto del broker MQTT
mqtt_broker = "Broker.MQTT"
mqtt_port = 1883

# Variables globales para almacenar los datos recibidos de cada MCU
distance = speed = 0
distance2 = speed2 = 0
distance3 = speed3 = 0
distance4 = speed4 = 0
distance5 = speed5 = 0

# Configuración de la base de datos MySQL
host = "Nombre_host"  # Dirección del servidor MySQL
user = "Nombre_usuario"  # Usuario de MySQL
password = "Contraseña_BasedDeDatos_MySQL"  # Contraseña de MySQL
database_name = "Nombre_base_de_datos"  # Nombre de la base de datos
table_name = "Nombre_tabla"  # Nombre de la tabla

# Conectar a la base de datos MySQL
def connect_to_db():
    try:
        cnx = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_name
        )
        print("Conexión a la base de datos exitosa.")
        return cnx
    except mysql.connector.Error as err:
        print(f"Error al conectar a la base de datos: {err}")
        return None

# Función para insertar los valores de distancia y velocidad en la base de datos
def insert_into_db():
    global distance, speed, distance2, speed2, distance3, speed3, distance4, speed4, distance5, speed5

    # Aseguramos que todos los valores son válidos
    if None in [distance, speed, distance2, speed2, distance3, speed3, distance4, speed4, distance5, speed5]:
        print("Faltan datos, no se puede insertar.")
        return

    try:
        # Conectar a la base de datos
        cnx = connect_to_db()
        if cnx is None:
            print("No se pudo conectar a la base de datos.")
            return

        cursor = cnx.cursor()

        # Consulta SQL para insertar los datos
        insertion_query = f"""
        INSERT INTO {table_name} 
        (distance, speed, distance2, speed2, distance3, speed3, distance4, speed4, distance5, speed5)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        # Verificamos que los valores sean floats antes de insertarlos
        data = (float(distance), float(speed), float(distance2), float(speed2), float(distance3), float(speed3), 
                float(distance4), float(speed4), float(distance5), float(speed5))
        
        cursor.execute(insertion_query, data)
        cnx.commit()  # Confirmar la transacción
        print(f"Datos insertados: {data}")

    except mysql.connector.Error as err:
        print(f"Error al insertar datos en la base de datos: {err}")
    finally:
        if cnx is not None and cnx.is_connected():
            cursor.close()  # Asegúrate de cerrar el cursor antes de la conexión
            cnx.close()  # Asegúrate de cerrar la conexión

# Callback cuando el cliente se conecta al broker MQTT
def on_connect(client, userdata, flags, rc):
    """Callback cuando el cliente se conecta al broker MQTT."""
    print(f"Conectado al broker MQTT con el código de resultado {rc}")
    
    # Suscripción a los tópicos para recibir distancia y velocidad de los 5 MCUs
    client.subscribe("arduino1/mediciones/distance")
    client.subscribe("arduino1/mediciones/speed")
    client.subscribe("arduino2/mediciones/distance")
    client.subscribe("arduino2/mediciones/speed")
    client.subscribe("arduino3/mediciones/distance")
    client.subscribe("arduino3/mediciones/speed")
    client.subscribe("arduino4/mediciones/distance")
    client.subscribe("arduino4/mediciones/speed")
    client.subscribe("arduino5/mediciones/distance")
    client.subscribe("arduino5/mediciones/speed")

# Callback para manejar los mensajes recibidos
def on_message(client, userdata, msg):
    global distance, speed, distance2, speed2, distance3, speed3, distance4, speed4, distance5, speed5
    payload = msg.payload.decode()

    # Procesar los datos recibidos según el tópico
    if msg.topic == "arduino1/mediciones/distance":
        distance = float(payload)
        print(f"Distancia1 recibida: {distance} metros")
    elif msg.topic == "arduino1/mediciones/speed":
        speed = float(payload)
        print(f"Velocidad1 recibida: {speed} m/s")
    
    elif msg.topic == "arduino2/mediciones/distance":
        distance2 = float(payload)
        print(f"Distancia2 recibida: {distance2} metros")
    elif msg.topic == "arduino2/mediciones/speed":
        speed2 = float(payload)
        print(f"Velocidad2 recibida: {speed2} m/s")
    
    elif msg.topic == "arduino3/mediciones/distance":
        distance3 = float(payload)
        print(f"Distancia3 recibida: {distance3} metros")
    elif msg.topic == "arduino3/mediciones/speed":
        speed3 = float(payload)
        print(f"Velocidad3 recibida: {speed3} m/s")
    
    elif msg.topic == "arduino4/mediciones/distance":
        distance4 = float(payload)
        print(f"Distancia4 recibida: {distance4} metros")
    elif msg.topic == "arduino4/mediciones/speed":
        speed4 = float(payload)
        print(f"Velocidad4 recibida: {speed4} m/s")
    
    elif msg.topic == "arduino5/mediciones/distance":
        distance5 = float(payload)
        print(f"Distancia5 recibida: {distance5} metros")
    elif msg.topic == "arduino5/mediciones/speed":
        speed5 = float(payload)
        print(f"Velocidad5 recibida: {speed5} m/s")
    
    # Si todos los datos están disponibles, inserta en la base de datos
    if all(v is not None for v in [distance, speed, distance2, speed2, distance3, speed3, distance4, speed4, distance5, speed5]):
        print(f"\nTodos los datos recibidos:")
        insert_into_db()

# Manejo de la señal de interrupción (Ctrl+C)
def signal_handler(sig, frame):
    """Manejo de la señal de interrupción (Ctrl+C)."""
    print("\n¡Desconectando!")
    client.disconnect()
    exit(0)

# Configuración del cliente MQTT
client = paho.Client()

# Asignar los callbacks
client.on_connect = on_connect
client.on_message = on_message

# Configuración de la señal para Ctrl+C (salir del programa)
signal.signal(signal.SIGINT, signal_handler)

# Conexión al broker MQTT
client.connect(mqtt_broker, mqtt_port, 60)

# Mantener el cliente en un bucle para escuchar los mensajes
print("Conectando al broker MQTT...")
client.loop_start()

try:
    print("Esperando mensajes MQTT...")
    while True:
        # El bucle principal no hace nada, ya que todo se maneja con los callbacks
        time.sleep(1)

except KeyboardInterrupt:
    # Permitir salir limpiamente con Ctrl+C
    signal_handler(None, None)
