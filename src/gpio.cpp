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





