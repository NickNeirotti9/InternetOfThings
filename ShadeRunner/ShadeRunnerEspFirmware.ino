#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>
#include "time.h"

const char* ssid = "Wifi Name";
const char* password = "Password";

const char* ntpServer = "pool.ntp.org";
const long gmtOffset_sec = -18000;  // EST
const int daylightOffset_sec = 0;

WebServer server(80);

String sunrise = "00:00:00";
String sunset = "00:00:00";

// Motor pins
#define MOTOR_IN1 1
#define MOTOR_IN2 2

void setupTime() {
    configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
    Serial.println("Time sync requested...");
}

String getCurrentTime() {
    struct tm timeinfo;
    if (!getLocalTime(&timeinfo)) {
        Serial.println("Failed to obtain time");
        return "00:00:00";
    }
    char timeString[9];
    strftime(timeString, sizeof(timeString), "%H:%M:%S", &timeinfo);
    return String(timeString);
}

void handleSetTimes() {
    if (server.hasArg("plain")) {
        String body = server.arg("plain");
        Serial.print("Raw Body: ");
        Serial.println(body);

        StaticJsonDocument<200> doc;
        DeserializationError error = deserializeJson(doc, body);

        if (error) {
            Serial.println("JSON Parsing Error");
            server.send(400, "text/plain", "JSON Parsing Error");
            return;
        }

        sunrise = doc["sunrise"].as<String>();
        sunset = doc["sunset"].as<String>();

        Serial.println("Received new times:");
        Serial.print("Sunrise: ");
        Serial.println(sunrise);
        Serial.print("Sunset: ");
        Serial.println(sunset);

        server.send(200, "text/plain", "Times received");
    } else {
        server.send(400, "text/plain", "No body received");
    }
}

void openBlinds() {
    Serial.println("Opening blinds...");
    digitalWrite(MOTOR_IN2, HIGH);
    digitalWrite(MOTOR_IN1, LOW);
    delay(10000);  // Run motor for 10 seconds
    stopMotor();
}

void closeBlinds() {
    Serial.println("Closing blinds...");
    digitalWrite(MOTOR_IN2, LOW);
    digitalWrite(MOTOR_IN1, HIGH);
    delay(10000);
    stopMotor();
}

void stopMotor() {
    digitalWrite(MOTOR_IN1, LOW);
    digitalWrite(MOTOR_IN2, LOW);
}

void setup() {
    Serial.begin(115200);

    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connecting to WiFi...");
    }
    Serial.println("Connected to WiFi");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());

    setupTime();  // Sync NTP time on boot

    server.on("/set_times", HTTP_POST, handleSetTimes);
    server.begin();

    pinMode(MOTOR_IN1, OUTPUT);
    pinMode(MOTOR_IN2, OUTPUT);

    stopMotor(); // Start with motor off
}

void loop() {
    server.handleClient();

    String currentTime = getCurrentTime();
    Serial.print("Current Time: ");
    Serial.println(currentTime);

    if (currentTime == sunrise) {
        openBlinds();
    }
    if (currentTime == sunset) {
        closeBlinds();
    }

    delay(1000);
}
