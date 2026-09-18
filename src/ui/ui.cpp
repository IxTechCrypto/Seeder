#include <Arduino.h>
#include <TFT_eSPI.h>
#include "theme.h"
#include "ui.h"
#include "../gpio.h"
#include "../Lib/images.h"
#include "../Lib/Free_Fonts.h"
#include "../qrcoded.h"
#include "brand.h"
#include "tactical_icons.h"
#include "ixtech_logo.h"
#include "utility/trezor/memzero.h"
#if !defined(SEEDER_BOARD_TDISPLAY_S3)
  #include "../Lib/images_splash85.h"
#endif

extern TFT_eSPI tft;

/* Los bitmaps del splash no escalan con la placa, asi que cada una usa el suyo:
   a tamano nativo el grupo se comia los 135 px de la pequena y dejaba los
   creditos pegados al borde. En la S3 caben de sobra sin tocar. */
#if defined(SEEDER_BOARD_TDISPLAY_S3)
  #define SPLASH_LOGO    uBitcoinLogo
  #define SPLASH_LOGO_W  logouBTCWidth
  #define SPLASH_LOGO_H  logouBTCHeight
  #define SPLASH_PW      powered_logo
  #define SPLASH_PW_W    poweredWidth
  #define SPLASH_PW_H    poweredHeight
  #define IXTECH_LOGO    ixtech_logo_s3
  #define IXTECH_LOGO_W  ixtech_logo_s3_w
  #define IXTECH_LOGO_H  ixtech_logo_s3_h
  #define IXTECH_TXT     ixtech_text_logo_s3
  #define IXTECH_TXT_W   ixtech_text_logo_s3_w
  #define IXTECH_TXT_H   ixtech_text_logo_s3_h
#else
  #define SPLASH_LOGO    uBitcoinLogoS
  #define SPLASH_LOGO_W  logouBTCSWidth
  #define SPLASH_LOGO_H  logouBTCSHeight
  #define SPLASH_PW      powered_logoS
  #define SPLASH_PW_W    poweredSWidth
  #define SPLASH_PW_H    poweredSHeight
  #define IXTECH_LOGO    ixtech_logo
  #define IXTECH_LOGO_W  ixtech_logo_w
  #define IXTECH_LOGO_H  ixtech_logo_h
  #define IXTECH_TXT     ixtech_text_logo
  #define IXTECH_TXT_W   ixtech_text_logo_w
  #define IXTECH_TXT_H   ixtech_text_logo_h
#endif

namespace ui {

static bool g_leftHanded = false;
void setHandedness(bool leftHanded){
  g_leftHanded = leftHanded;
  tft.setRotation(g_leftHanded ? 3 : 1);
}
bool isLeftHanded(void){ return g_leftHanded; }

/*==============================================================
  PIEZAS
==============================================================*/

/* Fuente 5x7 integrada. Se dibuja carácter a carácter para poder
   espaciarla: las versalitas necesitan aire o se leen como un bloque. */
void tiny(const char *s, int x, int y, uint16_t col, char datum, int sp, uint8_t size){
  const int n  = strlen(s);
  const int adv = UI_TINY_W * size + sp;
  const int w  = n * adv - sp;
  int px = x;
  if(datum == 'C')      px = x - w/2;
  else if(datum == 'R') px = x - w;
  tft.setTextFont(1);
  tft.setTextSize(size);
  tft.setTextColor(col, UI_BG);
  for(int i=0; i<n; i++){ tft.drawChar(s[i], px, y, 1); px += adv; }
  tft.setTextSize(1);
}
static void tiny(const String &s, int x, int y, uint16_t col, char datum='L', int sp=0, uint8_t size=1){
  tiny(s.c_str(), x, y, col, datum, sp, size);
}

/* Cuerpo grande: lo que el usuario tiene que copiar a mano */
static void bigLine(const char *s, int y, uint16_t col){
  tiny(s, UI_M, y, col, 'L', 0, UI_BIG_BODY);
}

/* Cara del dado por su valor: los puntos salen de una máscara sobre la
   rejilla 3x3, así una sola función sirve para el menú y para la captura. */
void die(int x, int y, int s, uint8_t value, uint16_t col){
  static const uint16_t FACE[6] = { 0x010, 0x101, 0x111, 0x145, 0x155, 0x16D };
  if(value < 1 || value > 6) return;

  /* radio de esquina /8, no /6: a radios grandes el arco de TFT_eSPI escalona */
  const int r = max(2, s/8), pip = max(1, s/10);
  tft.fillRoundRect(x, y, s, s, r, UI_BG);
  tft.drawRoundRect(x, y, s, s, r, col);
  if(s >= 32) tft.drawRoundRect(x+1, y+1, s-2, s-2, r-1, col);

  /* 0.22 / 0.50 / 0.78 del lado, no 1/6 / 3/6 / 5/6: los de las esquinas
     se iban al borde y ensuciaban la cara */
  const uint16_t face = FACE[value-1];
  for(int i=0; i<9; i++){
    if(!(face & (1 << i))) continue;
    tft.fillCircle(x + (s*(22 + 28*(i%3)))/100, y + (s*(22 + 28*(i/3)))/100, pip, col);
  }
}

/* Moneda de canto: cara elíptica a la izquierda y el canto a la derecha con
   sus estrías. Dibujada entera, así se tiñe igual que el dado y no depende
   de reducir un bitmap, que a este tamaño quedaba embarrado. */
void coin(int x, int y, int s, uint16_t col){
  const int rx = s/4, ry = s/2 - 2, dep = s/3;
  const int cx = x + rx + 1, cy = y + s/2;

  tft.drawEllipse(cx, cy, rx, ry, col);              //cara

  int prev = -1;                                     //borde exterior del canto
  for(int j = -ry; j <= ry; j++){
    const int w = (int)(rx * sqrtf(fmaxf(0.0f, 1.0f - (float)(j*j)/(float)(ry*ry))) + 0.5f);
    if(prev >= 0 && abs(w - prev) > 1){              //cerrar el escalón
      for(int q = min(w,prev); q <= max(w,prev); q++) tft.drawPixel(cx+dep+q, cy+j, col);
    }else tft.drawPixel(cx+dep+w, cy+j, col);
    prev = w;
  }
  tft.drawFastHLine(cx, cy-ry, dep+1, col);          //tapas
  tft.drawFastHLine(cx, cy+ry, dep+1, col);

  for(int k = -3; k <= 3; k++){                      //estrías
    const int j = (k*ry)/4;
    const int w = (int)(rx * sqrtf(fmaxf(0.0f, 1.0f - (float)(j*j)/(float)(ry*ry))) + 0.5f);
    tft.drawFastHLine(cx+w, cy+j, dep, col);
  }
}

/* El triángulo del bitmap original trae una fila punteada encima. Dibujado
   con primitivas no hay puntos sueltos y se puede teñir a cualquier nivel. */
void caret(int cx, int y, int w, int h, uint16_t col){
  tft.fillTriangle(cx - w/2, y, cx + w/2, y, cx, y + h, col);
}

void bar(int x, int y, int w, int h, float frac){
  if(frac < 0) frac = 0;
  if(frac > 1) frac = 1;
  tft.fillRect(x, y, w, h, UI_TRACK);
  tft.fillRect(x, y, (int)(w * frac + 0.5f), h, UI_ACCENT);
}

/* Raíl táctico: alineado con los botones físicos según la orientación */
static void rail(const char *topAct, const char *botAct, bool showKeys){
  const int railW  = UI_W - UI_RAIL_X;
  const int lineX  = g_leftHanded ? railW : UI_RAIL_X;
  const int railCX = g_leftHanded ? (railW / 2) : UI_RAIL_CX;

  tft.drawFastVLine(lineX, 0, UI_H, UI_TRACK);
  caret(railCX, SY(12), SX(9), SY(6), UI_DIM);
  if(showKeys){
    tiny("MOVE", railCX, UI_RAIL_TOP_Y,        UI_ACCENT, 'C', 1);
    tiny(topAct, railCX, UI_RAIL_TOP_Y+SY(10), UI_DIM,    'C', 0);
    tiny("OK",   railCX, UI_RAIL_BOT_Y,        UI_ACCENT, 'C', 1);
    tiny(botAct, railCX, UI_RAIL_BOT_Y+SY(10), UI_DIM,    'C', 0);
  }else{
    tiny(topAct, railCX, UI_RAIL_TOP_Y+SY(4),  UI_ACCENT, 'C', 1);
    tiny(botAct, railCX, UI_RAIL_BOT_Y+SY(4),  UI_ACCENT, 'C', 1);
  }
  caret(railCX, SY(124), SX(9), SY(-6), UI_DIM);
}

static int s_pwrX = -1;
static int s_pwrY = -1;
static uint16_t s_pwrFg = UI_TEXT;
static uint16_t s_pwrBg = UI_BG;
static uint8_t s_animFrame = 0;
static uint32_t s_lastAnimTick = 0;
static bool s_wasPlugged = false;
static bool s_wasHasBat = false;

static void drawBatteryInterior(int x, int y, uint8_t bars, uint16_t segCol, uint16_t bgCol){
  tft.fillRect(x + 3, y + 3, 22, 10, bgCol);
  if(bars >= 1){
    tft.fillRoundRect(x + 4, y + 4, 6, 8, 1, segCol);
  }
  if(bars >= 2){
    tft.fillRoundRect(x + 11, y + 4, 6, 8, 1, segCol);
  }
  if(bars >= 3){
    tft.fillRoundRect(x + 18, y + 4, 6, 8, 1, segCol);
  }
}

void drawPower(int x, int y, uint16_t fgCol, uint16_t bgCol){
  s_pwrX = x;
  s_pwrY = y;
  s_pwrFg = fgCol;
  s_pwrBg = bgCol;

  const bool plugged = isPowerPlugged();
  const bool hasBat  = isBatteryConnected();
  s_wasPlugged = plugged;
  s_wasHasBat  = hasBat;

  // Clear outer bounding area (34px wide x 16px high)
  tft.fillRect(x, y, 34, 16, bgCol);

  if(plugged && !hasBat){
    // STATE 1: USB-C only (NO battery attached) -> Modern bold Plug icon
    // Two bold prongs (3px thick, 6px long)
    tft.fillRect(x,     y + 2, 6, 3, fgCol);
    tft.fillRect(x,     y + 11, 6, 3, fgCol);
    // Plug body with rounded corners (12x14 block)
    tft.fillRoundRect(x + 6, y + 1, 12, 14, 3, fgCol);
    // Sleek dual vertical notches in contrasting background color
    tft.drawFastVLine(x + 10, y + 4, 8, bgCol);
    tft.drawFastVLine(x + 13, y + 4, 8, bgCol);
    // Strain relief collar & cord
    tft.fillRect(x + 18, y + 5, 3, 6, fgCol);
    tft.fillRect(x + 21, y + 6, 6, 4, fgCol);
  } else if(plugged && hasBat){
    // STATE 2: USB-C + Battery connected -> Battery charging animation
    // Bold 2-pixel outer rounded shell
    tft.drawRoundRect(x,     y,     27, 16, 4, fgCol);
    tft.drawRoundRect(x + 1, y + 1, 25, 14, 3, fgCol);
    // Positive terminal pip (smooth rounded)
    tft.fillRoundRect(x + 27, y + 4, 4, 8, 2, fgCol);

    const uint16_t segCol = (bgCol == UI_ACCENT) ? fgCol : UI_ACCENT;
    const uint8_t bars = (s_animFrame >= 4) ? 3 : s_animFrame;
    drawBatteryInterior(x, y, bars, segCol, bgCol);
  } else {
    // STATE 3: Running on battery alone (no USB) -> Modern segmented Battery gauge
    tft.drawRoundRect(x,     y,     27, 16, 4, fgCol);
    tft.drawRoundRect(x + 1, y + 1, 25, 14, 3, fgCol);
    tft.fillRoundRect(x + 27, y + 4, 4, 8, 2, fgCol);

    const uint8_t pct = getBatteryPercent();

    uint16_t segCol;
    if(pct <= 20){
      segCol = 0xF800; // Alert Red
    } else if(pct <= 45){
      segCol = 0xFFE0; // Amber / Yellow
    } else {
      segCol = (bgCol == UI_ACCENT) ? fgCol : UI_ACCENT; // Clean theme green / dark
    }

    uint8_t staticBars = 0;
    if(pct > 5)  staticBars = 1;
    if(pct >= 35) staticBars = 2;
    if(pct >= 70) staticBars = 3;
    drawBatteryInterior(x, y, staticBars, segCol, bgCol);
  }
}

void tickPower(void){
  if(s_pwrX < 0 || s_pwrY < 0) return;

  const uint32_t now = millis();
  const bool plugged = isPowerPlugged();
  const bool hasBat  = isBatteryConnected();

  if(plugged != s_wasPlugged || hasBat != s_wasHasBat){
    s_wasPlugged = plugged;
    s_wasHasBat  = hasBat;
    s_animFrame = 0;
    s_lastAnimTick = now;
    drawPower(s_pwrX, s_pwrY, s_pwrFg, s_pwrBg);
    return;
  }

  if(plugged && hasBat){
    // Update charging animation every 300ms: 0 -> 1 -> 2 -> 3 -> hold 3 -> loop
    if(now - s_lastAnimTick >= 300){
      s_lastAnimTick = now;
      s_animFrame = (s_animFrame + 1) % 5;
      const uint16_t segCol = (s_pwrBg == UI_ACCENT) ? s_pwrFg : UI_ACCENT;
      const uint8_t bars = (s_animFrame >= 4) ? 3 : s_animFrame;
      drawBatteryInterior(s_pwrX, s_pwrY, bars, segCol, s_pwrBg);
    }
  } else {
    // When running on battery or static USB plug, refresh level every 5 seconds
    if(now - s_lastAnimTick >= 5000){
      s_lastAnimTick = now;
      drawPower(s_pwrX, s_pwrY, s_pwrFg, s_pwrBg);
    }
  }
}

static void eyebrow(const char *s){
  const int m = g_leftHanded ? (UI_W - UI_RAIL_X + UI_M) : UI_M;
  tft.fillRoundRect(m, SY(5), SX(3), SY(11), 1, UI_ACCENT);
  tiny(s, m + SX(7), SY(7), UI_ACCENT, 'L', 1);
  const int pwrX = g_leftHanded ? (UI_W - UI_M - SX(36)) : (UI_RAIL_X - SX(38));
  drawPower(pwrX, SY(3), UI_TEXT, UI_BG);
}

/* Número grande: el único elemento a voz alta de la pantalla */
static int bigNumber(int n, int baselineY){
  char buf[8]; snprintf(buf, sizeof(buf), "%d", n);
  const int startX = g_leftHanded ? (UI_W - UI_RAIL_X + UI_M) : UI_M;
  tft.fillRect(startX, baselineY-36, SX(100), 40, UI_BG);   //alto por la fuente, ancho por la placa
  tft.setFreeFont(FMB24);
  tft.setTextColor(UI_TEXT);
  tft.setCursor(startX, baselineY);
  tft.print(buf);
  return tft.getCursorX();
}

/* Cabecera de las pantallas de semilla: etiqueta, paso y una regla fina táctica. */
static void head(const char *title, uint8_t step, uint8_t total){
  tft.fillScreen(UI_BG);
  tft.fillRoundRect(UI_M, SY(5), SX(3), SY(11), 1, UI_ACCENT);
  tiny(title, UI_M + SX(7), SY(7), UI_ACCENT, 'L', 1);
  if(total){
    char b[8]; snprintf(b, sizeof(b), "%u/%u", step, total);
    tiny(b, UI_W-UI_M, SY(7), UI_DIM, 'R', 0);
  }
  drawPower(UI_W - UI_M - (total ? SX(68) : SX(36)), SY(3), UI_TEXT, UI_BG);
  tft.drawFastHLine(UI_M, SY(18), UI_W - 2*UI_M, UI_TRACK);
}

/* Cuerpo de texto. Una sola tipografía por pantalla: o toda pequeña o toda
   FreeMono. UI_BODY_TINY decide cuál, para poder compararlo en la placa. */
#if UI_BODY_TINY
  #define BODY_LH   SY(14)
  #define BODY_CPL  UI_TINY_CPL
  static void bodyLine(const String &s, int y, uint16_t col){ tiny(s, UI_M, y, col, 'L', 0); }
#else
  #define BODY_LH   SY(18)
  #define BODY_CPL  UI_MONO_CPL
  static void bodyLine(const String &s, int y, uint16_t col){
    tft.setFreeFont(FM9); tft.setTextColor(col, UI_BG);
    tft.setCursor(UI_M, y); tft.print(s);
  }
#endif

/* Dibuja un destello de luz especular diagonal que recorre una imagen en PROGMEM.
   Solo ilumina los píxeles propios del bitmap (los 0x0000 de fondo se respetan),
   creando un reflejo metálico brillante de 60 FPS sin parpadeo. */
static void renderShimmer(int x, int y, int w, int h, const unsigned short *src, int beamPos, int beamW){
  static uint16_t buf[160 * 32];
  if(w * h > (int)(sizeof(buf)/sizeof(buf[0]))) return;

  for(int j = 0; j < h; j++){
    const int row = j * w;
    const int yDiag = (j * 11) / 10;
    for(int i = 0; i < w; i++){
      const uint16_t c = pgm_read_word(&src[row + i]);
      if(c == 0x0000){
        buf[row + i] = 0x0000;
        continue;
      }
      const int dist = abs(i + yDiag - beamPos);
      if(dist <= 2){
        buf[row + i] = 0xFFFF; // Núcleo blanco incandescente
      } else if(dist <= beamW){
        const int factor = beamW - dist;
        const int denom  = beamW - 2;
        const uint8_t r = (c >> 11) & 0x1F;
        const uint8_t g = (c >> 5)  & 0x3F;
        const uint8_t b = c & 0x1F;
        const uint8_t rN = (uint8_t)min(31, r + (14 * factor) / denom);
        const uint8_t gN = (uint8_t)min(63, g + (36 * factor) / denom);
        const uint8_t bN = (uint8_t)min(31, b + (30 * factor) / denom);
        buf[row + i] = (rN << 11) | (gN << 5) | bN;
      } else {
        buf[row + i] = c;
      }
    }
  }
  tft.pushImage(x, y, w, h, buf);
}

/*==============================================================
  PANTALLAS
==============================================================*/

void splash(void){
  s_pwrX = -1; s_pwrY = -1;
  tft.fillScreen(UI_BG);
  tft.pushImage((UI_W - seeder_splash_logo_w)/2, (UI_H - seeder_splash_logo_h)/2 - SY(8),
                seeder_splash_logo_w, seeder_splash_logo_h, seeder_splash_logo, 0x0000);
  tiny("V" SEEDER_VERSION "  " SEEDER_COMMIT, UI_W/2, UI_H - SY(15), UI_DIM, 'C', 1);
  delay(1800);

  /* Segunda pantalla: los creditos. Los dos logotipos y la linea de uBitcoin
     son bitmaps y no escalan, asi que van como un grupo -uno debajo del otro
     a distancia fija- y los creditos se anclan al borde de abajo.

     Cada nombre va bajo su preposicion en vez de en una sola fila porque
     "MADE BY BITMAKER" y "CREDITS TO LUNATICOIN" seguidos ocupan 257 px
     (111 + 146, con el sp=1 que se les pasa) y la placa pequena tiene 240,
     de los que ademas 20 son margenes: se tocarian. Partidos en dos, el
     bloque mas ancho mide 69 y sobra sitio en las dos placas. */
  tft.fillScreen(UI_BG);
  const int cr2 = UI_H - SY(9) - UI_TINY_H;     //linea de los nombres
  const int cr1 = cr2 - SY(12);                 //linea de las preposiciones

  /* El grupo se centra en la banda que queda por encima de los creditos, y no
     a una distancia fija del borde: como los bitmaps no escalan, colgarlo de
     arriba lo dejaba pegado al techo en la placa grande con un hueco muerto
     debajo. Centrado sale igual que antes en la pequena y baja solo en la S3. */
  const int grupo = SPLASH_LOGO_H + SY(6) + SPLASH_PW_H;
  const int top   = (cr1 - grupo) / 2;
  tft.pushImage((UI_W-SPLASH_LOGO_W)/2, top,
                SPLASH_LOGO_W, SPLASH_LOGO_H, SPLASH_LOGO);
  tft.pushImage((UI_W-SPLASH_PW_W)/2, top + SPLASH_LOGO_H + SY(6),
                SPLASH_PW_W, SPLASH_PW_H, SPLASH_PW);
  tiny("MADE BY",    UI_M,        cr1, UI_DIM,  'L', 1);
  tiny("BITMAKER",   UI_M,        cr2, UI_TEXT, 'L', 1);
  tiny("CREDITS TO", UI_W - UI_M, cr1, UI_DIM,  'R', 1);
  tiny("LUNATICOIN", UI_W - UI_M, cr2, UI_TEXT, 'R', 1);
  delay(2000);

  /* Tercera pantalla: mejoras de ixtech.xyz con animación Neon Shimmer */
  tft.fillScreen(UI_BG);
  const int logoX = (UI_W - IXTECH_LOGO_W)/2;
  const int logoY = SY(22);
  const int txtX  = (UI_W - IXTECH_TXT_W)/2;
  const int txtY  = SY(90);

  // Presentación inicial limpia
  tft.pushImage(logoX, logoY, IXTECH_LOGO_W, IXTECH_LOGO_H, IXTECH_LOGO);
  tiny("IMPROVEMENTS MADE BY", UI_W/2, SY(74), UI_DIM, 'C', 1);
  tft.pushImage(txtX, txtY, IXTECH_TXT_W, IXTECH_TXT_H, IXTECH_TXT);
  delay(350);

  // Fase 1: Destello de luz sobre el logotipo de la hélice
  const int logoDiagMax = IXTECH_LOGO_W + (IXTECH_LOGO_H * 11)/10 + 12;
  for(int p = -12; p <= logoDiagMax; p += 4){
    renderShimmer(logoX, logoY, IXTECH_LOGO_W, IXTECH_LOGO_H, IXTECH_LOGO, p, 9);
    delay(24);
  }
  tft.pushImage(logoX, logoY, IXTECH_LOGO_W, IXTECH_LOGO_H, IXTECH_LOGO);

  // Transición suave: pulso sutil en el subtítulo
  tiny("IMPROVEMENTS MADE BY", UI_W/2, SY(74), UI_TEXT, 'C', 1);
  delay(120);
  tiny("IMPROVEMENTS MADE BY", UI_W/2, SY(74), UI_DIM,  'C', 1);
  delay(100);

  // Fase 2: Destello metálico sobre las letras 3D ixtech.xyz
  const int txtDiagMax = IXTECH_TXT_W + (IXTECH_TXT_H * 11)/10 + 20;
  for(int p = -20; p <= txtDiagMax; p += 6){
    renderShimmer(txtX, txtY, IXTECH_TXT_W, IXTECH_TXT_H, IXTECH_TXT, p, 14);
    delay(24);
  }
  tft.pushImage(txtX, txtY, IXTECH_TXT_W, IXTECH_TXT_H, IXTECH_TXT);

  // Reposo final para contemplar el diseño antes de pasar al menú
  delay(600);
  tft.fillScreen(UI_BG);
}

/* Cabecera de marca táctica: fondo obsidiana, logotipo SEEDER naranja brillante,
   y estado de alimentación USB / Batería a la derecha. */
static void brandHead(void){
  tft.fillRect(0, 0, UI_W, UI_HEAD_H, UI_BG);
  // Logotipo SEEDER sin caja de fondo (transparente a 0x0000)
  tft.pushImage(SX(10), (UI_HEAD_H - icon_seeder_logo_h) / 2, icon_seeder_logo_w, icon_seeder_logo_h, icon_seeder_logo, 0x0000);

  // Icono de carga / batería a la derecha
  drawPower(UI_W - UI_M - SX(36), (UI_HEAD_H - 16) / 2, UI_TEXT, UI_BG);
}

/* Raíl táctico lateral con panel flotante y chevrons minimalistas del concepto */
static void thinRail(int y1, int y2, int cardH){
  const int rx = g_leftHanded ? SX(6) : (UI_MRAIL_X + SX(2));
  const int rw = UI_W - (UI_MRAIL_X + SX(2)) - SX(6);
  const int rh = (y2 + cardH) - y1;
  const int rcx = rx + rw / 2;

  tft.fillRoundRect(rx, y1, rw, rh, 6, UI_CARD_BG);
  tft.drawRoundRect(rx, y1, rw, rh, 6, UI_CARD_BOR);

  const int topCY = y1 + cardH / 2;
  const int botCY = y2 + cardH / 2;
  const int midCY = (y1 + y2 + cardH) / 2;

  // Arriba: chevron '>' alineado con botón MOVE / Tarjeta 1
  for(int i=0; i<2; i++){
    tft.drawLine(rcx - SX(3) + i, topCY - SY(6), rcx + SX(3) + i, topCY, UI_TEXT);
    tft.drawLine(rcx + SX(3) + i, topCY, rcx - SX(3) + i, topCY + SY(6), UI_TEXT);
  }

  // Centro: marca de verificación '✓' alineada con botón OK
  for(int i=0; i<2; i++){
    tft.drawLine(rcx - SX(5) + i, midCY, rcx - SX(1) + i, midCY + SY(5), UI_TEXT);
    tft.drawLine(rcx - SX(1) + i, midCY + SY(5), rcx + SX(6) + i, midCY - SY(4), UI_TEXT);
  }

  // Abajo: chevron '<' alineado con Tarjeta 2
  for(int i=0; i<2; i++){
    tft.drawLine(rcx + SX(3) - i, botCY - SY(6), rcx - SX(3) - i, botCY, UI_TEXT);
    tft.drawLine(rcx - SX(3) - i, botCY, rcx + SX(3) - i, botCY + SY(6), UI_TEXT);
  }
}

/* Geometría adaptativa para las tarjetas de menú flotantes */
static void getMenuCardLayout(int &cardX, int &cardW, int &cardH, int &y1, int &y2){
  const int railW = UI_W - (UI_MRAIL_X + SX(2)) - SX(6);
  if(g_leftHanded){
    cardX = SX(6) + railW + SX(8);
    cardW = UI_W - cardX - SX(8);
  } else {
    cardX = SX(8);
    cardW = UI_MRAIL_X - cardX - SX(8);
  }
  const int topY = UI_HEAD_H + SY(4);
  const int botY = UI_H - SY(6);
  const int gap  = SY(6);
  cardH = (botY - topY - gap) / 2;
  y1 = topY;
  y2 = topY + cardH + gap;
}

/* Renderizado de tarjeta flotante con iconos tácticos e indicadores brillantes */
static void drawMenuCard(int x, int y, int w, int h, bool sel, const char *title, const char *sub, int mode){
  // mode: 0 = Dado, 1 = Moneda, 2 = 12 Palabras, 3 = 24 Palabras
  const uint16_t bgCol = sel ? UI_CARD_BG_SEL : UI_CARD_BG;
  tft.fillRoundRect(x, y, w, h, 6, bgCol);

  if(sel){
    // Píldora vertical naranja Bitcoin brillante en el margen izquierdo
    const int pillH = h - SY(14);
    tft.fillRoundRect(x + SX(3), y + SY(6), SX(7), pillH + 2, 3, UI_ACCENT_GLOW);
    tft.fillRoundRect(x + SX(4), y + SY(7), SX(5), pillH, 2, UI_ACCENT);
    tft.drawRoundRect(x, y, w, h, 6, UI_CARD_BOR_SEL);
  } else {
    // Limpieza de cualquier halo residual y borde sutil pizarra
    tft.drawRoundRect(x - 1, y - 1, w + 2, h + 2, 7, UI_BG);
    tft.drawRoundRect(x, y, w, h, 6, UI_CARD_BOR);
  }

  // Posición del icono (36x36, dado ampliado a 32px y centrado óptimo)
  const int iconX = x + SX(14);
  const int iconY = y + (h - 36) / 2;

  if(mode == 0){ // Dado 3D isométrico
    if(sel) tft.pushImage(iconX, iconY, 36, 36, icon_dice_orange, 0x0000);
    else    tft.pushImage(iconX, iconY, 36, 36, icon_dice_dim, 0x0000);
  } else if(mode == 1){ // Moneda Bitcoin ₿
    if(sel) tft.pushImage(iconX, iconY, 36, 36, icon_coin_orange, 0x0000);
    else    tft.pushImage(iconX, iconY, 36, 36, icon_coin_silver, 0x0000);
  } else if(mode == 2){ // 12 Palabras
    if(sel) tft.pushImage(iconX, iconY, 36, 36, icon_words12_orange, 0x0000);
    else    tft.pushImage(iconX, iconY, 36, 36, icon_words12_dim, 0x0000);
  } else if(mode == 3){ // 24 Palabras
    if(sel) tft.pushImage(iconX, iconY, 36, 36, icon_words24_orange, 0x0000);
    else    tft.pushImage(iconX, iconY, 36, 36, icon_words24_dim, 0x0000);
  } else if(mode == 4){ // Right Hand (device with buttons on right)
    const int dx = iconX + 4, dy = iconY + 9;
    tft.fillRoundRect(dx, dy, 26, 18, 3, UI_BG);
    tft.drawRoundRect(dx, dy, 26, 18, 3, sel ? UI_ACCENT : UI_DIM);
    tft.fillRect(dx + 3, dy + 3, 14, 12, sel ? UI_ACCENT_GLOW : UI_TRACK);
    tft.fillRect(dx + 5, dy + 5, 2, 8, sel ? UI_ACCENT : UI_DIM);
    tft.fillRect(dx + 26, dy + 3, 2, 4, sel ? UI_ACCENT : UI_TEXT);
    tft.fillRect(dx + 26, dy + 11, 2, 4, sel ? UI_ACCENT : UI_TEXT);
  } else if(mode == 5){ // Left Hand (device with buttons on left)
    const int dx = iconX + 6, dy = iconY + 9;
    tft.fillRoundRect(dx, dy, 26, 18, 3, UI_BG);
    tft.drawRoundRect(dx, dy, 26, 18, 3, sel ? UI_ACCENT : UI_DIM);
    tft.fillRect(dx + 9, dy + 3, 14, 12, sel ? UI_ACCENT_GLOW : UI_TRACK);
    tft.fillRect(dx + 19, dy + 5, 2, 8, sel ? UI_ACCENT : UI_DIM);
    tft.fillRect(dx - 2, dy + 3, 2, 4, sel ? UI_ACCENT : UI_TEXT);
    tft.fillRect(dx - 2, dy + 11, 2, 4, sel ? UI_ACCENT : UI_TEXT);
  }

  // Título y subtítulo centrados verticalmente dentro de la tarjeta
  const int textX = iconX + 36 + SX(12);
  const int textY = y + (h - SY(30)) / 2;

  tft.setFreeFont(FSSB9);
  tft.setTextDatum(TL_DATUM);
  tft.setTextColor(sel ? UI_TEXT : 0xC618, bgCol);
  tft.drawString(title, textX, textY, GFXFF);

  tft.setFreeFont(FSS9);
  tft.setTextDatum(TL_DATUM);
  tft.setTextColor(sel ? 0x9CD3 : 0x6B4D, bgCol);
  tft.drawString(sub, textX, textY + SY(17), GFXFF);
  tft.setTextDatum(TL_DATUM);
}

/* Animación de deslizamiento fluido de la píldora de selección entre tarjetas */
static void animateSelectionSlide(int cardX, int cardW, int cardH, int fromY, int toY){
  const int yStart = fromY + SY(7);
  const int yEnd   = toY + SY(7);
  const int pillX  = cardX + SX(4);
  const int pillW  = SX(5);
  const int pillH  = cardH - SY(14);

  // Apagar halo de la tarjeta anterior
  tft.fillRoundRect(cardX + SX(3), fromY + SY(6), SX(7), pillH + 2, 3, UI_CARD_BG);
  tft.drawRoundRect(cardX, fromY, cardW, cardH, 6, UI_CARD_BOR);

  const int gapY1 = min(fromY, toY) + cardH;
  const int gapY2 = max(fromY, toY);

  const int STEPS = 6;
  int lastPillY = yStart;
  for(int s = 1; s <= STEPS; s++){
    const float t = (float)s / STEPS;
    const float ease = t * (2.0f - t); // Suavizado ease-out cuadrático
    const int curPillY = yStart + (int)((yEnd - yStart) * ease + 0.5f);

    if(curPillY > lastPillY){
      for(int py = lastPillY; py < curPillY; py++){
        const uint16_t c = (py >= gapY1 && py < gapY2) ? UI_BG : UI_CARD_BG;
        tft.drawFastHLine(pillX - 1, py, pillW + 2, c);
      }
    } else if(curPillY < lastPillY){
      for(int py = curPillY + pillH; py < lastPillY + pillH; py++){
        const uint16_t c = (py >= gapY1 && py < gapY2) ? UI_BG : UI_CARD_BG;
        tft.drawFastHLine(pillX - 1, py, pillW + 2, c);
      }
    }

    tft.fillRoundRect(pillX, curPillY, pillW, pillH, 2, UI_ACCENT);
    lastPillY = curPillY;
    delay(14);
  }
}

void orientation(bool leftSelected, bool animate){
  int cardX, cardW, cardH, y1, y2;
  getMenuCardLayout(cardX, cardW, cardH, y1, y2);

  if(animate){
    const int fromY = leftSelected ? y1 : y2;
    const int toY   = leftSelected ? y2 : y1;
    animateSelectionSlide(cardX, cardW, cardH, fromY, toY);
    drawMenuCard(cardX, y1, cardW, cardH, !leftSelected, "RIGHT HAND", "Buttons on right", 4);
    drawMenuCard(cardX, y2, cardW, cardH, leftSelected,  "LEFT HAND",  "Buttons on left (180 deg)", 5);
  } else {
    tft.fillScreen(UI_BG);
    brandHead();
    thinRail(y1, y2, cardH);
    drawMenuCard(cardX, y1, cardW, cardH, !leftSelected, "RIGHT HAND", "Buttons on right", 4);
    drawMenuCard(cardX, y2, cardW, cardH, leftSelected,  "LEFT HAND",  "Buttons on left (180 deg)", 5);
  }
}

void menu(bool diceSelected, bool animate){
  int cardX, cardW, cardH, y1, y2;
  getMenuCardLayout(cardX, cardW, cardH, y1, y2);

  if(animate){
    const int fromY = diceSelected ? y2 : y1;
    const int toY   = diceSelected ? y1 : y2;
    animateSelectionSlide(cardX, cardW, cardH, fromY, toY);
    drawMenuCard(cardX, y1, cardW, cardH, diceSelected, "DICE SEED", "50 or 99 rolls", 0);
    drawMenuCard(cardX, y2, cardW, cardH, !diceSelected, "COIN SEED", "128 or 256 flips", 1);

    // Giro 360° inmediato en el icono de la opción recién seleccionada
    const int iconX = cardX + SX(14);
    if(diceSelected){
      const int iconY = y1 + (cardH - 36) / 2;
      for(int f = 0; f < 12; f++){
        tft.fillRect(iconX, iconY, 36, 36, UI_CARD_BG_SEL);
        tft.pushImage(iconX, iconY, 36, 36, dice_spin_frames[f], 0x0000);
        delay(16);
      }
      tft.fillRect(iconX, iconY, 36, 36, UI_CARD_BG_SEL);
      tft.pushImage(iconX, iconY, 36, 36, icon_dice_orange, 0x0000);
    } else {
      const int iconY = y2 + (cardH - 36) / 2;
      for(int f = 0; f < 12; f++){
        tft.fillRect(iconX, iconY, 36, 36, UI_CARD_BG_SEL);
        tft.pushImage(iconX, iconY, 36, 36, coin_spin_frames[f], 0x0000);
        delay(16);
      }
      tft.fillRect(iconX, iconY, 36, 36, UI_CARD_BG_SEL);
      tft.pushImage(iconX, iconY, 36, 36, icon_coin_orange, 0x0000);
    }
  } else {
    tft.fillScreen(UI_BG);
    brandHead();
    thinRail(y1, y2, cardH);
    drawMenuCard(cardX, y1, cardW, cardH, diceSelected, "DICE SEED", "50 or 99 rolls", 0);
    drawMenuCard(cardX, y2, cardW, cardH, !diceSelected, "COIN SEED", "128 or 256 flips", 1);
  }
}

void words(uint8_t nWords, bool animate){
  int cardX, cardW, cardH, y1, y2;
  getMenuCardLayout(cardX, cardW, cardH, y1, y2);
  const bool w12 = (nWords == 12);

  if(animate){
    const int fromY = w12 ? y2 : y1;
    const int toY   = w12 ? y1 : y2;
    animateSelectionSlide(cardX, cardW, cardH, fromY, toY);
  } else {
    tft.fillScreen(UI_BG);
    brandHead();
    thinRail(y1, y2, cardH);
  }

  drawMenuCard(cardX, y1, cardW, cardH, w12,  "12 WORDS", "128 bits of entropy", 2);
  drawMenuCard(cardX, y2, cardW, cardH, !w12, "24 WORDS", "256 bits of entropy", 3);
}

/*----------------- captura de moneda -----------------*/
void coinEnter(uint16_t totalBits){
  tft.fillScreen(UI_BG);
  eyebrow("FLIP COIN");
  rail("HEADS", "TAILS", false);   //arriba cara, abajo cruz: no hace falta más
}

void coinUpdate(uint16_t done, uint16_t totalBits, const uint8_t *entropy){
  const int railW = g_leftHanded ? (UI_W - UI_RAIL_X) : 0;
  const int m = railW + UI_M;
  const int rightBound = g_leftHanded ? (UI_W - UI_M) : (UI_RAIL_X - SX(4));

  const int endX = bigNumber(totalBits - done, SY(56));
  tft.fillRect(endX, SY(44), rightBound - endX, SY(14), UI_BG);
  tiny("BITS LEFT", endX + SX(10), SY(46), UI_DIM, 'L', 1);

  /* Los últimos 16 lanzamientos: lleno = cara, hueco = cruz */
  const int from = (done > 16) ? done - 16 : 0;
  const int cell = SY(8), pitch = SX(9);
  tft.fillRect(m, SY(72), rightBound - m, cell, UI_BG);
  for(int i=0; i<16; i++){
    const int idx = from + i, x = m + i*pitch;
    if(idx >= done) break;
    const uint8_t bit = (entropy[idx/8] >> (7 - idx%8)) & 1;
    if(bit) tft.fillRect(x, SY(72), cell, cell, UI_ACCENT);
    else    tft.drawRect(x, SY(72), cell, cell, UI_DIM);
  }

  /* La entropía en hexadecimal, por bytes y alternando el color: es lo que
     el usuario coteja contra su papel mientras lanza. */
  tft.fillRect(m, SY(90), rightBound - m, SY(24), UI_BG);
  const int bytes = done / 8;
  const int first = (bytes > 26) ? bytes - 26 : 0;
  for(int i=first; i<bytes; i++){
    char b[3]; snprintf(b, sizeof(b), "%02X", entropy[i]);
    const int k = i - first;
    tiny(b, m + (k % 13) * SX(13), SY(90) + (k / 13) * SY(11),
         (i % 2) ? UI_TEXT : UI_ACCENT, 'L', 0);
  }

  bar(m, SY(118), UI_RAIL_X - 2*UI_M, SY(4), (float)done / totalBits);
}

/*----------------- captura de dado -----------------*/
void diceEnter(uint8_t totalRolls){
  tft.fillScreen(UI_BG);
  eyebrow("ROLL DICE");
  const int m = g_leftHanded ? (UI_W - UI_RAIL_X + UI_M) : UI_M;
  tiny("ROLLS LEFT", m, SY(64), UI_DIM, 'L', 1);
  rail("1-6", "ACCEPT", true);
}

/* Las tres últimas tiradas, de más antigua a más reciente. Ver el trío
   completo es lo que te deja comprobar que entró lo que lanzaste. */
void diceHistory(const uint8_t *hist){
  const int m = g_leftHanded ? (UI_W - UI_RAIL_X + UI_M) : UI_M;
  tft.fillRect(m, SY(78), SX(100), SY(26), UI_BG);
  static const uint16_t shade[3] = { UI_TRACK, UI_DIM, UI_TEXT };
  for(int i=0; i<3; i++)
    if(hist[i]) die(m + i*SX(30), SY(78), SY(26), hist[i], shade[i]);
}

void diceUpdate(uint8_t done, uint8_t totalRolls, uint8_t value, const uint8_t *hist){
  bigNumber(totalRolls - done, SY(56));

  const int m = g_leftHanded ? (UI_W - UI_RAIL_X + UI_M) : UI_M;
  const int size = SY(64);
  const int x = g_leftHanded ? (UI_W - size - SX(11)) : (UI_RAIL_X - size - SX(11));
  tft.fillRect(x, SY(16), size, size, UI_BG);
  die(x, SY(16), size, value, UI_ACCENT);

  diceHistory(hist);
  bar(m, SY(118), UI_RAIL_X - 2*UI_M, SY(4), (float)done / totalRolls);
}

/*----------------- mantener OK para empezar de nuevo -----------------*/
static int holdFilled = 0;          //ancho ya pintado de la barra

void holdEnter(void){
  const int railW = UI_W - UI_RAIL_X;
  if(g_leftHanded){
    tft.fillRect(railW, 0, UI_W - railW, UI_H, UI_BG);
    tiny("START OVER", railW + (UI_W - railW)/2, SY(38), UI_TEXT, 'C', 1, UI_BIG_BODY);
    tft.fillRect(railW + UI_M, SY(68), UI_RAIL_X - 2*UI_M, SY(10), UI_TRACK);
    tiny("RELEASE TO CANCEL", railW + (UI_W - railW)/2, SY(92), UI_DIM, 'C', 1);

    tft.fillRect(0, 0, railW, UI_H, UI_BG);
    tiny("OK", railW/2, SY(96), UI_ACCENT, 'C', 1);
    tiny("HOLD", railW/2, SY(106), UI_TEXT, 'C', 0);
    caret(railW/2, SY(124), SX(9), SY(-6), UI_DIM);
  } else {
    tft.fillRect(0, 0, UI_RAIL_X, UI_H, UI_BG);
    tiny("START OVER",        UI_RAIL_X/2, SY(38), UI_TEXT, 'C', 1, UI_BIG_BODY);
    tft.fillRect(UI_M, SY(68), UI_RAIL_X - 2*UI_M, SY(10), UI_TRACK);
    tiny("RELEASE TO CANCEL", UI_RAIL_X/2, SY(92), UI_DIM,  'C', 1);

    tft.fillRect(UI_RAIL_X+1, 0, UI_W - UI_RAIL_X - 1, UI_H, UI_BG);
    tiny("OK",   UI_RAIL_CX, SY(96),  UI_ACCENT, 'C', 1);
    tiny("HOLD", UI_RAIL_CX, SY(106), UI_TEXT,   'C', 0);
    caret(UI_RAIL_CX, SY(124), SX(9), SY(-6), UI_DIM);   //senala el boton fisico
  }
  holdFilled = 0;
}

/* Solo se pinta lo que crece: repintar la barra entera a cada vuelta del
   bucle, cien veces por segundo, se ve como un parpadeo. */
void holdUpdate(float frac){
  if(frac < 0) frac = 0;
  if(frac > 1) frac = 1;
  const int railW = g_leftHanded ? (UI_W - UI_RAIL_X) : 0;
  const int w  = UI_RAIL_X - 2*UI_M;
  const int px = (int)(w * frac + 0.5f);
  if(px <= holdFilled) return;
  tft.fillRect(railW + UI_M + holdFilled, SY(68), px - holdFilled, SY(10), UI_ACCENT);
  holdFilled = px;
}

void generating(void){
  s_pwrX = -1; s_pwrY = -1;
  tft.fillScreen(UI_BG);

  // Etiqueta superior táctica
  tiny("CRYPTOGRAPHIC DERIVATION", UI_W/2, SY(24), UI_DIM, 'C', 1);

  // Título principal en negrita
  tft.setFreeFont(FSSB9);
  tft.setTextDatum(MC_DATUM);
  tft.setTextColor(UI_ACCENT, UI_BG);
  tft.drawString("GENERATING SEED", UI_W/2, UI_H/2 - SY(18), GFXFF);
  tft.setTextDatum(TL_DATUM);

  // Barra de progreso táctica
  const int barX = UI_W / 6;
  const int barW = (UI_W * 2) / 3;
  const int barY = UI_H / 2 + SY(8);
  const int barH = SY(6);

  tft.fillRoundRect(barX, barY, barW, barH, 3, UI_TRACK);
  tft.drawRoundRect(barX - 1, barY - 1, barW + 2, barH + 2, 4, UI_CARD_BOR);

  const char* stages[4] = {
    "HASHING ENTROPY POOL...",
    "CALCULATING CHECKSUM...",
    "PBKDF2 HMAC-SHA512...",
    "FINALIZING BIP39 SEED..."
  };

  static const char hexChars[] = "0123456789ABCDEF";
  char hexDisplay[24];
  memset(hexDisplay, 0, sizeof(hexDisplay));

  const int TOTAL_STEPS = 12;
  for(int step = 1; step <= TOTAL_STEPS; step++){
    const float frac = (float)step / (float)TOTAL_STEPS;
    const int fillW = (int)(barW * frac + 0.5f);
    tft.fillRoundRect(barX, barY, fillW, barH, 3, UI_ACCENT);

    // Live scrambling crypto hex stream
    const int lockedPairs = (step * 7) / TOTAL_STEPS;
    for(int b = 0; b < 7; b++){
      const int pos = b * 3;
      if(b < lockedPairs){
        hexDisplay[pos]     = hexChars[(step * 7 + b * 5) & 0xF];
        hexDisplay[pos + 1] = hexChars[(step * 11 + b * 3 + 7) & 0xF];
      } else {
        hexDisplay[pos]     = hexChars[rand() & 0xF];
        hexDisplay[pos + 1] = hexChars[rand() & 0xF];
      }
      hexDisplay[pos + 2] = (b < 6) ? ' ' : '\0';
    }
    tft.fillRect(barX, UI_H/2 - SY(6), barW, SY(10), UI_BG);
    tiny(hexDisplay, UI_W/2, UI_H/2 - SY(6), (step == TOTAL_STEPS) ? UI_ACCENT : UI_TEXT, 'C', 1);

    const int stageIdx = min(3, (step - 1) / 3);
    tft.fillRect(0, barY + barH + SY(8), UI_W, SY(16), UI_BG);
    tiny(stages[stageIdx], UI_W/2, barY + barH + SY(10), 0x9CD3, 'C', 1);

    delay(45);
  }
  delay(80);
}

/*----------------- pantallas de la semilla -----------------*/
void mnemonic(const char *mn, uint8_t nWords, uint8_t from, uint8_t step, uint8_t total){
  head(nWords == 12 ? "MNEMONIC WORDS" : (from ? "MNEMONIC 13-24" : "MNEMONIC 1-12"), step, total);

  /* Rejilla fija de 6 filas x 2 columnas. En línea corrida, doce palabras
     largas ocupaban seis líneas y la última se salía de la pantalla; así
     caben siempre, sin depender de lo que midan. El número delante evita
     tener que contarlas al copiarlas. */
  const int COL[2] = { SX(6), SX(122) };
  int idx = 0, shown = 0;
  const char *p = mn;
  char wordBuf[16];

  while(*p && shown < 12){
    while(*p == ' ') p++;
    if(!*p) break;
    const char *end = p;
    while(*end && *end != ' ') end++;
    int wlen = end - p;
    if(idx++ < from){
      p = end;
      continue;
    }
    if(wlen >= (int)sizeof(wordBuf)) wlen = sizeof(wordBuf) - 1;
    memcpy(wordBuf, p, wlen);
    wordBuf[wlen] = '\0';

    const int x = COL[shown / 6], y = SY(30) + (shown % 6) * SY(17);
    char num[4]; snprintf(num, sizeof(num), "%d", from + shown + 1);
    tiny(num,     x + SX(14), y + SY(4), UI_DIM,  'R', 0);
    tiny(wordBuf, x + SX(18), y,         UI_TEXT, 'L', 0, UI_BIG_BODY);
    shown++;
    p = end;
  }
  memzero(wordBuf, sizeof(wordBuf));
}

void seedAddress(const char *addr, uint8_t step, uint8_t total){
  head("FIRST ADDRESS", step, total);
  bodyLine("m/84'/0'/0'/0/0", SY(30), UI_ACCENT);
  int y = SY(48);
  int len = strlen(addr);
  char chunk[UI_BIG_CPL + 1];
  for(int i=0; i<len; i += UI_BIG_CPL){
    int clen = min(len - i, UI_BIG_CPL);
    memcpy(chunk, addr + i, clen);
    chunk[clen] = '\0';
    bigLine(chunk, y, UI_TEXT);
    y += UI_BIG_LH;
  }
  memzero(chunk, sizeof(chunk));
}

void seedZpub(const char *zpub, uint8_t step, uint8_t total){
  head("ACCOUNT ZPUB", step, total);

  /* Un zpub son 111 caracteres de base58: no se copia a mano, se escanea
     para montar el monedero de sólo lectura. Al lado, principio y final
     para poder identificarlo de un vistazo. */
  char prefix[9];
  size_t len = strlen(zpub);
  if(len >= 8){
    memcpy(prefix, zpub, 8);
    prefix[8] = '\0';
  }else{
    snprintf(prefix, sizeof(prefix), "%s", zpub);
  }
  char suffix[10];
  if(len >= 5){
    snprintf(suffix, sizeof(suffix), "...%s", zpub + len - 5);
  }else{
    suffix[0] = '\0';
  }
  tiny(prefix, UI_M, SY(32), UI_TEXT, 'L', 0, UI_BIG_BODY);
  tiny(suffix, UI_M, SY(54), UI_TEXT, 'L', 0, UI_BIG_BODY);
  tiny("SCAN TO IMPORT",                        UI_M, SY(84), UI_DIM,  'L', 1);
  tiny("WATCH-ONLY",                            UI_M, SY(96), UI_DIM,  'L', 1);

  const int version = 6, px = 2;
  QRCode qr;
  uint8_t buf[qrcode_getBufferSize(version)];
  if(qrcode_initText(&qr, buf, version, 0, zpub) >= 0){
    /* Centrado en el hueco que queda bajo la cabecera, no pegado a ella */
    const int x0 = UI_W - qr.size*px - SX(8);
    const int y0 = SY(22) + (UI_H - SY(22) - qr.size*px) / 2;
    for(uint8_t y=0; y<qr.size; y++)
      for(uint8_t x=0; x<qr.size; x++)
        tft.fillRect(x0 + x*px, y0 + y*px, px, px,
                     qrcode_getModule(&qr, x, y) ? UI_QR_LIGHT : UI_BG);
  }
  memzero(buf, sizeof(buf));
  memzero(&qr, sizeof(qr));
}

void seedEntropy(const char *hex, uint8_t step, uint8_t total){
  head("ENTROPY (HEX)", step, total);
  /* A tamaño 1 y todo seguido no había quien lo leyera. Ocho bytes por fila,
     a doble tamaño y alternando el color: se puede cantar en voz alta. */
  const int hexLen = strlen(hex);
  const int bytes = hexLen / 2;
  char byteBuf[3];
  byteBuf[2] = '\0';
  for(int i=0; i<bytes; i++){
    byteBuf[0] = hex[i*2];
    byteBuf[1] = hex[i*2 + 1];
    tiny(byteBuf, SX(8) + (i % 8) * SX(29), SY(32) + (i / 8) * SY(26),
         (i % 2) ? UI_TEXT : UI_ACCENT, 'L', 0, UI_BIG_BODY);
  }
  memzero(byteBuf, sizeof(byteBuf));
  if(bytes <= 16) tiny("CHECK IT OFFLINE", UI_M, SY(98), UI_DIM, 'L', 1);
}

/* Versión mínima que aguanta el texto, en modo byte con corrección L.
   La v1 fijaba la 11 (61 módulos) para todo, y no hace falta: 12 palabras son
   67 caracteres y 24 son 155. Menos módulos significa módulos más grandes,
   que es lo único que decide si una cámara lo engancha. */
static uint8_t qrVersionFor(size_t len){
  if(len <= 134) return 6;    // 41 módulos
  if(len <= 154) return 7;    // 45
  if(len <= 192) return 8;    // 49
  if(len <= 230) return 9;    // 53
  return 11;                  // 61, el techo de siempre
}

void seedQr(const char *data){
  s_pwrX = -1; s_pwrY = -1;
  const size_t len = strlen(data);
  const uint8_t version = qrVersionFor(len);
  QRCode qrcode;
  uint8_t buf[qrcode_getBufferSize(11)];        // dimensionado al peor caso
  if(qrcode_initText(&qrcode, buf, version, 0, data) >= 0){
    /* El módulo manda para escanear, pero la zona tranquila hace falta o no
       hay código que valga: se coge el mayor píxel por módulo que deje al
       menos 2 módulos de margen claro, y luego se ensancha el margen con lo
       que sobre, hasta los 4 que pide la norma.

       Medido contra un decodificador de verdad, con y sin desenfoque: en la
       T-Display salen 3px con 2 módulos para 12 palabras y 2px con 4 para 24;
       en la S3, 3px y 4 módulos en los dos casos. */
    const int QUIET_MIN = 2, QUIET_MAX = 4;
    int px = 1;
    while((qrcode.size + 2*QUIET_MIN) * (px+1) <= UI_H && px < 6) px++;
    int quiet = (UI_H - qrcode.size*px) / (2*px);
    if(quiet > QUIET_MAX) quiet = QUIET_MAX;

    tft.fillScreen(UI_BG);
    tiny("EXPORT", UI_M, SY(10), UI_ACCENT, 'L', 1);
    tiny("SCAN WITH AN",  UI_M, SY(34), UI_DIM, 'L', 0);
    tiny("OFFLINE WALLET",UI_M, SY(44), UI_DIM, 'L', 0);
    tiny("NEVER A PHONE", UI_M, SY(62), UI_ACCENT, 'L', 0);

    /* Oscuro sobre claro, que es como se define un QR. Estaba al revés: los
       módulos oscuros se pintaban en blanco y el fondo negro hacía de zona
       tranquila, así que salía un código invertido. Muchos lectores de móvil
       no leen un QR invertido, y comprobado con un decodificador: el de antes
       no se leía ni sin desenfoque, y éste sí. */
    const int qw = qrcode.size * px, b = quiet * px;
    const int qx = UI_W - qw - b - SX(2);
    const int qy = (UI_H - qw) / 2;

    tft.fillRect(qx - b, qy - b, qw + 2*b, qw + 2*b, UI_QR_LIGHT);
    for(uint8_t y=0; y<qrcode.size; y++)
      for(uint8_t x=0; x<qrcode.size; x++)
        if(qrcode_getModule(&qrcode, x, y))
          tft.fillRect(qx + x*px, qy + y*px, px, px, UI_QR_DARK);
  }
  memzero(buf, sizeof(buf));
  memzero(&qrcode, sizeof(qrcode));
}

void seedExit(void){
  s_pwrX = -1; s_pwrY = -1;
  tft.fillScreen(UI_BG);

  /* Cabecera distinta a propósito: una regla con la etiqueta incrustada.
     Esta pantalla no es una más de la semilla, y debe notarse. */
  tft.drawFastHLine(UI_M, SY(22), UI_W - 2*UI_M, UI_TRACK);
  tft.fillRect(UI_M + SX(6), SY(16), 46, 13, UI_BG);   //hueco del tamaño del texto
  tiny("EXIT", UI_M + SX(12), SY(18), UI_ACCENT, 'L', 2);

  /* Lo único que el usuario tiene que hacer, a doble tamaño */
  tiny("WRITE IT DOWN", SX(6), SY(36), UI_TEXT, 'L', 0, UI_BIG_BODY);

  /* Y por qué: lo que este aparato no ha hecho con tu semilla */
  tiny("GENERATED OFFLINE",      UI_M, SY(62), UI_DIM, 'L', 1);
  tiny("NEVER WRITTEN TO FLASH", UI_M, SY(74), UI_DIM, 'L', 1);
  tiny("IT ONLY LIVES IN RAM",   UI_M, SY(86), UI_DIM, 'L', 1);

  /* El recuadro va abajo a la derecha, a la altura del botón OK físico,
     y la punta apunta hacia él. */
  tiny("TO WIPE & LEAVE", UI_M, SY(112), UI_DIM, 'L', 1);
  const int bx = SX(126), by = SY(100), bw = SX(106), bh = SY(30);
  tft.drawRoundRect(bx,   by,   bw,   bh,   6, UI_ACCENT);
  tft.drawRoundRect(bx+1, by+1, bw-2, bh-2, 5, UI_ACCENT);
  tiny("HOLD OK", bx + bw/2, by + (bh-8*UI_BIG_BODY)/2, UI_ACCENT, 'C', 1, UI_BIG_BODY);
  /* la punta señala al botón OK físico, en el borde derecho */
  tft.fillTriangle(UI_W-SX(6), by+SY(9), UI_W-SX(6), by+SY(21), UI_W-SX(1), by+SY(15), UI_ACCENT);
}

}  // namespace ui
