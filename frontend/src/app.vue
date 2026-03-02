<template>
  <div id="app" class="game-wrapper">
    <header class="game-header">
      <div class="header-controls">
        <button class="help-btn" @click="openChatbot">?</button>
        <div class="scores">
          <div class="score-box user-box">Tú: {{ userScore }}</div>
          <div class="score-box rival-box">Rival: {{ aiScore }}</div>
        </div>
      </div>
      
      <div class="turn-status">
        TURNO DE: <span :class="currentTurn === 'user' ? 'text-green' : 'text-red'">
          {{ currentTurn === 'user' ? 'TÚ' : 'RIVAL' }}
        </span>
      </div>
    </header>

    <main class="game-area">
      <div class="capture-meter-container">
        <div class="meter-segment ai" :style="{ height: (aiScore * 8.3) + '%' }"></div>
        <div class="meter-segment user" :style="{ height: (userScore * 8.3) + '%' }"></div>
      </div>

      <div class="board-container">
        <Board @piece-captured="incrementScore" @turn-changed="updateTurn" />
      </div>
    </main>

    <footer class="game-footer">
      <p>Asthon Sebastian Ramirez Gutierrez | Software Engineering @ Tecmilenio</p>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import Board from './components/Board.vue';

// Estado global para Tecmilenio
const userScore = ref(0);
const aiScore = ref(0);
const currentTurn = ref('user');

const incrementScore = (winner) => {
  if (winner === 'user') userScore.value++;
  else aiScore.value++;
};

const updateTurn = (turn) => currentTurn.value = turn;

// Llama a la función de Landbot definida en tu index.html
const openChatbot = () => {
  if (window.initLandbot) window.initLandbot();
};
</script>

<style scoped>
.game-wrapper { background-color: #34495e; min-height: 100vh; display: flex; flex-direction: column; align-items: center; color: white; padding: 20px; }
.header-controls { display: flex; justify-content: space-between; width: 100%; max-width: 600px; margin-bottom: 20px; }
.help-btn { background-color: #f1c40f; border: none; font-size: 24px; font-weight: bold; width: 45px; height: 45px; cursor: pointer; border-radius: 4px; }
.scores { display: flex; gap: 40px; }
.score-box { padding: 10px 30px; border-radius: 4px; font-weight: bold; min-width: 100px; text-align: center; }
.user-box { background-color: #2980b9; }
.rival-box { background-color: #c0392b; }
.turn-status { font-size: 2rem; font-weight: bold; margin: 20px 0; }
.text-green { color: #2ecc71; }
.text-red { color: #e74c3c; }

/* Flex para barra y tablero */
.game-area { display: flex; align-items: stretch; gap: 20px; background-color: #2c3e50; padding: 15px; border-radius: 8px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
.capture-meter-container { width: 25px; background-color: #1a252f; border-radius: 4px; display: flex; flex-direction: column-reverse; overflow: hidden; border: 2px solid #34495e; }
.meter-segment { transition: height 0.5s ease; width: 100%; }
.meter-segment.user { background-color: #2980b9; }
.meter-segment.ai { background-color: #c0392b; align-self: flex-start; }
.game-footer { margin-top: auto; opacity: 0.6; font-size: 0.8rem; padding: 10px; }
</style>