<template>
  <div id="app" class="game-wrapper">
    <header class="game-header">
      <div class="header-controls">
        <button class="help-btn" @click="openChatbot">?</button>
        
        <div class="scores">
          <div class="score-box user-box">
            Tú: <span class="score-value">{{ userScore }}</span>
          </div>
          <div class="score-box rival-box">
            Rival: <span class="score-value">{{ aiScore }}</span>
          </div>
        </div>
      </div>

      <div class="turn-status">
        TURNO DE: <span :class="['status-text', currentTurn === 'rival' ? 'text-red' : 'text-green']">
          {{ currentTurn === 'user' ? 'TÚ' : 'RIVAL' }}
        </span>
      </div>
    </header>

    <main class="board-container">
      <Board 
        @piece-captured="incrementScore" 
        @turn-changed="updateTurn" 
      />
    </main>

    <footer class="game-footer">
      <p>Ingeniería de Software - 5to Semestre | Asthon Ramirez</p>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import Board from './components/Board.vue';

// --- ESTADO GLOBAL DEL JUEGO ---
const userScore = ref(0);
const aiScore = ref(0);
const currentTurn = ref('user'); // Puede ser 'user' o 'rival'

/**
 * Incrementa el puntaje cuando una ficha es capturada.
 * @param {string} winner - Quién realizó la captura ('user' o 'rival')
 */
const incrementScore = (winner) => {
  if (winner === 'user') {
    userScore.value++;
  } else {
    aiScore.value++;
  }
};

/**
 * Actualiza visualmente de quién es el turno.
 */
const updateTurn = (nextTurn) => {
  currentTurn.value = nextTurn;
};

/**
 * Activa el chatbot de Landbot integrado en el index.html.
 */
const openChatbot = () => {
  if (typeof window.initLandbot === 'function') {
    window.initLandbot();
  } else {
    console.error("Error: La función initLandbot no está definida en index.html");
  }
};
</script>

<style scoped>
/* Contenedor principal con el color de fondo de tu captura */
.game-wrapper {
  background-color: #34495e;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  color: white;
  padding-top: 20px;
}

/* Header que organiza el botón ? y los marcadores */
.game-header {
  width: 100%;
  max-width: 600px;
  text-align: center;
}

.header-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

/* Botón amarillo de ayuda */
.help-btn {
  background-color: #f1c40f;
  color: #2c3e50;
  border: none;
  font-size: 24px;
  font-weight: bold;
  width: 45px;
  height: 45px;
  cursor: pointer;
  border-radius: 4px;
  transition: transform 0.2s;
}

.help-btn:hover {
  transform: scale(1.1);
}

/* Estilo de los cuadros de puntaje */
.scores {
  display: flex;
  gap: 150px; /* Espaciado entre Tú y Rival */
}

.score-box {
  padding: 8px 30px;
  font-weight: bold;
  font-size: 1.2rem;
  border-radius: 2px;
  min-width: 120px;
}

.user-box { background-color: #2980b9; }
.rival-box { background-color: #c0392b; }

/* Texto del Turno */
.turn-status {
  font-size: 2rem;
  font-weight: bold;
  letter-spacing: 1px;
  margin-bottom: 20px;
}

.text-green { color: #2ecc71; }
.text-red { color: #e74c3c; }

/* Contenedor del tablero */
.board-container {
  background-color: #2c3e50;
  padding: 15px;
  border-radius: 4px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}

.game-footer {
  margin-top: auto;
  padding: 20px;
  font-size: 0.8rem;
  opacity: 0.6;
}
</style>