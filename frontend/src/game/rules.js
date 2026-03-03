/**
 * frontend/src/game/rules.js
 *
 * Reglas y logica del juego de damas (movimientos, capturas, promociones, empate).
 *
 * Este modulo es el "motor" del juego en el frontend:
 * - Calcula movimientos simples y de captura (incluyendo reyes con movimiento diagonal largo)
 * - Aplica movimientos al estado del tablero
 * - Detecta ganador/empate
 * - Calcula endpoints posibles para cadenas de captura (para resaltar casillas en UI)
 *
 * Se apoya en:
 * - constants.js: codigos de piezas/board size
 * - helpers.js: helpers puros (clonado, validaciones, etc.)
 */

import {
  BOARD_SIZE,
  PLAYER_MAN,
  PLAYER_KING,
  AI_MAN,
  AI_KING,
  EMPTY,
  DRAW_NO_CAPTURE_LIMIT
} from './constants';
import {
  isInsideBoard,
  isDarkCell,
  isPlayerPiece,
  isAiPiece,
  isKing,
  isOpponentPiece,
  cloneBoard,
  cellKey
} from './helpers';

export const createInitialBoard = () => ([
  // Matriz 8x8. Solo casillas oscuras se usan para piezas.
  [EMPTY, AI_MAN, EMPTY, AI_MAN, EMPTY, AI_MAN, EMPTY, AI_MAN],
  [AI_MAN, EMPTY, AI_MAN, EMPTY, AI_MAN, EMPTY, AI_MAN, EMPTY],
  [EMPTY, AI_MAN, EMPTY, AI_MAN, EMPTY, AI_MAN, EMPTY, AI_MAN],
  [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
  [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
  [PLAYER_MAN, EMPTY, PLAYER_MAN, EMPTY, PLAYER_MAN, EMPTY, PLAYER_MAN, EMPTY],
  [EMPTY, PLAYER_MAN, EMPTY, PLAYER_MAN, EMPTY, PLAYER_MAN, EMPTY, PLAYER_MAN],
  [PLAYER_MAN, EMPTY, PLAYER_MAN, EMPTY, PLAYER_MAN, EMPTY, PLAYER_MAN, EMPTY]
]);

export const getDirections = (piece) => {
  // Direcciones diagonales:
  // - Peon: depende del color/lado (solo "hacia adelante")
  // - Rey: 4 diagonales
  if (piece === PLAYER_KING || piece === AI_KING) {
    return [[-1, -1], [-1, 1], [1, -1], [1, 1]];
  }
  if (piece === PLAYER_MAN) return [[-1, -1], [-1, 1]];
  return [[1, -1], [1, 1]];
};

export const getPieceCaptureMoves = (state, r, c) => {
  const piece = state[r][c];
  if (piece === EMPTY) return [];

  const moves = [];
  const directions = getDirections(piece);

  if (isKing(piece)) {
    // Rey: puede recorrer diagonales hasta encontrar un enemigo y capturar si hay aterrizaje valido.
    for (const [dr, dc] of directions) {
      let row = r + dr;
      let col = c + dc;
      let enemyFound = false;
      let enemyR = -1;
      let enemyC = -1;

      while (isInsideBoard(row, col) && isDarkCell(row, col)) {
        const current = state[row][col];

        if (!enemyFound) {
          if (current === EMPTY) {
            row += dr;
            col += dc;
            continue;
          }

          if (isOpponentPiece(piece, current)) {
            enemyFound = true;
            enemyR = row;
            enemyC = col;
            row += dr;
            col += dc;
            continue;
          }

          break;
        }

        if (current !== EMPTY) break;

        // Regla solicitada: el rey aterriza en la casilla inmediata despues de capturar.
        moves.push({
          fromR: r,
          fromC: c,
          toR: row,
          toC: col,
          capture: true,
          capturedR: enemyR,
          capturedC: enemyC
        });
        break;
      }
    }

    return moves;
  }

  for (const [dr, dc] of directions) {
    const midR = r + dr;
    const midC = c + dc;
    const landR = r + dr * 2;
    const landC = c + dc * 2;

    if (!isInsideBoard(midR, midC) || !isInsideBoard(landR, landC)) continue;
    if (!isDarkCell(landR, landC)) continue;
    if (state[landR][landC] !== EMPTY) continue;

    const midPiece = state[midR][midC];
    if (isPlayerPiece(piece) && isAiPiece(midPiece)) {
      moves.push({
        fromR: r,
        fromC: c,
        toR: landR,
        toC: landC,
        capture: true,
        capturedR: midR,
        capturedC: midC
      });
    }
    if (isAiPiece(piece) && isPlayerPiece(midPiece)) {
      moves.push({
        fromR: r,
        fromC: c,
        toR: landR,
        toC: landC,
        capture: true,
        capturedR: midR,
        capturedC: midC
      });
    }
  }

  return moves;
};

export const getPieceSimpleMoves = (state, r, c) => {
  const piece = state[r][c];
  if (piece === EMPTY) return [];

  const moves = [];
  const directions = getDirections(piece);

  if (isKing(piece)) {
    // Rey: movimiento diagonal largo mientras la casilla este vacia.
    for (const [dr, dc] of directions) {
      let toR = r + dr;
      let toC = c + dc;

      while (isInsideBoard(toR, toC) && isDarkCell(toR, toC) && state[toR][toC] === EMPTY) {
        moves.push({
          fromR: r,
          fromC: c,
          toR,
          toC,
          capture: false
        });
        toR += dr;
        toC += dc;
      }
    }
    return moves;
  }

  for (const [dr, dc] of directions) {
    const toR = r + dr;
    const toC = c + dc;
    if (!isInsideBoard(toR, toC) || !isDarkCell(toR, toC)) continue;
    if (state[toR][toC] !== EMPTY) continue;
    moves.push({
      fromR: r,
      fromC: c,
      toR,
      toC,
      capture: false
    });
  }

  return moves;
};

export const getAllLegalMoves = (state, side, forcedPiece = null, forceCaptureOnly = false) => {
  const captureMoves = [];
  const simpleMoves = [];

  for (let r = 0; r < BOARD_SIZE; r++) {
    for (let c = 0; c < BOARD_SIZE; c++) {
      const piece = state[r][c];
      if (side === 'player' && !isPlayerPiece(piece)) continue;
      if (side === 'ai' && !isAiPiece(piece)) continue;
      if (forcedPiece && (forcedPiece.r !== r || forcedPiece.c !== c)) continue;

      captureMoves.push(...getPieceCaptureMoves(state, r, c));
      if (!forceCaptureOnly) {
        simpleMoves.push(...getPieceSimpleMoves(state, r, c));
      }
    }
  }

  if (captureMoves.length > 0) return captureMoves;
  if (forceCaptureOnly) return [];
  return simpleMoves;
};

export const applyMove = (state, move) => {
  // Aplica un movimiento (mutando el tablero) y retorna flags para UI/turnos.
  const piece = state[move.fromR][move.fromC];
  state[move.fromR][move.fromC] = EMPTY;
  state[move.toR][move.toC] = piece;

  let captured = false;
  if (move.capture) {
    state[move.capturedR][move.capturedC] = EMPTY;
    captured = true;
  }

  let promoted = false;
  if (piece === PLAYER_MAN && move.toR === 0) {
    // Promocion a rey cuando el peon alcanza la ultima fila del oponente.
    state[move.toR][move.toC] = PLAYER_KING;
    promoted = true;
  }
  if (piece === AI_MAN && move.toR === BOARD_SIZE - 1) {
    state[move.toR][move.toC] = AI_KING;
    promoted = true;
  }

  return { captured, promoted };
};

export const countPieces = (state) => {
  let player = 0;
  let ai = 0;

  for (let r = 0; r < BOARD_SIZE; r++) {
    for (let c = 0; c < BOARD_SIZE; c++) {
      if (isPlayerPiece(state[r][c])) player++;
      if (isAiPiece(state[r][c])) ai++;
    }
  }

  return { player, ai };
};

export const getWinnerForTurn = (state, sideToMove, noCaptureCount) => {
  if (noCaptureCount >= DRAW_NO_CAPTURE_LIMIT) return 'draw';

  const counts = countPieces(state);
  if (counts.player === 0) return 'ai';
  if (counts.ai === 0) return 'player';

  const legalForSide = getAllLegalMoves(state, sideToMove);
  if (legalForSide.length === 0) return sideToMove === 'player' ? 'ai' : 'player';

  return null;
};

export const getCaptureChainEndpoints = (state, r, c) => {
  const initialCaptures = getPieceCaptureMoves(state, r, c);
  if (initialCaptures.length === 0) return [];

  const endpoints = new Set();

  const dfs = (draft, fromR, fromC) => {
    const captures = getPieceCaptureMoves(draft, fromR, fromC);
    if (captures.length === 0) {
      endpoints.add(cellKey(fromR, fromC));
      return;
    }

    for (const move of captures) {
      const next = cloneBoard(draft);
      const result = applyMove(next, move);

      if (result.promoted) {
        endpoints.add(cellKey(move.toR, move.toC));
        continue;
      }

      dfs(next, move.toR, move.toC);
    }
  };

  dfs(cloneBoard(state), r, c);
  endpoints.delete(cellKey(r, c));

  return Array.from(endpoints).map((value) => {
    const [row, col] = value.split(',').map(Number);
    return { r: row, c: col };
  });
};
