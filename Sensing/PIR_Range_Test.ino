#define PIR_PIN           15
#define LASER_RX_PIN      4     // Receiver: LOW = beam present, HIGH = beam broken
#define LASER_TX_CTRL     26
#define CAMERA_TRIGGER    18
#define LED_PIN           2

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
  pinMode(CAMERA_TRIGGER, OUTPUT);
  pinMode(LED_PIN, OUTPUT);

  digitalWrite(LASER_TX_CTRL, LOW);
  digitalWrite(CAMERA_TRIGGER, LOW);
  digitalWrite(LED_PIN, LOW);

  Serial.begin(115200);
  Serial.println("🔧 Predator Detection System Ready");
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

      // Trigger immediately if beam broken long enough
      if ((now - beamBreakStart) >= beamBreakHold) {
        Serial.println("🚨 Beam broken ≥2s. Triggering camera.");
        digitalWrite(CAMERA_TRIGGER, HIGH);
        digitalWrite(LED_PIN, HIGH);
        cameraStartTime = now;
        cameraTriggered = true;

        // Shutdown laser
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

    // If laser ON for 10s and no valid beam break
    if ((now - laserStartTime) >= laserOnTime && !beamBrokenLong) {
      Serial.println("✅ Laser expired after 10s. No beam break.");
      digitalWrite(LASER_TX_CTRL, LOW);
      laserOn = false;
      pirMotionValid = false;
    }
  }

  // === Camera Hold ===
  if (cameraTriggered && (now - cameraStartTime) >= cameraHoldTime) {
    digitalWrite(CAMERA_TRIGGER, LOW);
    digitalWrite(LED_PIN, LOW);
    cameraTriggered = false;
    Serial.println("✅ Camera finished recording.");
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
