#define PIR_PIN 15  // Your PIR signal output pin

unsigned long pirStartTime = 0;
unsigned long motionHoldTime = 4000; // 4s required to confirm motion
bool motionConfirmed = false;

void setup() {
  pinMode(PIR_PIN, INPUT);
  Serial.begin(115200);
  Serial.println("🔍 PIR Sensor Test Started");
}

void loop() {
  unsigned long now = millis();
  bool pirRaw = digitalRead(PIR_PIN) == HIGH;

  // Print raw signal
  Serial.print("Time: ");
  Serial.print(now);
  Serial.print(" ms | PIR: ");
  Serial.print(pirRaw ? "HIGH (motion)" : "LOW  (idle)");

  // Software filtering
  if (pirRaw) {
    if (pirStartTime == 0) pirStartTime = now;

    if ((now - pirStartTime) >= motionHoldTime && !motionConfirmed) {
      motionConfirmed = true;
      Serial.print(" | ✅ Filtered motion confirmed");
    }
  } else {
    pirStartTime = 0;
    if (motionConfirmed) {
      Serial.print(" | 🔁 Motion ended, reset");
      motionConfirmed = false;
    }
  }

  Serial.println();
  delay(100);  // Adjust for resolution
}
