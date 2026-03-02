<template>
    <div class="board">
      <div v-for="(row, rIdx) in board" :key="rIdx" class="row">
        <div 
          v-for="(cell, cIdx) in row" 
          :key="cIdx" 
          :class="['cell', (rIdx + cIdx) % 2 === 0 ? 'light' : 'dark']"
        >
          <div v-if="cell === 1" class="piece player"></div>
          <div v-if="cell === -1" class="piece ai"></div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  const board = ref([
    [0, -1, 0, -1, 0, -1, 0, -1],
    [-1, 0, -1, 0, -1, 0, -1, 0],
    [0, -1, 0, -1, 0, -1, 0, -1],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [1, 0, 1, 0, 1, 0, 1, 0],
    [0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 0]
  ])
  </script>
  
  <style scoped>
  .board { border: 5px solid #333; display: inline-block; }
  .row { display: flex; }
  .cell { width: 50px; height: 50px; display: flex; justify-content: center; align-items: center; }
  .light { background-color: #f0d9b5; }
  .dark { background-color: #b58863; }
  .piece { width: 40px; height: 40px; border-radius: 50%; }
  .player { background-color: #2196f3; }
  .ai { background-color: #f44336; }
  </style>