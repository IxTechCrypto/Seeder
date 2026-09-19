#include <Arduino.h>
#include "gpio.h"
#include "btc.h"
#include "workflow.h"
#include "GlobalVARS.h"
#include "ui/ui.h"

sWallet myWallet;
sButton btnMove(PIN_MOVE);
sButton btnSelect(PIN_SELECT);
  
#include "esp_core_dump.h"

void setup() {
  // Early verification: if woken by sleep wake trigger, verify dual-button 1.5s hold, else sleep immediately
  if(!checkWakeupOrSleepAgain()){
    return;
  }

  // Asegurar que cualquier residuo previo de coredump en flash quede borrado
  esp_core_dump_image_erase();


#if SEEDER_DEBUG
  Serial.begin(SERIAL_BAUD);                  // UART only exists in debug builds
#endif
  Init_TFT();                                   // Init TFT wallet
  myWallet.State = STATE_ORIENTATION;
}


void loop() {
  
  while(true){
    /***** Check power management (dual button hold & inactivity sleep) ******/
    checkDualButtonPowerOff();
    checkInactivityAutoSleep();

    /***** Check button state ******/
    btnMove.check();
    btnSelect.check();

    /***** Print menu options ***********/
    switch(myWallet.State){
      case STATE_ORIENTATION:   doOrientation(); break;
      case STATE_INITMENU:      doInitMenu(); break;
      case STATE_WORDS:        doMenuWords(); break;
      case STATE_SEED:        doShowSeed(); break;
      case STATE_COINSEED:    doCoinSeed(); break;
      case STATE_DICESEED:    doDiceSeed(); break;
    }
    ui::tickPower();
    delay(10);
  }
}
