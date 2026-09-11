#pragma once
#include "../boards/board.h"

/**********************************
 🍃 TEMA
 Todo lo que define el aspecto vive aquí. Cambiar de estética, o de placa,
 es cambiar este fichero: ni la máquina de estados ni la lógica de entropía
 saben nada de colores ni de coordenadas.

 Las medidas se derivan del tamaño de la placa con SX()/SY(), de modo que
 la misma composición sirve para 240x135 y para 320x170 sin mantener dos
 layouts en paralelo.
**********************************/

/*** Colores (RGB565) - Concept 1: Sovereign Tactical (Bitcoin Orange) *********/
#define UI_ACCENT         0xFD00   // Naranja Bitcoin (#FF8000 / #F7931A eléctrico)
#define UI_ACCENT_GLOW    0x9340   // Brillo cálido sutil para borde de tarjeta activa
#define UI_CARD_BG        0x10C3   // Fondo oscuro pizarra para tarjetas inactivas
#define UI_CARD_BG_SEL    0x1904   // Fondo oscuro sutilmente elevado para tarjeta activa
#define UI_CARD_BOR       0x2125   // Borde pizarra para tarjetas inactivas
#define UI_CARD_BOR_SEL   0x3A20   // Borde sutil tarjeta activa
#define UI_TEXT           0xFFFF   // Blanco puro de alto contraste
#define UI_DIM            0x8410   // Gris técnico (#848484) para subtítulos y pistas
#define UI_TRACK          0x2124   // Reglas divisorias oscuras
#define UI_BG             0x0000   // Negro obsidiana profundo
#define UI_QR_LIGHT       0xFFFF   // Fondo y zona tranquila del QR
#define UI_QR_DARK        0x0000   // Los módulos, oscuros sobre claro como manda

/*** Métricas *********************************************************/
#define UI_M          SX(10)     // margen izquierdo del contenido
#define UI_RAIL_X     SX(183)    // el raíl ancho de las capturas
#define UI_RAIL_CX    ((UI_RAIL_X + UI_W) / 2)

/* Los dos botones están en el borde derecho, uno arriba y otro abajo, así
   que la pista de cada uno se pinta a su altura. */
#define UI_RAIL_TOP_Y   SY(22)   // MOVE
#define UI_RAIL_BOT_Y   SY(96)   // OK

/* El menú lleva un raíl más estrecho y sólo con símbolos: allí los dos
   botones se interpretan solos y la carcasa ya los rotula. Que cambie de
   anchura entre capas es, además, otra señal de que no estás en el mismo
   sitio - menú, captura y datos son tres interfaces, no una. */
#define UI_MRAIL_X    SX(214)
#define UI_MRAIL_CX   ((UI_MRAIL_X + UI_W) / 2)

#define UI_HEAD_H     SY(26)     // Altura cabecera táctica del menú

/*** Tipografía *******************************************************
 Las fuentes miden lo que miden en píxeles: NO se escalan con la placa.
 En la S3 los píxeles son mayores, así que el mismo texto se ve más grande
 y además sobra ancho, de modo que caben más caracteres por línea.

 Etiqueta de versión del arranque: sirve para saber qué lleva cada placa
 cuando tienes varias en la mesa; NO demuestra nada sobre el firmware.
 Ver SECURITY.md: la integridad se comprueba desde fuera, no desde dentro. */
#ifndef SEEDER_VERSION
  #define SEEDER_VERSION "dev"
#endif
#ifndef SEEDER_COMMIT
  #define SEEDER_COMMIT  "local"
#endif

#define UI_TINY_W     6
#define UI_TINY_H     8
#define UI_BODY_TINY  1

/* La misma fuente a doble tamaño para lo que hay que copiar a mano: las
   palabras y la dirección. Un solo tipo de letra, dos tamaños, que es
   jerarquía y no mezcla. */
#define UI_BIG_BODY   2
#define UI_BIG_LH     SY(20)

/* Caracteres por línea, calculados del ancho real: así la placa grande
   aprovecha el sitio de más en vez de dejarlo en blanco. */
#define UI_BIG_CPL    ((UI_W - 2*UI_M) / (UI_TINY_W * UI_BIG_BODY))
#define UI_TINY_CPL   ((UI_W - 2*UI_M) / UI_TINY_W)

/*** Ancho de línea de las fuentes monoespaciadas **********************/
#define UI_MONO_W     11      // FreeMono9pt7b avanza 11px
#define UI_MONO_CPL   (UI_W / UI_MONO_W)
