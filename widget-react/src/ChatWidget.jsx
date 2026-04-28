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
  const [showContactForm, setShowContactForm] = useState(false);
  const [contactFormData, setContactFormData] = useState({
    nombre: '',
    telefono: '',
    disponibilidad: ''
  });
  const [botEnabled, setBotEnabled] = useState(true);
  const [botDisabledMessage, setBotDisabledMessage] = useState('El asistente virtual no está disponible en este momento.');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Configuración con defaults
  const {
    apiUrl = 'https://n8n-bot-inmobiliario.onrender.com/webhook/chat',
    contactUrl = 'https://n8n-bot-inmobiliario.onrender.com/webhook/contact',
    primaryColor = '#2563eb',
    botName = 'AsistenteBot',
    welcomeMessage = '¡Hola! Soy tu asistente inmobiliario virtual. ¿En qué te puedo ayudar hoy?',
    placeholderText = 'Busco una casa por menos de 100.000 USD',
    position = 'bottom-right',
    buttonSize = '60px',
    chatWidth = '500px',
    chatHeight = '600px',
    repo = 'demo' // 'demo' o 'bbr'
  } = config || {};

  // Verificar estado del bot al inicializar (antes de abrir el widget)
  useEffect(() => {
    const statusUrl = config.statusUrl || apiUrl.replace(/\/chat$/, '/status');
    fetch(statusUrl)
      .then(r => r.ok ? r.json() : null)
      .then(data => {
        if (data && data.bot_enabled === false) {
          setBotEnabled(false);
          if (data.message) setBotDisabledMessage(data.message);
        }
      })
      .catch(() => {
        // Fail-open: si el status check falla, el widget funciona normal
      });
  }, []);

  // Scroll automático al último mensaje
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Focus en input cuando se abre (solo en desktop, no en mobile para evitar que aparezca el teclado)
  useEffect(() => {
    if (isOpen && inputRef.current) {
      // Solo hacer autofocus en pantallas mayores a 480px (desktop/tablet)
      const isMobile = window.innerWidth <= 480;
      if (!isMobile) {
        inputRef.current.focus();
      }
    } else if (!isOpen) {
      // Cuando se cierra, remover focus de cualquier elemento
      if (document.activeElement && document.activeElement !== document.body) {
        document.activeElement.blur();
      }
    }
  }, [isOpen]);

  // Mensaje de bienvenida (o aviso de bot deshabilitado) al abrir por primera vez
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      setMessages([
        {
          id: 'welcome',
          text: botEnabled ? welcomeMessage : botDisabledMessage,
          sender: 'bot',
          timestamp: new Date().toISOString()
        }
      ]);
    }
  }, [isOpen, messages.length, welcomeMessage, botEnabled, botDisabledMessage]);

  // Toggle widget
  const toggleWidget = (e) => {
    setIsOpen(!isOpen);
    if (!isOpen) {
      setUnreadCount(0);
    } else {
      // Cuando se cierra el chat, remover el focus del botón
      if (e && e.currentTarget) {
        e.currentTarget.blur();
      }
      // También remover focus de cualquier elemento activo
      if (document.activeElement) {
        document.activeElement.blur();
      }
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
          timestamp: new Date().toISOString(),
          repo: repo // 'demo' o 'bbr'
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
        costos: data.metricas || data.costos || null,
        leads: data.leads === true // Solo true si explícitamente viene true del WF
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
    setShowContactForm(false);
  };

  // Manejar click en "Agendar visita"
  const handleAgendarVisita = () => {
    setShowContactForm(true);
    scrollToBottom();
  };

  // Manejar click en "Ver otras opciones"
  const handleVerOtrasOpciones = () => {
    setShowContactForm(false);
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  // Manejar cambios en formulario de contacto
  const handleContactFormChange = (field, value) => {
    setContactFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Enviar formulario de contacto
  const handleSubmitContactForm = async (e) => {
    e.preventDefault();

    if (!contactFormData.nombre || !contactFormData.telefono) {
      alert('Por favor completá tu nombre y teléfono');
      return;
    }

    // Agregar mensaje del usuario con los datos
    const contactMessage = {
      id: `contact-${Date.now()}`,
      text: `📋 Solicitud de contacto:\n\nNombre: ${contactFormData.nombre}\nTeléfono: ${contactFormData.telefono}${contactFormData.disponibilidad ? `\nDisponibilidad: ${contactFormData.disponibilidad}` : ''}`,
      sender: 'user',
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, contactMessage]);
    setIsTyping(true);

    // Enviar datos a N8N
    try {
      const response = await fetch(contactUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          nombre: contactFormData.nombre,
          telefono: contactFormData.telefono,
          disponibilidad: contactFormData.disponibilidad || 'No especificada',
          timestamp: new Date().toISOString(),
          sessionId: sessionId,
          repo: repo
        })
      });

      setIsTyping(false);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Agregar respuesta del bot
      const confirmationMessage = {
        id: `confirmation-${Date.now()}`,
        text: data.message || '¡Perfecto! Recibimos tus datos. Uno de nuestros asesores se va a contactar con vos a la brevedad para coordinar la visita. ¡Gracias por tu interés!',
        sender: 'bot',
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, confirmationMessage]);

    } catch (error) {
      console.error('Error al enviar formulario:', error);
      setIsTyping(false);

      const errorMessage = {
        id: `error-${Date.now()}`,
        text: 'Hubo un problema al enviar tu solicitud. Por favor, intentá de nuevo en unos momentos.',
        sender: 'bot',
        timestamp: new Date().toISOString(),
        isError: true
      };

      setMessages(prev => [...prev, errorMessage]);
    }

    // Limpiar formulario y ocultarlo
    setContactFormData({
      nombre: '',
      telefono: '',
      disponibilidad: ''
    });
    setShowContactForm(false);
  };

  // Formatear timestamp
  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' });
  };

  // Renderizar mensaje con markdown básico e imágenes integradas
  const renderMessage = (message) => {
    let text = message.text;

    // Remover texto "Ver fotos:" y variantes
    text = text.replace(/📷\s*Ver fotos?:\s*/gi, '');
    text = text.replace(/🖼️\s*Ver fotos?:\s*/gi, '');
    text = text.replace(/Ver fotos?:\s*/gi, '');

    // Lógica simplificada: mostrar botones solo si hay propiedades Y el WF indica leads: true
    const showButtons = message.propiedades?.length > 0 && message.leads === true;

    // Detectar idioma del mensaje para los botones
    let buttonLanguage = 'es'; // Default español
    if (text.includes('Leave your contact') || text.includes('See other options')) {
      buttonLanguage = 'en';
    } else if (text.includes('Deixar seus dados') || text.includes('Ver outras opções')) {
      buttonLanguage = 'pt';
    }

    // Limpiar el texto de los botones de acción que vienen del bot (ya no los necesitamos en el texto)
    let mainText = text
      .replace(/¿(?:Alguna de estas propiedades|Esta propiedad|Te interesa alguna|Alguna propiedad) te interesa\?.*?(?:Podés:|You can:|Você pode:)/gsi, '')
      .replace(/Are (?:any of these properties|this property) interesting.*?You can:/gsi, '')
      .replace(/(?:Alguma dessas propriedades|Esta propriedade) te interessa\?.*?Você pode:/gsi, '')
      .replace(/✅\s*(?:Dejar tus datos de contacto|Leave your contact information|Deixar seus dados de contato)/gi, '')
      .replace(/🔍\s*(?:Ver otras opciones|See other options|Ver outras opções)/gi, '')
      .trim();

    // Dividir el texto en secciones por saltos de línea dobles (propiedades separadas)
    const sections = mainText.split(/\n\n+/);

    return (
      <div>
        {sections.map((section, sectionIdx) => {
          // Buscar imágenes en esta sección
          const imageRegex = /(https?:\/\/[^\s]+\.(?:jpg|jpeg|png|gif|webp))/gi;
          const images = [];
          let match;
          let cleanSection = section;

          while ((match = imageRegex.exec(section)) !== null) {
            images.push(match[1]);
          }

          // Remover URLs de imágenes del texto
          cleanSection = cleanSection.replace(imageRegex, '');

          // Convertir **texto** a <strong>
          cleanSection = cleanSection.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

          // Convertir URLs restantes a links
          cleanSection = cleanSection.replace(
            /(https?:\/\/[^\s]+)/g,
            '<a href="$1" target="_blank" rel="noopener noreferrer">Ver enlace</a>'
          );

          // Convertir saltos de línea simples
          cleanSection = cleanSection.replace(/\n/g, '<br/>');

          return (
            <div key={sectionIdx} className="message-section">
              <div dangerouslySetInnerHTML={{ __html: cleanSection }} />
              {images.length > 0 && (
                <div className="message-images">
                  {images.map((url, imgIdx) => (
                    <img
                      key={imgIdx}
                      src={url}
                      alt={`Foto ${imgIdx + 1}`}
                      className="message-image-thumbnail"
                      onClick={() => window.open(url, '_blank')}
                      title="Click para ampliar"
                    />
                  ))}
                </div>
              )}
            </div>
          );
        })}

        {/* Botones de acción si están presentes */}
        {showButtons && (() => {
          // Textos según el idioma detectado
          const buttonTexts = {
            es: {
              prompt: '¿Alguna de estas propiedades te interesa? Podés:',
              schedule: '✅ Dejar tus datos de contacto',
              other: '🔍 Ver otras opciones'
            },
            en: {
              prompt: 'Are any of these properties interesting to you? You can:',
              schedule: '✅ Leave your contact information',
              other: '🔍 See other options'
            },
            pt: {
              prompt: 'Alguma dessas propriedades te interessa? Você pode:',
              schedule: '✅ Deixar seus dados de contato',
              other: '🔍 Ver outras opções'
            }
          };

          const texts = buttonTexts[buttonLanguage] || buttonTexts.es;

          return (
            <div className="action-buttons">
              <p className="action-prompt">{texts.prompt}</p>
              <button
                className="action-button primary"
                onClick={handleAgendarVisita}
              >
                {texts.schedule}
              </button>
              <button
                className="action-button secondary"
                onClick={handleVerOtrasOpciones}
              >
                {texts.other}
              </button>
            </div>
          );
        })()}
      </div>
    );
  };

  // Estilos dinámicos basados en config
  const hexToRgb = (hex) => {
    const r = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return r ? `${parseInt(r[1], 16)}, ${parseInt(r[2], 16)}, ${parseInt(r[3], 16)}` : '37, 99, 235';
  };

  const dynamicStyles = {
    '--primary-color': primaryColor,
    '--primary-color-rgb': hexToRgb(primaryColor),
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
          onMouseDown={(e) => e.preventDefault()}
          tabIndex="-1"
          aria-label="Abrir chat"
          style={{ backgroundColor: primaryColor }}
        >
          <img src="https://inmobot-widget.vercel.app/inmobot-logo.jpg" alt="InmoBot" className="chat-icon-logo" />
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
                <img src="https://inmobot-widget.vercel.app/inmobot-logo.jpg" alt="InmoBot" />
              </div>
              <div className="bot-info">
                <h3 className="bot-name">{botName}</h3>
                <span className="bot-status">
                  <span className={`status-dot${botEnabled ? '' : ' disabled'}`}></span>
                  {botEnabled ? 'En línea' : 'No disponible'}
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
                </div>
                <span className="message-time">{formatTime(message.timestamp)}</span>
              </div>
            ))}

            {/* Typing indicator */}
            {isTyping && (
              <div className="message bot typing">
                <div className="typing-container">
                  <img
                    src="https://inmobot-widget.vercel.app/inmobot-logo.jpg"
                    alt="InmoBot"
                    className="typing-avatar"
                  />
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input o Formulario de Contacto */}
          {showContactForm ? (
            <div className="contact-form-container">
              <div className="contact-form-header">
                <h4>📋 Dejanos tus datos</h4>
                <button
                  className="close-form-button"
                  onClick={() => setShowContactForm(false)}
                  aria-label="Cerrar formulario"
                >
                  ✕
                </button>
              </div>
              <p className="contact-form-subtitle">Te contactamos a la brevedad</p>
              <form onSubmit={handleSubmitContactForm} className="contact-form">
                <div className="form-group">
                  <label htmlFor="nombre">Nombre completo *</label>
                  <input
                    type="text"
                    id="nombre"
                    value={contactFormData.nombre}
                    onChange={(e) => handleContactFormChange('nombre', e.target.value)}
                    placeholder="Juan Pérez"
                    required
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="telefono">Teléfono *</label>
                  <input
                    type="tel"
                    id="telefono"
                    value={contactFormData.telefono}
                    onChange={(e) => handleContactFormChange('telefono', e.target.value)}
                    placeholder="+54 9 11 1234-5678"
                    required
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="disponibilidad">Disponibilidad horaria (opcional)</label>
                  <input
                    type="text"
                    id="disponibilidad"
                    value={contactFormData.disponibilidad}
                    onChange={(e) => handleContactFormChange('disponibilidad', e.target.value)}
                    placeholder="Ej: Lunes a viernes 14-18hs"
                  />
                </div>
                <button type="submit" className="submit-form-button">
                  Enviar solicitud
                </button>
              </form>
            </div>
          ) : (
            <div className="chat-input-container">
              <textarea
                ref={inputRef}
                className="chat-input"
                placeholder={botEnabled ? placeholderText : 'El servicio no está disponible'}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                rows="1"
                disabled={isTyping || !botEnabled}
              />
              <button
                className="send-button"
                onClick={sendMessage}
                disabled={!inputValue.trim() || isTyping || !botEnabled}
                aria-label="Enviar mensaje"
              >
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                </svg>
              </button>
            </div>
          )}

          {/* Footer */}
          <div className="chat-footer">
            <a href="https://www.automatizacionia.com.ar" target="_blank" rel="noopener noreferrer" className="powered-by">
              Powered by AutomatizacionIA
            </a>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatWidget;
