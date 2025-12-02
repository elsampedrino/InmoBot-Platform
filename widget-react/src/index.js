// index.js - Punto de entrada del widget
import React from 'react';
import { createRoot } from 'react-dom/client';
import ChatWidget from './ChatWidget';

// Clase global para inicializar el widget
class InmoBot {
  constructor() {
    this.config = {};
    this.root = null;
  }

  // Inicializar el widget
  init(config = {}) {
    this.config = {
      // Defaults
      apiUrl: 'https://n8n-bot-inmobiliario.onrender.com/webhook/chat',
      primaryColor: '#2563eb',
      botName: 'AsistenteBot',
      welcomeMessage: '¡Hola! Soy tu asistente inmobiliario virtual. ¿En qué te puedo ayudar hoy?',
      placeholderText: 'Escribe tu mensaje...',
      position: 'bottom-right',
      buttonSize: '60px',
      chatWidth: '380px',
      chatHeight: '600px',
      // Sobrescribir con config del usuario
      ...config
    };

    // Crear container si no existe
    let container = document.getElementById('inmobot-widget-root');
    if (!container) {
      container = document.createElement('div');
      container.id = 'inmobot-widget-root';
      document.body.appendChild(container);
    }

    // Renderizar el widget
    this.root = createRoot(container);
    this.root.render(React.createElement(ChatWidget, { config: this.config }));

    console.log('InmoBot widget initialized', this.config);
  }

  // Destruir el widget
  destroy() {
    if (this.root) {
      this.root.unmount();
      const container = document.getElementById('inmobot-widget-root');
      if (container) {
        container.remove();
      }
    }
  }

  // Actualizar configuración
  updateConfig(newConfig) {
    this.config = { ...this.config, ...newConfig };
    if (this.root) {
      this.root.render(React.createElement(ChatWidget, { config: this.config }));
    }
  }
}

// Exponer globalmente
window.InmoBot = new InmoBot();

// Auto-inicializar si hay config en el window
if (window.InmoBotConfig) {
  window.InmoBot.init(window.InmoBotConfig);
}

export default InmoBot;
