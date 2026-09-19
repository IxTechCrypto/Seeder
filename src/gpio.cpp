#include "GlobalVARS.h"
#include "gpio.h"
#include "workflow.h"
#include "ui/ui.h"
#include <TFT_eSPI.h> // Graphics and font library for ST7789 driver chip

/**********************🍃 GLOBAL Vars *******************************/
TFT_eSPI tft = TFT_eSPI();  // Invoke library, pins defined in User_Setup.h
extern sWallet myWallet;
extern sButton btnMove;
extern sButton btnSelect;

/*****************🍃 TFT WORK *********************/

void Init_TFT(void){

#ifdef PIN_POWER_ON
  /* La T-Display-S3 alimenta sus periféricos desde este pin. Si no se pone
     alto ANTES de arrancar el panel, la pantalla no enciende y la placa
     parece muerta: es el fallo clásico de esa placa. */
  gpio_hold_dis((gpio_num_t)PIN_POWER_ON);
  gpio_deep_sleep_hold_dis();
  pinMode(PIN_POWER_ON, OUTPUT);
  digitalWrite(PIN_POWER_ON, HIGH);
  delay(20);
#endif

  tft.init();
  tft.setRotation(1);
  tft.setSwapBytes(true);   // orden de bytes al volcar imágenes

  ui::splash();

  myWallet.entropySrc = coinEntropy;
  drawOrientationMenu();
}

/*****************🍃 BUTTON DETECTION *********************/

sButton::sButton(byte bPin){        //Constructor
    pin = bPin; pinMode(pin, INPUT);
    antState = HIGH; longFired = holdFired = false;
    msecLst = msecEdge = 0; clickState = None;
}
void sButton::init(void){  pinMode(pin, INPUT); }     // Init pushbutton pin
void sButton::setPin(byte bPin){
    pin = bPin;
    pinMode(pin, INPUT);
    antState = digitalRead(pin);
    longFired = holdFired = false;
    msecLst = msecEdge = 0;
    clickState = None;
}
int sButton::click(void){  return clickState; }
void sButton::forceClick(void){ clickState = ForcedClick;} //Generates one click loop
void sButton::reset(void){
    antState = digitalRead(pin);
    msecLst = 0;
    msecEdge = millis();
    longFired = true;
    holdFired = true;
    clickState = None;
}

void setButtonOrientation(bool leftHanded){
    if(leftHanded){
        btnMove.setPin(PIN_SELECT);
        btnSelect.setPin(PIN_MOVE);
    }else{
        btnMove.setPin(PIN_MOVE);
        btnSelect.setPin(PIN_SELECT);
    }
}

//Cuanto lleva pulsado ahora mismo. Cero significa suelto, asi que sirve
//igual para dibujar el progreso de un mantenido y para saber si sigue ahi.
unsigned long sButton::heldMs(void){
    if(!msecLst) return 0;
    const unsigned long h = millis() - msecLst;
    return h ? h : 1;               //0 esta reservado para "suelto"
}

void sButton::check(void)
{
    const unsigned long ButDebounce  = 25;
          unsigned long msec = millis();

    if(clickState == ForcedClick){ clickState = SingleClick; return; }
    clickState = None;

    byte but = digitalRead(pin);

    if(but != antState){
        resetInactivityTimer();
        if(msec - msecEdge < ButDebounce) return;   // bounce, ignore the edge
        msecEdge = msec;
        antState = but;

        if(but == LOW){                             // pressed
            msecLst = msec ? msec : 1;
            longFired = holdFired = false;
        }else{                                      // released
            //Click reported on release, so holding the button never turns two
            //presses into one and no input is ever swallowed
            if(msecLst && !longFired){ clickState = SingleClick; DBGLN("SingleClick"); }
            msecLst = 0;
        }
        return;
    }

    //Still held: LongClick fires once and suppresses the click on release.
    //HoldClick comes later on that same press, so a screen armed by LongClick
    //has something to fill up to and letting go still backs out of it.
    if(but != LOW || !msecLst) return;
    const unsigned long held = msec - msecLst;

    if(!longFired && held > BTN_LONG_MS){
        longFired = true;
        clickState = LongClick;
        DBGLN("LongClick");
    }else if(longFired && !holdFired && held > BTN_HOLD_MS){
        holdFired = true;
        clickState = HoldClick;
        DBGLN("HoldClick");
    }
}

/*****************🍃 POWER / BATTERY MEASUREMENT *********************/

#if defined(SEEDER_BOARD_TDISPLAY_S3)
#include "HWCDC.h"
#endif

static uint32_t s_lastBatCheck = 0;
static bool     s_cachedHasBat = true;
static uint8_t  s_batDebounceCount = 0;

uint16_t getBatteryMilliVolts(void){
#if defined(PIN_BAT_ADC)
  uint32_t sum = 0;
  for(int i = 0; i < 8; i++){
    sum += analogReadMilliVolts(PIN_BAT_ADC);
    delayMicroseconds(50);
  }
  return (uint16_t)((sum / 8) * 2);
#else
  return 0;
#endif
}

bool isPowerPlugged(void){
#if defined(SEEDER_BOARD_TDISPLAY_S3)
  // When connected to a USB host (PC), ESP32-S3 receives SOF frames via HWCDC
  if(HWCDC::isPlugged()){
    return true;
  }
#endif
  // Fallback (e.g. wall charger / power bank): charger pulls line high
  uint16_t mv = getBatteryMilliVolts();
  return (mv >= 4220);
}

bool isBatteryConnected(void){
#if defined(PIN_BAT_ADC)
  const uint32_t now = millis();

  // Rate-limit hardware sampling to 1 Hz
  if(s_lastBatCheck != 0 && (now - s_lastBatCheck < 1000)){
    return s_cachedHasBat;
  }

  // Sample multiple times across 14ms to measure average and ripple
  uint16_t vMin = 65535;
  uint16_t vMax = 0;
  uint32_t sum = 0;

  for(int i = 0; i < 8; i++){
    uint16_t v = (uint16_t)(analogReadMilliVolts(PIN_BAT_ADC) * 2);
    sum += v;
    if(v < vMin) vMin = v;
    if(v > vMax) vMax = v;
    delayMicroseconds(1800);
  }
  const uint16_t avg = (uint16_t)(sum / 8);
  const uint16_t ripple = vMax - vMin;

  bool rawDetected = false;
  const bool plugged = isPowerPlugged();

  if(!plugged){
    // Running solely on battery power: if code is executing without USB, battery is present
    rawDetected = (avg >= 2400);
  } else {
    // When plugged into USB power:
    // A physical Li-ion cell has huge capacitance and clamps rail steadily (< 45mV ripple)
    // An open charger circuit without a battery oscillates with high ripple or floats > 4250mV
    if(avg >= 2400 && avg <= 4250 && ripple < 55){
      rawDetected = true;
    } else if(avg < 4140){
      // Under active charging, battery voltage is solidly below 4.14V
      rawDetected = true;
    } else {
      rawDetected = false;
    }
  }

  // Instant on first check; 2-sample debounced on subsequent transitions
  if(s_lastBatCheck == 0){
    s_cachedHasBat = rawDetected;
  } else if(rawDetected != s_cachedHasBat){
    s_batDebounceCount++;
    if(s_batDebounceCount >= 2){
      s_cachedHasBat = rawDetected;
      s_batDebounceCount = 0;
    }
  } else {
    s_batDebounceCount = 0;
  }

  s_lastBatCheck = now;
  return s_cachedHasBat;
#else
  return false;
#endif
}

uint8_t getBatteryPercent(void){
  uint16_t mv = getBatteryMilliVolts();
  if(mv >= 4150) return 100;
  if(mv <= 3400) return 0;
  return (uint8_t)((mv - 3400) * 100 / (4150 - 3400));
}

/*****************🍃 POWER MANAGEMENT & DEEP SLEEP *********************/
#include "esp_sleep.h"
#include "driver/rtc_io.h"

static uint32_t s_lastActivityMs = 0;
static uint32_t s_dualHoldStart  = 0;
static bool     s_dualHoldArmed  = false;

void resetInactivityTimer(void){
  s_lastActivityMs = millis();
}

static void configureWakeupTriggers(void){
  pinMode(PIN_MOVE, INPUT);
  pinMode(PIN_SELECT, INPUT);

#if defined(SEEDER_BOARD_TDISPLAY_S3)
  // On ESP32-S3: GPIO 14 (PIN_MOVE) has internal pull-up, GPIO 0 (PIN_SELECT) has external pull-up
  rtc_gpio_pullup_en((gpio_num_t)PIN_MOVE);
  rtc_gpio_pulldown_dis((gpio_num_t)PIN_MOVE);
  rtc_gpio_pullup_en((gpio_num_t)PIN_SELECT);
  rtc_gpio_pulldown_dis((gpio_num_t)PIN_SELECT);
  const uint64_t wakeMask = (1ULL << PIN_MOVE) | (1ULL << PIN_SELECT);
  esp_sleep_enable_ext1_wakeup(wakeMask, ESP_EXT1_WAKEUP_ANY_LOW);
#else
  // Classic ESP32: GPIO 35 and GPIO 0 both have external pull-ups on TTGO T-Display board
  const uint64_t wakeMask = (1ULL << PIN_MOVE) | (1ULL << PIN_SELECT);
  esp_sleep_enable_ext1_wakeup(wakeMask, ESP_EXT1_WAKEUP_ALL_LOW);
#endif
}

static void enterDeepSleepFast(void){
#if defined(PIN_POWER_ON)
  digitalWrite(PIN_POWER_ON, LOW);
  gpio_hold_en((gpio_num_t)PIN_POWER_ON);
  gpio_deep_sleep_hold_en();
#endif
  configureWakeupTriggers();
  esp_deep_sleep_start();
}

void powerOffDevice(void){
  // 1. Play sleek Tron power down animation
  ui::playPowerDownAnimation();

  // 2. Put display controller into low power sleep mode
  tft.writecommand(0x10); // ST7789_SLPIN
  tft.writecommand(0x28); // ST7789_DISPOFF
  delay(100);

  // 3. Cut peripheral & backlight power
#if defined(PIN_POWER_ON)
  pinMode(PIN_POWER_ON, OUTPUT);
  digitalWrite(PIN_POWER_ON, LOW);
  gpio_hold_en((gpio_num_t)PIN_POWER_ON);
  gpio_deep_sleep_hold_en();
#endif
#if defined(TFT_BL)
  pinMode(TFT_BL, OUTPUT);
  digitalWrite(TFT_BL, LOW);
#endif

  // 4. Configure wake triggers and enter deep sleep
  configureWakeupTriggers();
  esp_deep_sleep_start();
}

bool checkWakeupOrSleepAgain(void){
  // Always unhold power pins on boot
#if defined(PIN_POWER_ON)
  gpio_hold_dis((gpio_num_t)PIN_POWER_ON);
  gpio_deep_sleep_hold_dis();
#endif

  const esp_sleep_wakeup_cause_t cause = esp_sleep_get_wakeup_cause();

  // If not woken by button press (e.g. cold power-on, reset button, USB plug-in): boot normally
  if(cause != ESP_SLEEP_WAKEUP_EXT1){
    resetInactivityTimer();
    return true;
  }

  // Woken by EXT1 button trigger: verify dual-button hold for 1.5 seconds
  pinMode(PIN_MOVE, INPUT);
  pinMode(PIN_SELECT, INPUT);
#if defined(SEEDER_BOARD_TDISPLAY_S3)
  pinMode(PIN_MOVE, INPUT_PULLUP);
  pinMode(PIN_SELECT, INPUT_PULLUP);
#endif

  // Grace period: allow up to 250ms for the second finger to contact
  const uint32_t graceStart = millis();
  bool bothLow = false;
  while(millis() - graceStart < 250){
    if(digitalRead(PIN_MOVE) == LOW && digitalRead(PIN_SELECT) == LOW){
      bothLow = true;
      break;
    }
    delay(5);
  }

  if(!bothLow){
    // Single accidental button bump in pocket/bag: abort and return to deep sleep
    enterDeepSleepFast();
    return false;
  }

  // Both buttons are LOW: verify they remain held continuously for 1500 ms
  const uint32_t holdStart = millis();
  uint8_t highDebounce = 0;
  while(millis() - holdStart < 1500){
    if(digitalRead(PIN_MOVE) == HIGH || digitalRead(PIN_SELECT) == HIGH){
      highDebounce++;
      if(highDebounce >= 4){ // ~40ms confirmed release
        // Released prematurely: return to deep sleep
        enterDeepSleepFast();
        return false;
      }
    } else {
      highDebounce = 0;
    }
    delay(10);
  }

  // Power-on confirmed! Wait for release to avoid spurious initial clicks
  while(digitalRead(PIN_MOVE) == LOW || digitalRead(PIN_SELECT) == LOW){
    delay(20);
  }

  resetInactivityTimer();
  return true;
}

void checkDualButtonPowerOff(void){
  const byte moveState = digitalRead(PIN_MOVE);
  const byte selState  = digitalRead(PIN_SELECT);

  if(moveState == LOW && selState == LOW){
    const uint32_t now = millis();
    if(s_dualHoldStart == 0){
      s_dualHoldStart = now;
      s_dualHoldArmed = false;
    }

    const uint32_t elapsed = now - s_dualHoldStart;

    if(elapsed >= 300){
      s_dualHoldArmed = true;
      btnMove.reset();
      btnSelect.reset();
      ui::drawPowerOffProgress((uint16_t)elapsed, 2000);

      if(elapsed >= 2000){
        // Hold reached 2.0s -> initiate shutdown!
        s_dualHoldStart = 0;
        s_dualHoldArmed = false;
        powerOffDevice();
      }
    }
  } else {
    // Either or both buttons released
    if(s_dualHoldArmed){
      // Released before 2.0s: cancel power-off overlay and restore screen
      btnMove.reset();
      btnSelect.reset();
      ui::cancelPowerOffProgress();
    }
    s_dualHoldStart = 0;
    s_dualHoldArmed = false;
  }
}

void checkInactivityAutoSleep(void){
  if(s_lastActivityMs == 0){
    s_lastActivityMs = millis();
    return;
  }
  // 3 minutes inactivity threshold
  if(millis() - s_lastActivityMs >= (3UL * 60UL * 1000UL)){
    powerOffDevice();
  }
}





