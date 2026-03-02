<template>
    <div id="app">
      <header class="game-header">
        <h1>Damas Pro - IA Edition</h1>
        <p>Nivel: Experto (Datos ACF)</p>
      </header>
  
      <main class="game-container">
        <Board />
      </main>
  
      <footer class="game-footer">
        <p>Proyecto de Ingeniería de Software - Tecmilenio</p>
      </footer>
    </div>
  </template>
  
  <script setup>
  // Importamos el archivo Board.vue que está en la carpeta components
  import Board from './components/Board.vue'
  </script>
  
  <style>
  /* Estilos globales para que se vea profesional */
  body {
    margin: 0;
    background-color: #1a1a1a;
    color: white;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  }
  
  #app {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
  }
  
  .game-header {
    margin-bottom: 20px;
    text-align: center;
  }
  
  .game-header h1 {
    color: #3498db;
    font-size: 2.5rem;
    margin: 0;
  }
  
  .game-container {
    background-color: #2c3e50;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 15px 35px rgba(0,0,0,0.5);
  }
  
  .game-footer {
    margin-top: 30px;
    font-size: 0.9rem;
    opacity: 0.7;
  }
  </style>