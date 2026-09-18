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
  // Fallback: If charger IC floats line to >= 4200mV
  uint16_t mv = getBatteryMilliVolts();
  return (mv >= 4200);
}

bool isBatteryConnected(void){
#if defined(PIN_BAT_ADC)
  // Read 16 samples to compute stable average voltage
  uint32_t sum = 0;
  for(int i = 0; i < 16; i++){
    sum += (uint16_t)(analogReadMilliVolts(PIN_BAT_ADC) * 2);
    delayMicroseconds(200);
  }
  const uint16_t avg = (uint16_t)(sum / 16);

  // If voltage is under 2200mV, rail is unpowered or floating with no battery
  if(avg < 2200) return false;

  const bool plugged = isPowerPlugged();
  if(!plugged){
    // Running solely on battery power: if ESP32 is executing code, battery is present
    return true;
  }

  // When plugged into USB power:
  // If voltage is clamped below 4100mV, a physical LiPo battery is connected and drawing charge.
  // (An open charger with only a 10uF cap floats at ~4.20V-4.26V and cannot sit steadily below 4.10V).
  if(avg < 4100){
    return true;
  }

#if defined(SEEDER_BOARD_TDISPLAY_S3)
  // Voltage is >= 4100mV (could be a fully charged Li-ion battery OR an open 10uF capacitor).
  // Test capacitance with a 30ms 42uA discharge pulse through the top 100k divider resistor:
  pinMode(PIN_BAT_ADC, OUTPUT);
  digitalWrite(PIN_BAT_ADC, LOW);
  delay(30);
  pinMode(PIN_BAT_ADC, INPUT);
  delayMicroseconds(500);
  const uint16_t vAfter = (uint16_t)(analogReadMilliVolts(PIN_BAT_ADC) * 2);

  // An open 10uF capacitor plummets by > 600mV (typically > 1300mV).
  // A chemical battery cell (thousands of Farads equivalent) drops 0mV (noise < 80mV).
  if((int)avg - (int)vAfter > 250){
    return false; // Fast capacitor discharge -> No battery connected
  }
  return true;
#else
  return (avg < 4200);
#endif

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





