#include "DHT.h"
#include "WiFi.h"
#include "HTTPClient.h"

// Configuração do sensor de temperatura
#define DHTPIN 4 // Pino de dados do sensor de temperatura
#define DHTTYPE DHT11 // Especificando que o sensor de temperatura é o DHT11 
DHT dht(DHTPIN, DHTTYPE); // Inicializando o sensor de temperatura

int secondsToWait = 5 * 1000; // Segundos de delay entre leituras

// Configuração do WiFi
const char WIFI_SSID[] = "Macuxi Digital";
const char WIFI_PASSWORD[] = "@Macuxi#ufrr35anos";

String HOST_NAME = "https://api-maloca.ed-henrique.com";
String PATH_NAME   = "/temperature";

HTTPClient http;

void setup() {
  Serial.begin(115200);
  dht.begin();

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.println("Connecting");
  while(WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Conectado.");

  http.begin(HOST_NAME + PATH_NAME);
}

void loop() {
  delay(secondsToWait);

  float t = dht.readTemperature(); // Ler temperatura

  if (isnan(t)) {
    return;
  }

  http.addHeader("Content-Type", "application/json");
  int httpResponseCode = http.POST("{\"patient_id\":\"1\",\"celsius\":\"" + String(t) + "\"}");
  Serial.print("HTTP Response code: ");
  Serial.println(httpResponseCode);
}
