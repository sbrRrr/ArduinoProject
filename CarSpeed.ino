/*********
  Rui Santos
  Complete project details at https://RandomNerdTutorials.com/esp8266-nodemcu-hc-sr04-ultrasonic-arduino/
  
  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files.
  
  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.
*********/

const int trigPin = 12;
const int echoPin = 14;
const int buzzerPin = D1; // Pin D1 para el buzzer

// Define sound velocity in cm/uS
#define SOUND_VELOCITY 0.034
#define SPEED_THRESHOLD 2.77 // Velocidad umbral en m/s

long duration;
float distanceM;
float distancePrevM = 0; // Distancia previa
unsigned long previousTime = 0;

void setup() {
  Serial.begin(115200); // Inicia la comunicación serial
  pinMode(trigPin, OUTPUT); // Establece trigPin como salida
  pinMode(echoPin, INPUT); // Establece echoPin como entrada
  pinMode(buzzerPin, OUTPUT); // Establece buzzerPin como salida
}

void loop() {
  // Limpia el trigPin
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  // Establece el trigPin en estado alto durante 10 microsegundos
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  // Lee el echoPin, retorna el tiempo de viaje de la onda sonora en microsegundos
  duration = pulseIn(echoPin, HIGH);
  
  // Calcula la distancia
  distanceM = (duration * SOUND_VELOCITY / 2) * 0.01; // Conversión a metros
  
  // Calcula la velocidad
  unsigned long currentTime = millis();
  float speed = (distanceM - distancePrevM) / ((currentTime - previousTime) / 1000.0); // velocidad en m/s

  // Imprime la distancia y la velocidad en el monitor serial
  Serial.print("Distance (m): ");
  Serial.println(distanceM);
  Serial.print("Speed (m/s): ");
  Serial.println(speed);
  
  // Acciona el buzzer si la velocidad es mayor al umbral
  if (speed > SPEED_THRESHOLD) {
    activateBuzzer(20); // Activa el buzzer 10 veces
  } else {
    digitalWrite(buzzerPin, LOW); // Desactiva el buzzer
  }
  
  // Actualiza la distancia previa y el tiempo
  distancePrevM = distanceM;
  previousTime = currentTime;
  
  delay(1000);
}

void activateBuzzer(int times) {
  for (int i = 0; i < times; i++) {
    digitalWrite(buzzerPin, HIGH); // Activa el buzzer
    delay(1); // Espera 1 milisegundo
    digitalWrite(buzzerPin, LOW); // Desactiva el buzzer
    delay(1); // Espera 1 milisegundo
  }
}
