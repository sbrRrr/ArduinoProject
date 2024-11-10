import paho.mqtt.client as paho
import time
import signal
import mysql.connector
from mysql.connector import errorcode

# Dirección y puerto del broker MQTT
mqtt_broker = "192.168.101.115"
mqtt_port = 1883

# Variables globales para almacenar los datos recibidos
distance = None
speed = None

# Configuración de la base de datos MySQL
host = "127.0.0.1"  # Dirección del servidor MySQL
user = "root"  # Usuario de MySQL
password = "Nano_humpa32_32"  # Contraseña de MySQL
database_name = "COMPANY"  # Nombre de la base de datos
table_name = "mediciones"  # Nombre de la tabla

# Conectar a la base de datos MySQL
def connect_to_db():
    try:
        cnx = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_name
        )
        return cnx
    except mysql.connector.Error as err:
        print(f"Error al conectar a la base de datos: {err}")
        return None

# Función para insertar los valores de distancia y velocidad en la base de datos
def insert_into_db(distance, speed):
    try:
        # Conectar a la base de datos
        cnx = connect_to_db()
        if cnx is None:
            return
        
        cursor = cnx.cursor()

        # Consulta SQL para insertar los datos
        insertion_query = f"""
        INSERT INTO {table_name} (distance, speed)
        VALUES (%s, %s)
        """
        cursor.execute(insertion_query, (distance, speed))
        cnx.commit()  # Confirmar la transacción
        print(f"Datos insertados - Distancia: {distance} metros, Velocidad: {speed} m/s")

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
    
    # Suscripción a los tópicos para recibir distancia y velocidad
    client.subscribe("arduino1/mediciones/distance")
    client.subscribe("arduino2/mediciones/speed")

# Callback para manejar los mensajes recibidos
def on_message(client, userdata, msg):
    """Callback para manejar los mensajes recibidos."""
    global distance, speed
    payload = msg.payload.decode()
    
    if msg.topic == "arduino1/mediciones/distance":
        distance = float(payload)  # Convertir a float para poder almacenarlo en la base de datos
        print(f"Distancia recibida: {distance} metros")
    elif msg.topic == "arduino2/mediciones/speed":
        speed = float(payload)  # Convertir a float para poder almacenarlo en la base de datos
        print(f"Velocidad recibida: {speed} m/s")
    
    # Si ambos datos están disponibles, muestra la información e inserta en la base de datos
    if distance is not None and speed is not None:
        print(f"\nValores actuales - Distancia: {distance} metros, Velocidad: {speed} m/s")
        insert_into_db(distance, speed)

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


