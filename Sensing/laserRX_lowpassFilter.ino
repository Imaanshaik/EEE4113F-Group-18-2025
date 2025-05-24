#define LASER_TX_PIN 26
#define LASER_RX_PIN 4
#define CAMERA_TRIGGER_LED 18

unsigned long beamBreakStartTime = 0;
bool beamBrokenConfirmed = false;

void setup() {
  pinMode(LASER_TX_PIN, OUTPUT);
  pinMode(LASER_RX_PIN, INPUT);
  pinMode(CAMERA_TRIGGER_LED, OUTPUT);

  // Turn on laser
  digitalWrite(LASER_TX_PIN, HIGH);

  // Init serial monitor
  Serial.begin(115200);
}

void loop() {
  int laserState = digitalRead(LASER_RX_PIN);  // 0 = beam intact, 1 = beam broken

  // Beam broken
  if (laserState == HIGH) {
    if (!beamBrokenConfirmed) {
      // Start timing
      if (beamBreakStartTime == 0) {
        beamBreakStartTime = millis();
      }

      // Check if sustained break > 2s
      if (millis() - beamBreakStartTime > 2000) {
        beamBrokenConfirmed = true;
        Serial.println("✅ Beam broken for >2s — TRIGGERING CAMERA!");
        digitalWrite(CAMERA_TRIGGER_LED, HIGH);  // Trigger
      }
    }
  } else {
    // Beam is intact again, reset
    beamBreakStartTime = 0;
    beamBrokenConfirmed = false;
    digitalWrite(CAMERA_TRIGGER_LED, LOW);  // Reset camera LED
    Serial.println("🌟 Beam intact (laser detected)");
  }

  delay(100);
}
