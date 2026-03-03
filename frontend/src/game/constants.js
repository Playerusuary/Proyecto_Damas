/**
 * frontend/src/game/constants.js
 *
 * Constantes de la logica del juego (damas).
 *
 * Convencion de valores en el tablero:
 * -  0: casilla vacia
 * -  1: peon del jugador
 * -  2: rey del jugador
 * - -1: peon de la IA
 * - -2: rey de la IA
 */

export const BOARD_SIZE = 8;

export const PLAYER_MAN = 1;
export const PLAYER_KING = 2;
export const AI_MAN = -1;
export const AI_KING = -2;
export const EMPTY = 0;

// Regla de empate: numero maximo de turnos sin captura antes de declarar draw.
export const DRAW_NO_CAPTURE_LIMIT = 80;
