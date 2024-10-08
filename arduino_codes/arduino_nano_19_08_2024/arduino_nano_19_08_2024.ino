#define TURNSTILE_ON_TIME_MS 3500
#define COMMUNICATION_TIMEOUT_MS 10000
#define THIS_IS_ARDUINO_CHECK_CHAR 'i'
#define TURNSTILE_RELAY_OFF_CHAR '0'
#define TURNSTILE_RELAY_ON_CHAR '1'

#define TURNSTILE_IS_ACTIVATED_IF_HIGH false  // when the output is low, turnstiles are activated so that if power is off, turnstiles are not blocked.

#define TURNSTILE_RELAY_SIGNAL_PIN 10      // if HIGH, turnstile relay is energized
#define TURNSTILE_RELAY_NOT_SIGNAL_PIN 11  // Logical not of the TURNSTILE_RELAY_SIGNAL_PIN, used for indicator LED
#define BACKUP_RELAY_SIGNAL_PIN A0
#define BACKUP_RELAY_NOT_SIGNAL_PIN 13

unsigned long last_time_communication_ms = 0;
unsigned long last_time_turnstile_activated = 0;

void setup() {
  Serial.begin(9600);
  pinMode(TURNSTILE_RELAY_SIGNAL_PIN, OUTPUT);
  pinMode(TURNSTILE_RELAY_NOT_SIGNAL_PIN, OUTPUT);
  pinMode(BACKUP_RELAY_SIGNAL_PIN, OUTPUT);
  pinMode(BACKUP_RELAY_NOT_SIGNAL_PIN, OUTPUT);
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    last_time_communication_ms = millis();
    if (c == THIS_IS_ARDUINO_CHECK_CHAR) {  // send a reply so that the computer knows this is the arduino port
      Serial.println("THIS_IS_ARDUINO");
    } else if (c == TURNSTILE_RELAY_ON_CHAR) {  // Activate turnstile for a while
      last_time_turnstile_activated = millis();
    } else if (c == TURNSTILE_RELAY_OFF_CHAR) {  // Deactivate Turnstile due to timeout
      last_time_turnstile_activated = 0;
    } 
  }

  //=============================================================================
  // Set whether turnstile is activated or not
  if ((millis() - last_time_communication_ms) > COMMUNICATION_TIMEOUT_MS) {
    activate_turnstile();  // If miru does not send any command from the serial, keep turnstile activated
  } else if ((millis() - last_time_turnstile_activated) < TURNSTILE_ON_TIME_MS) {
    activate_turnstile();  //If miru sent activate turnstile command recently, keep turnstile activated
  } else {
    block_turnstile();
  }
}

void activate_turnstile() {
  if (TURNSTILE_IS_ACTIVATED_IF_HIGH) {
    digitalWrite(TURNSTILE_RELAY_SIGNAL_PIN, HIGH);
    digitalWrite(TURNSTILE_RELAY_NOT_SIGNAL_PIN, LOW);
  } else {
    digitalWrite(TURNSTILE_RELAY_SIGNAL_PIN, LOW);
    digitalWrite(TURNSTILE_RELAY_NOT_SIGNAL_PIN, HIGH);
  }
}

void block_turnstile() {
  if (TURNSTILE_IS_ACTIVATED_IF_HIGH) {
    digitalWrite(TURNSTILE_RELAY_SIGNAL_PIN, LOW);
    digitalWrite(TURNSTILE_RELAY_NOT_SIGNAL_PIN, HIGH);
  } else {
    digitalWrite(TURNSTILE_RELAY_SIGNAL_PIN, HIGH);
    digitalWrite(TURNSTILE_RELAY_NOT_SIGNAL_PIN, LOW);
  }
}
