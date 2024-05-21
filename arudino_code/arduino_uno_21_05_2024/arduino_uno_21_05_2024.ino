#define TURNSTILE_ON_TIME_MS 3500
#define COMMUNICATION_TIMEOUT_MS 10000
#define TURNSTILE_ON_CHAR '1'

#define TURNSTILE_IS_ACTIVATED_IF_HIGH true  // when the output is low, turnstiles are activated so that if power is off, turnstiles are not blocked. 
#define TURNSTILE_SIGNAL_PIN 13               //if HIGH, turnstiles are blocked, otherwise turnstiles are activated

unsigned long last_time_communication_ms = 0;
unsigned long last_time_turnstile_activated = 0;

void setup() {
  Serial.begin(9600);
  pinMode(TURNSTILE_SIGNAL_PIN, OUTPUT);
  activate_turnstile();
}

void loop() {

  //=============================================================================
  // set whether turnstile is activated or not
  if ((millis() - last_time_communication_ms) > COMMUNICATION_TIMEOUT_MS) {
    activate_turnstile();  // If miru does not send any command from the serial, keep turnstile activated
  } else if ((millis() - last_time_turnstile_activated) < TURNSTILE_ON_TIME_MS) {
    activate_turnstile();  //If miru sent activate turnstile command recently, keep turnstile activated
  } else {
    block_turnstile();
  }

  //=============================================================================
  //check for the serial data sent by the miru
  if (Serial.available()) {
    last_time_communication_ms = millis();
    char c = Serial.read();

    if (c == 'i') {  // send a reply so that the computer knows this is the arduino port
      Serial.println("THIS_IS_ARDUINO");
    } else if (c == '1') {
      last_time_turnstile_activated = millis();
      Serial.println("ECHO_1");
    } else if (c=='0'){
      Serial.println("ECHO_0");
    }
  }
}

void activate_turnstile() {
  if (TURNSTILE_IS_ACTIVATED_IF_HIGH) {
    digitalWrite(TURNSTILE_SIGNAL_PIN, HIGH);
  } else {
    digitalWrite(TURNSTILE_SIGNAL_PIN, LOW);
  }
}

void block_turnstile() {
  if (TURNSTILE_IS_ACTIVATED_IF_HIGH) {
    digitalWrite(TURNSTILE_SIGNAL_PIN, LOW);
  } else {
    digitalWrite(TURNSTILE_SIGNAL_PIN, HIGH);
  }
}
