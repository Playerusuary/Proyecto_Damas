<script setup>
import { ref, computed, defineEmits, onBeforeUnmount } from 'vue';
import { EMPTY } from '../game/constants';
import {
  isDarkCell,
  isPlayerPiece,
  isAiPiece,
  isKing,
  cellKey
} from '../game/helpers';
import {
  createInitialBoard,
  getAllLegalMoves,
  applyMove,
  getWinnerForTurn,
  getCaptureChainEndpoints
} from '../game/rules';
import { chooseAiMove } from '../game/ai';

const emit = defineEmits(['piece-captured', 'turn-changed', 'score-reset']);
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const props = defineProps({
  currentTurn: {
    type: String,
    default: 'user'
  }
});

const board = ref(createInitialBoard());
const selected = ref(null);
const forcedCapturePiece = ref(null);
const isAiThinking = ref(false);
const gameOver = ref(false);
const noCaptureTurns = ref(0);

const showEndModal = ref(false);
const endModalTitle = ref('');
const endModalMessage = ref('');

const lastMove = ref(null);
let moveAnimTimer = null;

const setLastMove = (move) => {
  lastMove.value = move;
  if (moveAnimTimer) clearTimeout(moveAnimTimer);
  moveAnimTimer = setTimeout(() => {
    lastMove.value = null;
  }, 240);
};

onBeforeUnmount(() => {
  if (moveAnimTimer) clearTimeout(moveAnimTimer);
});

const getSelectedLegalMoves = () => {
  if (!selected.value) return [];

  const forceCaptureOnly = Boolean(forcedCapturePiece.value);
  return getAllLegalMoves(
    board.value,
    'player',
    forceCaptureOnly ? forcedCapturePiece.value : null,
    forceCaptureOnly
  ).filter((move) => move.fromR === selected.value.r && move.fromC === selected.value.c);
};

const selectedLegalMoves = computed(() => getSelectedLegalMoves());

const legalTargetSet = computed(() => {
  const set = new Set();
  for (const move of selectedLegalMoves.value) {
    set.add(cellKey(move.toR, move.toC));
  }
  return set;
});

const chainEndpointSet = computed(() => {
  const set = new Set();
  if (!selected.value) return set;

  const hasCapture = selectedLegalMoves.value.some((move) => move.capture);
  if (!hasCapture) return set;

  const endpoints = getCaptureChainEndpoints(board.value, selected.value.r, selected.value.c);
  for (const point of endpoints) {
    set.add(cellKey(point.r, point.c));
  }
  return set;
});

const isLegalTargetCell = (r, c) => legalTargetSet.value.has(cellKey(r, c));
const isChainEndpointCell = (r, c) => chainEndpointSet.value.has(cellKey(r, c));
const isLastMoveTarget = (r, c) =>
  Boolean(lastMove.value && lastMove.value.toR === r && lastMove.value.toC === c);

const getPieceMotionStyle = (r, c) => {
  if (!isLastMoveTarget(r, c)) return {};
  return {
    '--start-x': `${(lastMove.value.fromC - c) * 60}px`,
    '--start-y': `${(lastMove.value.fromR - r) * 60}px`
  };
};

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const resetGame = () => {
  board.value = createInitialBoard();
  selected.value = null;
  forcedCapturePiece.value = null;
  noCaptureTurns.value = 0;
  gameOver.value = false;
  isAiThinking.value = false;
  showEndModal.value = false;
  endModalTitle.value = '';
  endModalMessage.value = '';
  lastMove.value = null;
  emit('score-reset');
  emit('turn-changed', 'user');
};

const closeEndModal = () => {
  showEndModal.value = false;
};

const openEndModal = (winner) => {
  gameOver.value = true;

  if (winner === 'player') {
    endModalTitle.value = 'Ganaste';
    endModalMessage.value = 'Terminaste la partida con victoria. Quieres jugar de nuevo?';
  } else if (winner === 'ai') {
    endModalTitle.value = 'Perdiste';
    endModalMessage.value = 'La IA gano esta partida. Quieres intentar de nuevo?';
  } else {
    endModalTitle.value = 'Empate';
    endModalMessage.value = 'No hubo capturas por muchas jugadas. Quieres jugar otra vez?';
  }

  showEndModal.value = true;
};

const validateAndHandleGameOver = (sideToMove) => {
  const winner = getWinnerForTurn(board.value, sideToMove, noCaptureTurns.value);
  if (!winner) return false;
  openEndModal(winner);
  return true;
};

const onCellClick = (r, c) => {
  if (props.currentTurn !== 'user' || isAiThinking.value || gameOver.value) return;
  if (!isDarkCell(r, c)) return;

  const cellValue = board.value[r][c];

  if (selected.value && selected.value.r === r && selected.value.c === c) {
    selected.value = null;
    return;
  }

  if (isPlayerPiece(cellValue)) {
    if (forcedCapturePiece.value) {
      if (forcedCapturePiece.value.r === r && forcedCapturePiece.value.c === c) {
        selected.value = { r, c };
      }
      return;
    }
    selected.value = { r, c };
    return;
  }

  if (!selected.value || cellValue !== EMPTY) return;

  const forceCaptureOnly = Boolean(forcedCapturePiece.value);
  const legalMoves = getAllLegalMoves(
    board.value,
    'player',
    forceCaptureOnly ? forcedCapturePiece.value : null,
    forceCaptureOnly
  ).filter((move) => move.fromR === selected.value.r && move.fromC === selected.value.c);

  const chosenMove = legalMoves.find((move) => move.toR === r && move.toC === c);
  if (!chosenMove) return;

  const result = applyMove(board.value, chosenMove);
  setLastMove(chosenMove);

  if (result.captured) {
    emit('piece-captured', 'user');
    noCaptureTurns.value = 0;
  } else {
    noCaptureTurns.value += 1;
  }

  selected.value = { r: chosenMove.toR, c: chosenMove.toC };

  if (result.captured && !result.promoted) {
    const chainMoves = getAllLegalMoves(
      board.value,
      'player',
      { r: chosenMove.toR, c: chosenMove.toC },
      true
    );
    if (chainMoves.length > 0) {
      forcedCapturePiece.value = { r: chosenMove.toR, c: chosenMove.toC };
      return;
    }
  }

  forcedCapturePiece.value = null;
  selected.value = null;

  if (validateAndHandleGameOver('ai')) return;
  playAiTurn();
};

const playAiTurn = async () => {
  emit('turn-changed', 'rival');
  isAiThinking.value = true;

  try {
    let aiForcedPiece = null;

    while (true) {
      const aiMove = await chooseAiMove(board.value, API_BASE_URL, aiForcedPiece);
      if (!aiMove) break;

      const result = applyMove(board.value, aiMove);
      setLastMove(aiMove);

      if (result.captured) {
        emit('piece-captured', 'rival');
        noCaptureTurns.value = 0;
      } else {
        noCaptureTurns.value += 1;
      }

      if (result.captured && !result.promoted) {
        const chainMoves = getAllLegalMoves(
          board.value,
          'ai',
          { r: aiMove.toR, c: aiMove.toC },
          true
        );
        if (chainMoves.length > 0) {
          aiForcedPiece = { r: aiMove.toR, c: aiMove.toC };
          await sleep(120);
          continue;
        }
      }

      await sleep(120);
      break;
    }
  } catch (error) {
    console.error('Error en turno de IA:', error);
  } finally {
    isAiThinking.value = false;
  }

  if (validateAndHandleGameOver('player')) return;
  emit('turn-changed', 'user');
};
</script>

<template>
  <div class="board-wrapper">
    <div class="checkers-board">
      <div v-for="(row, rIdx) in board" :key="rIdx" class="row">
        <div
          v-for="(cell, cIdx) in row"
          :key="cIdx"
          :class="[
            'cell',
            (rIdx + cIdx) % 2 === 0 ? 'cell-light' : 'cell-dark',
            selected && selected.r === rIdx && selected.c === cIdx ? 'selected' : '',
            isLegalTargetCell(rIdx, cIdx) ? 'legal-target' : '',
            isChainEndpointCell(rIdx, cIdx) ? 'chain-endpoint' : ''
          ]"
          @click="onCellClick(rIdx, cIdx)"
        >
          <div
            v-if="isPlayerPiece(cell)"
            :class="['piece', 'player', isKing(cell) ? 'king' : '', isLastMoveTarget(rIdx, cIdx) ? 'piece-moving' : '']"
            :style="getPieceMotionStyle(rIdx, cIdx)"
          >
            <span v-if="isKing(cell)" class="crown">K</span>
          </div>
          <div
            v-if="isAiPiece(cell)"
            :class="['piece', 'ai', isKing(cell) ? 'king' : '', isLastMoveTarget(rIdx, cIdx) ? 'piece-moving' : '']"
            :style="getPieceMotionStyle(rIdx, cIdx)"
          >
            <span v-if="isKing(cell)" class="crown">K</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showEndModal" class="modal-backdrop">
      <div class="modal-card">
        <h3>{{ endModalTitle }}</h3>
        <p>{{ endModalMessage }}</p>
        <div class="modal-actions">
          <button class="btn primary" @click="resetGame">Jugar de nuevo</button>
          <button class="btn secondary" @click="closeEndModal">Cerrar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.board-wrapper { position: relative; }
.checkers-board { border: 8px solid #3e2723; display: inline-block; }
.row { display: flex; }
.cell {
  width: 60px;
  height: 60px;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  transition: background-color 0.18s ease, box-shadow 0.18s ease;
}
.cell-light { background-color: #eadab9; }
.cell-dark { background-color: #704214; }
.selected {
  background-color: #f1c40f !important;
  box-shadow: inset 0 0 0 3px rgba(0, 0, 0, 0.22);
}
.legal-target {
  box-shadow: inset 0 0 0 3px #29b765;
}
.legal-target::after {
  content: '';
  width: 12px;
  height: 12px;
  border-radius: 999px;
  background: rgba(41, 183, 101, 0.9);
}
.chain-endpoint {
  box-shadow: inset 0 0 0 3px #1f7acc;
}
.chain-endpoint::after {
  content: '';
  width: 16px;
  height: 16px;
  border-radius: 999px;
  border: 3px solid #1f7acc;
}

.piece {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  box-shadow: 0 4px 4px rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.22s ease, box-shadow 0.22s ease;
}
.player { background-color: #2980b9; }
.ai { background-color: #c0392b; }

.king { border: 3px solid #f7e27e; }
.crown { color: #ffffff; font-weight: 800; font-size: 0.9rem; }
.piece-moving {
  animation: piece-slide 220ms ease-out;
}

@keyframes piece-slide {
  from {
    transform: translate(var(--start-x), var(--start-y)) scale(0.94);
    opacity: 0.75;
  }
  to {
    transform: translate(0, 0) scale(1);
    opacity: 1;
  }
}

.modal-backdrop {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.modal-card {
  width: min(360px, calc(100% - 24px));
  background: #f8f6f1;
  border: 3px solid #3e2723;
  border-radius: 10px;
  padding: 16px;
  color: #2c2c2c;
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.35);
}

.modal-card h3 {
  margin: 0 0 8px;
  font-size: 1.25rem;
}

.modal-card p {
  margin: 0 0 14px;
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.btn {
  border: none;
  border-radius: 6px;
  padding: 8px 12px;
  font-weight: 700;
  cursor: pointer;
}

.btn.primary {
  background: #2e7d32;
  color: #fff;
}

.btn.secondary {
  background: #d7ccc8;
  color: #3e2723;
}
</style>
