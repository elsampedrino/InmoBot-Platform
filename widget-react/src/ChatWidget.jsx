// ChatWidget.jsx - Componente principal del widget
import React, { useState, useEffect, useRef } from 'react';
import './ChatWidget.css';

const ChatWidget = ({ config }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [sessionId] = useState(() => `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Configuración con defaults
  const {
    apiUrl = 'https://n8n-bot-inmobiliario.onrender.com/webhook/chat',
    primaryColor = '#2563eb',
    botName = 'AsistenteBot',
    welcomeMessage = '¡Hola! Soy tu asistente inmobiliario virtual. ¿En qué te puedo ayudar hoy?',
    placeholderText = 'Escribe tu mensaje...',
    position = 'bottom-right',
    buttonSize = '60px',
    chatWidth = '380px',
    chatHeight = '600px'
  } = config || {};

  // Scroll automático al último mensaje
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Focus en input cuando se abre
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  // Mensaje de bienvenida al abrir por primera vez
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      setMessages([
        {
          id: 'welcome',
          text: welcomeMessage,
          sender: 'bot',
          timestamp: new Date().toISOString()
        }
      ]);
    }
  }, [isOpen, messages.length, welcomeMessage]);

  // Toggle widget
  const toggleWidget = () => {
    setIsOpen(!isOpen);
    if (!isOpen) {
      setUnreadCount(0);
    }
  };

  // Enviar mensaje
  const sendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage = {
      id: `user-${Date.now()}`,
      text: inputValue,
      sender: 'user',
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputValue,
          sessionId: sessionId,
          timestamp: new Date().toISOString()
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      setIsTyping(false);

      const botMessage = {
        id: `bot-${Date.now()}`,
        text: data.response || data.respuesta_bot || 'Lo siento, no pude procesar tu consulta.',
        sender: 'bot',
        timestamp: new Date().toISOString(),
        propiedades: data.propiedades_detalladas || data.propiedades || [],
        costos: data.metricas || data.costos || null
      };

      setMessages(prev => [...prev, botMessage]);

      // Incrementar contador si está cerrado
      if (!isOpen) {
        setUnreadCount(prev => prev + 1);
      }

    } catch (error) {
      console.error('Error sending message:', error);
      setIsTyping(false);
      
      const errorMessage = {
        id: `error-${Date.now()}`,
        text: 'Lo siento, hubo un problema al conectar con el servidor. Por favor, intenta de nuevo en unos momentos.',
        sender: 'bot',
        timestamp: new Date().toISOString(),
        isError: true
      };

      setMessages(prev => [...prev, errorMessage]);
    }
  };

  // Handle Enter key
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Nueva consulta
  const startNewChat = () => {
    setMessages([
      {
        id: 'welcome-new',
        text: welcomeMessage,
        sender: 'bot',
        timestamp: new Date().toISOString()
      }
    ]);
  };

  // Formatear timestamp
  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' });
  };

  // Renderizar mensaje con markdown básico
  const renderMessage = (message) => {
    let text = message.text;

    // Convertir **texto** a <strong>
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Convertir URLs a links
    text = text.replace(
      /(https?:\/\/[^\s]+)/g,
      '<a href="$1" target="_blank" rel="noopener noreferrer">Ver foto</a>'
    );

    // Convertir saltos de línea
    text = text.replace(/\n/g, '<br/>');

    return <div dangerouslySetInnerHTML={{ __html: text }} />;
  };

  // Estilos dinámicos basados en config
  const dynamicStyles = {
    '--primary-color': primaryColor,
    '--button-size': buttonSize,
    '--chat-width': chatWidth,
    '--chat-height': chatHeight
  };

  return (
    <div 
      className={`chat-widget-container ${position}`} 
      style={dynamicStyles}
    >
      {/* Botón flotante */}
      {!isOpen && (
        <button 
          className="chat-widget-button"
          onClick={toggleWidget}
          aria-label="Abrir chat"
        >
          <svg 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            strokeWidth="2"
            className="chat-icon"
          >
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
          {unreadCount > 0 && (
            <span className="unread-badge">{unreadCount}</span>
          )}
        </button>
      )}

      {/* Ventana de chat */}
      {isOpen && (
        <div className="chat-widget-window">
          {/* Header */}
          <div className="chat-header">
            <div className="chat-header-info">
              <div className="bot-avatar">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/>
                </svg>
              </div>
              <div className="bot-info">
                <h3 className="bot-name">{botName}</h3>
                <span className="bot-status">
                  <span className="status-dot"></span>
                  En línea
                </span>
              </div>
            </div>
            <div className="chat-header-actions">
              <button 
                className="header-button"
                onClick={startNewChat}
                aria-label="Nueva consulta"
                title="Nueva consulta"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 5v14M5 12h14" />
                </svg>
              </button>
              <button 
                className="header-button"
                onClick={toggleWidget}
                aria-label="Minimizar"
                title="Minimizar"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M19 9l-7 7-7-7" />
                </svg>
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="chat-messages">
            {messages.map((message) => (
              <div 
                key={message.id} 
                className={`message ${message.sender} ${message.isError ? 'error' : ''}`}
              >
                <div className="message-content">
                  {renderMessage(message)}
                  
                  {/* Mostrar propiedades si hay */}
                  {message.propiedades && message.propiedades.length > 0 && (
                    <div className="propiedades-list">
                      {message.propiedades.map((prop, idx) => (
                        <div key={idx} className="propiedad-card">
                          <strong>{prop.titulo}</strong>
                          {prop.precio && (
                            <div className="propiedad-precio">
                              {prop.precio.moneda} {prop.precio.valor.toLocaleString()}
                              {prop.precio.periodo && `/${prop.precio.periodo}`}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
                <span className="message-time">{formatTime(message.timestamp)}</span>
              </div>
            ))}

            {/* Typing indicator */}
            {isTyping && (
              <div className="message bot typing">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="chat-input-container">
            <textarea
              ref={inputRef}
              className="chat-input"
              placeholder={placeholderText}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              rows="1"
              disabled={isTyping}
            />
            <button 
              className="send-button"
              onClick={sendMessage}
              disabled={!inputValue.trim() || isTyping}
              aria-label="Enviar mensaje"
            >
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
              </svg>
            </button>
          </div>

          {/* Footer */}
          <div className="chat-footer">
            <span className="powered-by">
              Powered by InmoBot
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatWidget;
