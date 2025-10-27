// Chat de Ayuda con IA Simbólica
// Usar configuración global definida en auth.js: window.API_URL

const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');
const suggestionsContainer = document.getElementById('suggestions');

// Verificar autenticación al cargar
async function checkAuth() {
  if (!AuthService.isAuthenticated()) {
    showAuthRequired();
    return false;
  }

  const isValid = await AuthService.verifyToken();
  if (!isValid) {
    AuthService.removeToken();
    showAuthRequired();
    return false;
  }

  return true;
}

// Mostrar mensaje de autenticación requerida
function showAuthRequired() {
  chatMessages.innerHTML = `
    <div class="auth-required-message">
      <h2>🔒 Autenticación Requerida</h2>
      <p>Debes iniciar sesión para usar el chat de ayuda.</p>
      <a href="login.html" class="btn btn-google">Iniciar Sesión</a>
    </div>
  `;
  chatInput.disabled = true;
  sendBtn.disabled = true;
}

// Cargar sugerencias
async function loadSuggestions() {
  try {
    const token = AuthService.getToken();
    const response = await fetch(`${window.API_URL}/chat/suggestions`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    const data = await response.json();
    if (data.success) {
      displaySuggestions(data.data.suggestions);
    }
  } catch (error) {
    console.error('Error cargando sugerencias:', error);
  }
}

// Mostrar sugerencias
function displaySuggestions(suggestions) {
  suggestionsContainer.innerHTML = '';
  suggestions.forEach(suggestion => {
    const chip = document.createElement('div');
    chip.className = 'suggestion-chip';
    chip.textContent = suggestion;
    chip.onclick = () => {
      chatInput.value = suggestion;
      chatInput.focus();
    };
    suggestionsContainer.appendChild(chip);
  });
}

// Cargar historial de chat
async function loadChatHistory() {
  try {
    const token = AuthService.getToken();
    const response = await fetch(`${window.API_URL}/chat/history`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    const data = await response.json();
    if (data.success && data.data.messages.length > 0) {
      // Limpiar mensaje de bienvenida
      chatMessages.innerHTML = '';
      
      // Mostrar historial
      data.data.messages.forEach(msg => {
        addMessage(msg.message, 'user');
        addMessage(msg.response, 'bot');
      });
    }
  } catch (error) {
    console.error('Error cargando historial:', error);
  }
}

// Agregar mensaje al chat
function addMessage(text, sender) {
  const messageDiv = document.createElement('div');
  messageDiv.className = `message ${sender}-message`;

  const avatar = document.createElement('div');
  avatar.className = 'message-avatar';
  avatar.textContent = sender === 'bot' ? '🤖' : '👤';

  const content = document.createElement('div');
  content.className = 'message-content';
  content.innerHTML = `<p>${text}</p>`;

  messageDiv.appendChild(avatar);
  messageDiv.appendChild(content);
  chatMessages.appendChild(messageDiv);

  // Scroll al final
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Mostrar indicador de escritura
function showTypingIndicator() {
  const typingDiv = document.createElement('div');
  typingDiv.className = 'message bot-message typing-indicator';
  typingDiv.id = 'typingIndicator';

  const avatar = document.createElement('div');
  avatar.className = 'message-avatar';
  avatar.textContent = '🤖';

  const content = document.createElement('div');
  content.className = 'message-content';
  content.innerHTML = `
    <div class="typing-dot"></div>
    <div class="typing-dot"></div>
    <div class="typing-dot"></div>
  `;

  typingDiv.appendChild(avatar);
  typingDiv.appendChild(content);
  chatMessages.appendChild(typingDiv);

  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Remover indicador de escritura
function removeTypingIndicator() {
  const typingIndicator = document.getElementById('typingIndicator');
  if (typingIndicator) {
    typingIndicator.remove();
  }
}

// Enviar mensaje
async function sendMessage() {
  const message = chatInput.value.trim();
  if (!message) return;

  // Deshabilitar input
  chatInput.disabled = true;
  sendBtn.disabled = true;

  // Agregar mensaje del usuario
  addMessage(message, 'user');
  chatInput.value = '';

  // Mostrar indicador de escritura
  showTypingIndicator();

  try {
    const token = AuthService.getToken();
    const response = await fetch(`${window.API_URL}/chat/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ message })
    });

    const data = await response.json();

    // Remover indicador de escritura
    removeTypingIndicator();

    if (data.success) {
      // Agregar respuesta del bot
      addMessage(data.data.response, 'bot');
    } else {
      addMessage('Lo siento, hubo un error al procesar tu mensaje. Por favor intenta de nuevo.', 'bot');
    }
  } catch (error) {
    console.error('Error enviando mensaje:', error);
    removeTypingIndicator();
    addMessage('Error de conexión. Verifica que el servidor esté ejecutándose.', 'bot');
  } finally {
    // Habilitar input
    chatInput.disabled = false;
    sendBtn.disabled = false;
    chatInput.focus();
  }
}

// Event listeners
sendBtn.addEventListener('click', sendMessage);

chatInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

// Inicializar chat
(async function initChat() {
  const isAuthenticated = await checkAuth();
  if (isAuthenticated) {
    await loadSuggestions();
    await loadChatHistory();
  }
})();
