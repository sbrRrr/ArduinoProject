//Aunque no te corra el código acá, si todo está bien configurado, entonces el código de python 
//debería correr de forma inalámbrica sin ningún problema. 

#include <ESP8266WiFi.h>
#include <PubSubClient.h>

// Configura tu red WiFi
const char* ssid = "Nombre_red";
const char* password = "Contraseña_de_red";

// Configura tu servidor MQTT
const char* mqtt_server = "Direccion.Broker.MQTT"; // Dirección del broker MQTT
const int mqtt_port = 1883; // Puerto MQTT

WiFiClient espClient;
PubSubClient client(espClient);

const int trigPin = D6;
const int echoPin = D5;
const int buzzerPin = D1;

#define SOUND_VELOCITY 0.034
#define SPEED_THRESHOLD 0.5
#define NEGATIVE_SPEED_THRESHOLD -0.5

long duration;
float distanceM;
float distancePrevM = 0;
unsigned long previousTime = 0;

void setup() {
  Serial.begin(115200);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(buzzerPin, OUTPUT);
  
  // Conexión WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Conectando a WiFi...");
  }
  Serial.println("Conexión WiFi establecida.");

  // Conexión al broker MQTT
  client.setServer(mqtt_server, mqtt_port);
  while (!client.connected()) {
    if (client.connect("ArduinoClient1")) { //Cambiar el número de cliente 
      Serial.println("Conectado al broker MQTT.");
    } else {
      delay(5000);
      Serial.print("Error de conexión MQTT, intentando nuevamente...");
    }
  }
}

void loop() {
  // Establece el trigPin
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  // Lee el echoPin
  duration = pulseIn(echoPin, HIGH);
  
  // Calcula la distancia
  distanceM = (duration * SOUND_VELOCITY / 2) * 0.01;
  
  // Calcula la velocidad
  unsigned long currentTime = millis();
  float speed = (distanceM - distancePrevM) / ((currentTime - previousTime) / 1000.0);

  // Publica los datos a través de MQTT
  char distanceStr[10];
  char speedStr[10];
  dtostrf(distanceM, 5, 2, distanceStr); // Convierte la distancia a string
  dtostrf(speed, 5, 2, speedStr); // Convierte la velocidad a string

  // Publica en los tópicos MQTT correspondientes. //Cambiar el número de arduino acá. 
  client.publish("arduino1/mediciones/distance", distanceStr);
  client.publish("arduino1/mediciones/speed", speedStr);

  // Acciona el buzzer si la velocidad es mayor al umbral
  if (distanceM>=0.18) {
    activateBuzzer(1000);
  } else {
    digitalWrite(buzzerPin, LOW);
  }

  distancePrevM = distanceM;
  previousTime = currentTime;
  
  delay(1000); // Espera 1 segundo
}

void activateBuzzer(int times) {
  for (int i = 0; i < times; i++) {
    digitalWrite(buzzerPin, HIGH);
    delay(1);
    digitalWrite(buzzerPin, LOW);
    delay(1);
  }
}
