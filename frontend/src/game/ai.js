import axios from 'axios';
import { cloneBoard } from './helpers';
import { applyMove, getAllLegalMoves } from './rules';

/**
 * Integra la IA con el backend (/predict).
 *
 * Idea general:
 * - Para cada movimiento legal, se simula en un tablero clonado
 * - Se manda el tablero resultante al modelo (FastAPI)
 * - Se elige el movimiento con mejor score
 *
 * Nota: este archivo NO implementa el modelo. Solo consume el endpoint.
 */
export const scoreMoveWithModel = async (currentState, move, apiBaseUrl) => {
  const simulated = cloneBoard(currentState);
  applyMove(simulated, move);

  try {
    // El backend acepta:
    // - body como lista plana [64]
    // - o {"board": [64]} (ver backend/src/main.py)
    const response = await axios.post(
      `${apiBaseUrl}/predict`,
      simulated.flat(),
      { timeout: 4000 }
    );
    const score = Number(response?.data?.score);
    if (Number.isFinite(score)) return score;
    return null;
  } catch {
    return null;
  }
};

export const chooseAiMove = async (state, apiBaseUrl, forcedPiece = null) => {
  // forcedPiece se usa cuando la regla obliga a continuar una cadena de captura.
  const forceCaptureOnly = Boolean(forcedPiece);
  const legalMoves = getAllLegalMoves(state, 'ai', forcedPiece, forceCaptureOnly);
  if (legalMoves.length === 0) return null;

  const scores = await Promise.all(
    legalMoves.map((move) => scoreMoveWithModel(state, move, apiBaseUrl))
  );

  let bestMove = null;
  let bestScore = -Infinity;

  for (let i = 0; i < legalMoves.length; i++) {
    const score = scores[i];
    if (score === null) continue;
    if (score > bestScore) {
      bestScore = score;
      bestMove = legalMoves[i];
    }
  }

  if (bestMove) return bestMove;

  // Fallback si el modelo no responde:
  // - prioriza capturas
  // - si no hay capturas, toma el primer movimiento legal
  const captureMoves = legalMoves.filter((m) => m.capture);
  if (captureMoves.length > 0) return captureMoves[0];
  return legalMoves[0];
};
