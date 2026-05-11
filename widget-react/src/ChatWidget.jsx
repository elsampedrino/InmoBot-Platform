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
        leads: data.leads === true, // Solo true si explícitamente viene true del WF
        whatsapp: data.whatsapp_handoff || null
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

  // Manejar click en CTA WhatsApp
  const handleWhatsAppHandoffClick = (message) => {
    const clickUrl = apiUrl.replace(/\/chat$/, '/whatsapp-click');
    fetch(clickUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        item_id: message.propiedades?.[0]?.id || null,
        id_lead: message.whatsapp?.id_lead || null
      })
    }).catch(() => {});
    window.open(message.whatsapp.url, '_blank', 'noopener,noreferrer');
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

        {/* CTA WhatsApp handoff */}
        {message.whatsapp?.enabled && (
          <div className="whatsapp-handoff">
            <button
              className="whatsapp-handoff-button"
              onClick={() => handleWhatsAppHandoffClick(message)}
            >
              <svg width={16} height={16} viewBox="0 0 24 24" fill="currentColor">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
              </svg>
              Continuar por WhatsApp con {message.whatsapp.agent_name}
            </button>
          </div>
        )}

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
