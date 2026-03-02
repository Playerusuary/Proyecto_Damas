import {
  BOARD_SIZE,
  PLAYER_MAN,
  PLAYER_KING,
  AI_MAN,
  AI_KING
} from './constants';

export const isInsideBoard = (r, c) => r >= 0 && r < BOARD_SIZE && c >= 0 && c < BOARD_SIZE;
export const isDarkCell = (r, c) => (r + c) % 2 === 1;

export const isPlayerPiece = (v) => v === PLAYER_MAN || v === PLAYER_KING;
export const isAiPiece = (v) => v === AI_MAN || v === AI_KING;
export const isKing = (v) => Math.abs(v) === 2;

export const isOpponentPiece = (piece, other) =>
  (isPlayerPiece(piece) && isAiPiece(other)) ||
  (isAiPiece(piece) && isPlayerPiece(other));

export const cloneBoard = (state) => state.map((row) => [...row]);
export const cellKey = (r, c) => `${r},${c}`;
