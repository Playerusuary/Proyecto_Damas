import axios from 'axios';
import { cloneBoard } from './helpers';
import { applyMove, getAllLegalMoves } from './rules';

export const scoreMoveWithModel = async (currentState, move, apiBaseUrl) => {
  const simulated = cloneBoard(currentState);
  applyMove(simulated, move);

  try {
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

  const captureMoves = legalMoves.filter((m) => m.capture);
  if (captureMoves.length > 0) return captureMoves[0];
  return legalMoves[0];
};
