#define PIR_PIN           15
#define LASER_RX_PIN      4     // Receiver: LOW = beam present, HIGH = beam broken
#define LASER_TX_CTRL     26
#define LED_PIN           2     // Onboard LED used to simulate camera trigger

// === Timing Settings ===
unsigned long minMotionDuration = 4000;    // 4s  - PIR must be HIGH
unsigned long laserOnTime       = 10000;   // 10s - Max laser ON time
unsigned long beamBreakHold     = 2000;    // 2s  - Beam must be broken
unsigned long cameraHoldTime    = 15000;   // 15s - Camera trigger duration
unsigned long cooldownTime      = 10000;   // 10s - Post-camera cooldown

// === Timers ===
unsigned long pirStartTime      = 0;
unsigned long laserStartTime    = 0;
unsigned long beamBreakStart    = 0;
unsigned long cameraStartTime   = 0;
unsigned long lastTriggerTime   = 0;

// === Flags ===
bool laserOn         = false;
bool cameraTriggered = false;
bool cooldown        = false;
bool pirMotionValid  = false;
bool beamBrokenLong  = false;

void setup() {
  pinMode(PIR_PIN, INPUT);
  pinMode(LASER_RX_PIN, INPUT);
  pinMode(LASER_TX_CTRL, OUTPUT);
  pinMode(LED_PIN, OUTPUT);

  digitalWrite(LASER_TX_CTRL, LOW);
  digitalWrite(LED_PIN, LOW);

  Serial.begin(115200);     // USB debug output
  Serial2.begin(115200, SERIAL_8N1, 17, 16); // UART: TX=17, RX=16 (not used)

  Serial.println("🔧 Predator Detection System Ready (LED = camera trigger)");
}

void loop() {
  unsigned long now = millis();

  // === Sensor Reads ===
  bool pirDetected    = digitalRead(PIR_PIN) == HIGH;
  bool beamDetected   = digitalRead(LASER_RX_PIN) == LOW;
  bool beamBroken     = !beamDetected;  // HIGH = broken

  // === PIR Filtering ===
  if (!laserOn && !cameraTriggered && !cooldown) {
    if (pirDetected) {
      if (pirStartTime == 0) pirStartTime = now;

      if ((now - pirStartTime) >= minMotionDuration && !pirMotionValid) {
        pirMotionValid = true;
        laserOn = true;
        laserStartTime = now;
        digitalWrite(LASER_TX_CTRL, HIGH);
        Serial.println("✅ PIR motion confirmed. Laser ON for max 10s.");
      }
    } else {
      pirStartTime = 0;
    }
  }

  // === Laser ON: Watch for early or late beam break ===
  if (laserOn) {
    if (beamBroken) {
      if (beamBreakStart == 0) beamBreakStart = now;

      if ((now - beamBreakStart) >= beamBreakHold) {
        Serial.println("🚨 Beam broken ≥2s. Triggering camera (LED ON + UART).");
        digitalWrite(LED_PIN, HIGH);
        cameraStartTime = now;
        cameraTriggered = true;

        // Trigger Raspberry Pi via UART
        Serial2.println("CAPTURE");

        // Turn off laser and start cooldown
        digitalWrite(LASER_TX_CTRL, LOW);
        laserOn = false;
        cooldown = true;
        lastTriggerTime = now;
        pirMotionValid = false;
        beamBrokenLong = true;
      }
    } else {
      beamBreakStart = 0;
    }

    if ((now - laserStartTime) >= laserOnTime && !beamBrokenLong) {
      Serial.println("✅ Laser expired after 10s. No beam break.");
      digitalWrite(LASER_TX_CTRL, LOW);
      laserOn = false;
      pirMotionValid = false;
    }
  }

  // === Camera Hold ===
  if (cameraTriggered && (now - cameraStartTime) >= cameraHoldTime) {
    digitalWrite(LED_PIN, LOW);
    cameraTriggered = false;
    Serial.println("✅ Camera finished recording (LED OFF).");
  }

  // === Cooldown Reset ===
  if (cooldown && (now - lastTriggerTime >= cooldownTime)) {
    cooldown = false;
    beamBrokenLong = false;
    beamBreakStart = 0;
    pirStartTime = 0;
    Serial.println("✅ Cooldown ended. System rearmed.");
  }

  delay(50);
}
