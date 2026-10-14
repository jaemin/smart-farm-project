#include <WiFi.h>
#include <WebSocketsClient.h>
#include "local_wifi.h"

WebSocketsClient webSocket;

char r_buf[100];

void webSocketEvent(WStype_t type, uint8_t* payload, size_t length) {
  switch (type) {
    case WStype_CONNECTED:
      Serial.println("WebSocket connected");
      break;

    case WStype_DISCONNECTED:
      Serial.println("WebSocket disconnected");
      break;

    case WStype_TEXT:      
      strcpy(r_buf, (char*)payload);
      Serial1.print(r_buf);      
      Serial.print("[Flask -> ESP32] ");
      Serial.println(r_buf);
      break;
  }
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  Serial1.begin(115200);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  webSocket.begin(host, port, url);

  webSocket.onEvent(webSocketEvent);

  // 연결이 끊어지면 자동 재연결
  webSocket.setReconnectInterval(5000);
}

void loop() {
  webSocket.loop();

  if(Serial1.available() > 0) {
    String str = Serial1.readStringUntil('\n');

    // STM32에게 받은 데이터가 센서 데이터 및 액추에이터 상태인 경우
    if(str.charAt(0) == '[' && str.charAt(5) == ']') {
      while(str.indexOf(split_c) != -1){
        String data = str.substring(0, str.indexOf(split_c));
        str = str.substring(str.indexOf(split_c) + 1);

        String sendStr = "sensor=" + data.substring(1, 5) + split_c + "value=" + data.substring(6);
        webSocket.sendTXT(sendStr);
        Serial.print("[ESP32 -> Flask] ");
        Serial.println(sendStr);
      }
    }
    // STM32에게 받은 데이터가 액추에이터 상태 요청인 경우
    else if (str.compareTo("actuator") == 0) {
      webSocket.sendTXT("Actuator request");
      Serial.println("[ESP32 -> Flask] Actuator Request");
    }
  }
}