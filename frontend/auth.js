// Configuración de la API
if (!window.API_URL) {
  window.API_URL = 'http://127.0.0.1:5000/api';
}

// Utilidades para manejo de tokens
const AuthService = {
  setToken(token) {
    localStorage.setItem('activate_token', token);
  },

  getToken() {
    return localStorage.getItem('activate_token');
  },

  removeToken() {
    localStorage.removeItem('activate_token');
    localStorage.removeItem('activate_user');
  },

  setUser(user) {
    localStorage.setItem('activate_user', JSON.stringify(user));
  },

  getUser() {
    const user = localStorage.getItem('activate_user');
    return user ? JSON.parse(user) : null;
  },

  isAuthenticated() {
    return !!this.getToken();
  },

  async verifyToken() {
    const token = this.getToken();
    if (!token) return false;

    try {
      const response = await fetch(`${API_URL}/auth/verify`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        return data.success;
      }
      return false;
    } catch (error) {
      console.error('Error verificando token:', error);
      return false;
    }
  }
};

// Manejo del formulario de login
if (document.getElementById('loginForm')) {
  const loginForm = document.getElementById('loginForm');
  const submitBtn = document.getElementById('submitBtn');
  const errorMessage = document.getElementById('errorMessage');
  const successMessage = document.getElementById('successMessage');

  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const remember = document.getElementById('remember').checked;

    // Limpiar mensajes
    errorMessage.style.display = 'none';
    successMessage.style.display = 'none';

    // Deshabilitar botón y mostrar loading
    submitBtn.disabled = true;
    submitBtn.classList.add('loading');

    try {
      const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
      });

      const data = await response.json();

      if (data.success) {
        // Guardar token y usuario
        AuthService.setToken(data.data.token);
        AuthService.setUser(data.data.user);

        // Mostrar mensaje de éxito
        successMessage.textContent = '¡Login exitoso! Redirigiendo...';
        successMessage.style.display = 'block';

        // Redirigir después de 1 segundo
        setTimeout(() => {
          window.location.href = 'index.html';
        }, 1000);
      } else {
        errorMessage.textContent = data.message || 'Error al iniciar sesión';
        errorMessage.style.display = 'block';
        submitBtn.disabled = false;
        submitBtn.classList.remove('loading');
      }
    } catch (error) {
      console.error('Error:', error);
      errorMessage.textContent = 'Error de conexión. Verifica que el servidor esté ejecutándose.';
      errorMessage.style.display = 'block';
      submitBtn.disabled = false;
      submitBtn.classList.remove('loading');
    }
  });
}

// Manejo del formulario de registro
if (document.getElementById('registerForm')) {
  const registerForm = document.getElementById('registerForm');
  const submitBtn = document.getElementById('submitBtn');
  const errorMessage = document.getElementById('errorMessage');
  const successMessage = document.getElementById('successMessage');

  registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;

    // Limpiar mensajes
    errorMessage.style.display = 'none';
    successMessage.style.display = 'none';

    // Validar contraseñas
    if (password !== confirmPassword) {
      errorMessage.textContent = 'Las contraseñas no coinciden';
      errorMessage.style.display = 'block';
      return;
    }

    // Validar formato de contraseña
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{6,}$/;
    if (!passwordRegex.test(password)) {
      errorMessage.textContent = 'La contraseña debe tener al menos 6 caracteres, incluir mayúscula, minúscula y número';
      errorMessage.style.display = 'block';
      return;
    }

    // Deshabilitar botón y mostrar loading
    submitBtn.disabled = true;
    submitBtn.classList.add('loading');

    try {
      const response = await fetch(`${API_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, email, password })
      });

      const data = await response.json();

      if (data.success) {
        // Guardar token y usuario
        AuthService.setToken(data.data.token);
        AuthService.setUser(data.data.user);

        // Mostrar mensaje de éxito
        successMessage.textContent = '¡Cuenta creada exitosamente! Redirigiendo...';
        successMessage.style.display = 'block';

        // Redirigir después de 1 segundo
        setTimeout(() => {
          window.location.href = 'index.html';
        }, 1000);
      } else {
        // Mostrar errores de validación
        if (data.errors && data.errors.length > 0) {
          errorMessage.innerHTML = data.errors.map(err => `• ${err.message}`).join('<br>');
        } else {
          errorMessage.textContent = data.message || 'Error al crear cuenta';
        }
        errorMessage.style.display = 'block';
        submitBtn.disabled = false;
        submitBtn.classList.remove('loading');
      }
    } catch (error) {
      console.error('Error:', error);
      errorMessage.textContent = 'Error de conexión. Verifica que el servidor esté ejecutándose.';
      errorMessage.style.display = 'block';
      submitBtn.disabled = false;
      submitBtn.classList.remove('loading');
    }
  });
}

// Actualizar navbar según estado de autenticación
function updateNavbar() {
  const navUser = document.querySelector('.nav-user');
  if (!navUser) return;

  if (AuthService.isAuthenticated()) {
    const user = AuthService.getUser();
    navUser.innerHTML = `
      <div class="user-menu">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="12" cy="8" r="4" fill="currentColor"/>
          <path d="M4 20C4 16.6863 6.68629 14 10 14H14C17.3137 14 20 16.6863 20 20V21H4V20Z" fill="currentColor"/>
        </svg>
        <span class="user-name">${user.username}</span>
      </div>
    `;
    navUser.style.cursor = 'pointer';
    navUser.onclick = () => {
      if (confirm('¿Deseas cerrar sesión?')) {
        AuthService.removeToken();
        window.location.href = 'index.html';
      }
    };
  } else {
    navUser.onclick = () => {
      window.location.href = 'login.html';
    };
  }
}

// Ejecutar al cargar la página
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', updateNavbar);
} else {
  updateNavbar();
}
