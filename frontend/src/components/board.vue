<template>
  <div class="checkers-board">
    <div v-for="(row, rIdx) in board" :key="rIdx" class="row">
      <div 
        v-for="(cell, cIdx) in row" 
        :key="cIdx" 
        :class="[
          'cell', 
          (rIdx + cIdx) % 2 === 0 ? 'cell-light' : 'cell-dark',
          selected && selected.r === rIdx && selected.c === cIdx ? 'selected' : ''
        ]"
        @click="onCellClick(rIdx, cIdx)"
      >
        <div v-if="cell === 1" class="piece player"></div>
        <div v-if="cell === -1" class="piece ai"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, defineEmits } from 'vue';

const emit = defineEmits(['piece-captured', 'turn-changed']);

// 1 = Azul (Tú), -1 = Rojo (IA), 0 = Vacío
const board = ref([
  [0, -1, 0, -1, 0, -1, 0, -1],
  [-1, 0, -1, 0, -1, 0, -1, 0],
  [0, -1, 0, -1, 0, -1, 0, -1],
  [0, 0, 0, 0, 0, 0, 0, 0],
  [0, 0, 0, 0, 0, 0, 0, 0],
  [1, 0, 1, 0, 1, 0, 1, 0],
  [0, 1, 0, 1, 0, 1, 0, 1],
  [1, 0, 1, 0, 1, 0, 1, 0]
]);

const selected = ref(null);

const onCellClick = (r, c) => {
  const cellValue = board.value[r][c];

  if (cellValue === 1) { // Seleccionar pieza azul
    selected.value = { r, c };
  } else if (selected.value && cellValue === 0) { // Intentar mover a vacío
    verificarMovimiento(selected.value.r, selected.value.c, r, c);
  }
};

const verificarMovimiento = (fromR, fromC, toR, toC) => {
  const rowDiff = toR - fromR;
  const colDiff = Math.abs(toC - fromC);

  // Movimiento diagonal simple
  if (rowDiff === -1 && colDiff === 1) {
    ejecutar(fromR, fromC, toR, toC);
  } 
  // Captura (salto sobre ficha roja)
  else if (rowDiff === -2 && colDiff === 2) {
    const midR = (fromR + toR) / 2;
    const midC = (fromC + toC) / 2;
    if (board.value[midR][midC] === -1) {
      board.value[midR][midC] = 0; // Se elimina la roja
      ejecutar(fromR, fromC, toR, toC);
      emit('piece-captured', 'user'); // Sube el marcador y la barra azul
    }
  }
};

const ejecutar = (fR, fC, tR, tC) => {
  board.value[tR][tC] = 1;
  board.value[fR][fC] = 0;
  selected.value = null;
  emit('turn-changed', 'rival');
};
</script>

<style scoped>
.checkers-board { display: inline-block; border: 8px solid #3e2723; box-shadow: 0 5px 15px rgba(0,0,0,0.5); }
.row { display: flex; }
.cell { width: 60px; height: 60px; display: flex; justify-content: center; align-items: center; cursor: pointer; }
.cell-light { background-color: #eadab9; }
.cell-dark { background-color: #704214; }
.selected { background-color: #f1c40f !important; }

.piece { width: 48px; height: 48px; border-radius: 50%; border: 2px solid rgba(0,0,0,0.3); transition: transform 0.2s; }
.piece:hover { transform: scale(1.05); }
.player { background-color: #2980b9; }
.ai { background-color: #c0392b; }
</style>