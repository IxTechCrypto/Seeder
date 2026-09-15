#pragma once
#include <Arduino.h>

/**********🍃 WORKFLOW FUNCTIONS ****************/
void doOrientation(void);
void doInitMenu(void);
void doMenuWords(void);
void doShowSeed(void);
void doCoinSeed(void);
void doDiceSeed(void);
void drawOrientationMenu(bool animate = false);
void drawInitMenu(bool animate = false);
void drawWordsMenu(bool animate = false);
