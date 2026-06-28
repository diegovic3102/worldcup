<template>
  <main class="auth-page">
    <section class="auth-copy">
      <p class="eyebrow">Polla Mundialista - Sucesores</p>
      <h1>{{ title }}</h1>
    </section>

    <section class="auth-panel" aria-label="Acceso de usuario">
      <div class="mode-switch" role="tablist" aria-label="Modo de acceso">
        <button
          :class="{ active: mode === 'login' }"
          type="button"
          @click="setMode('login')"
        >
          Iniciar sesion
        </button>
        <button
          :class="{ active: mode === 'register' }"
          type="button"
          @click="setMode('register')"
        >
          Registrarse
        </button>
      </div>

      <form @submit.prevent="submit">
        <label v-if="mode === 'register'">
          Nombres
          <input v-model.trim="nombres" autocomplete="given-name" type="text" />
        </label>

        <label v-if="mode === 'register'">
          Apellidos
          <input v-model.trim="apellidos" autocomplete="family-name" type="text" />
        </label>

        <label>
          Usuario
          <input v-model.trim="usuario" autocomplete="username" type="text" />
        </label>

        <label>
          Contraseña
          <input
            v-model="password"
            autocomplete="current-password"
            placeholder="Minimo 6 caracteres"
            type="password"
          />
        </label>

        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

        <button class="submit-button" type="submit">{{ submitLabel }}</button>
      </form>
    </section>
  </main>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

type AuthMode = 'login' | 'register';

interface AuthSubmitPayload {
  mode: AuthMode;
  usuario: string;
  contrasena: string;
  nombres: string;
  apellidos: string;
}

export default defineComponent({
  name: 'AuthPanel',
  emits: ['submit-auth'],
  data() {
    return {
      mode: 'login' as AuthMode,
      nombres: '',
      apellidos: '',
      usuario: '',
      password: '',
      errorMessage: '',
    };
  },
  computed: {
    title(): string {
      return this.mode === 'login' ? 'Entra a tus apuestas' : 'Crea tu cuenta';
    },
    submitLabel(): string {
      return this.mode === 'login' ? 'Iniciar sesion' : 'Crear cuenta';
    },
  },
  methods: {
    setMode(mode: AuthMode) {
      this.mode = mode;
      this.errorMessage = '';
    },
    submit() {
      const normalizedUsuario = this.usuario.toLowerCase();

      if (!normalizedUsuario || !this.password) {
        this.errorMessage = 'Completa usuario y contrasena.';
        return;
      }

      if (this.password.length < 6) {
        this.errorMessage = 'La contrasena debe tener al menos 6 caracteres.';
        return;
      }

      if (this.mode === 'register' && !this.nombres) {
        this.errorMessage = 'Ingresa tus nombres para registrarte.';
        return;
      }

      this.errorMessage = '';
      this.$emit('submit-auth', {
        mode: this.mode,
        usuario: normalizedUsuario,
        contrasena: this.password,
        nombres: this.nombres,
        apellidos: this.apellidos,
      } as AuthSubmitPayload);
    },
  },
});
</script>

<style scoped>
.auth-page {
  align-items: center;
  display: grid;
  gap: 36px;
  grid-template-columns: minmax(0, 1fr) 420px;
  min-height: 100vh;
  padding: 48px 0;
}

.auth-copy {
  max-width: 660px;
}

.eyebrow {
  color: #0f766e;
  font-size: 0.78rem;
  font-weight: 800;
  margin: 0 0 10px;
  text-transform: uppercase;
}

h1 {
  color: #102033;
  font-size: clamp(2.4rem, 5vw, 4.6rem);
  line-height: 1;
  margin: 0;
}

.auth-copy p:not(.eyebrow) {
  color: #536171;
  font-size: 1.05rem;
  line-height: 1.65;
  margin: 18px 0 0;
}

.auth-panel {
  background: #fff;
  border: 1px solid #d9e2ec;
  border-radius: 8px;
  box-shadow: 0 18px 45px rgba(15, 23, 42, 0.1);
  padding: 24px;
}

.mode-switch {
  background: #edf2f7;
  border-radius: 8px;
  display: grid;
  gap: 4px;
  grid-template-columns: 1fr 1fr;
  margin-bottom: 22px;
  padding: 4px;
}

.mode-switch button {
  background: transparent;
  border: 0;
  border-radius: 6px;
  color: #64748b;
  cursor: pointer;
  font-weight: 800;
  min-height: 42px;
}

.mode-switch button.active {
  background: #fff;
  color: #102033;
  box-shadow: 0 6px 16px rgba(15, 23, 42, 0.08);
}

form {
  display: grid;
  gap: 16px;
}

label {
  color: #334155;
  display: grid;
  font-size: 0.88rem;
  font-weight: 800;
  gap: 8px;
}

input {
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  color: #102033;
  font: inherit;
  min-height: 46px;
  padding: 0 12px;
}

input:focus {
  border-color: #0f766e;
  outline: 3px solid rgba(15, 118, 110, 0.16);
}

.error-message {
  background: #fee2e2;
  border-radius: 8px;
  color: #991b1b;
  font-size: 0.9rem;
  font-weight: 700;
  margin: 0;
  padding: 12px;
}

.submit-button {
  background: #0f766e;
  border: 0;
  border-radius: 8px;
  color: #fff;
  cursor: pointer;
  font-weight: 800;
  min-height: 48px;
}

@media (max-width: 860px) {
  .auth-page {
    align-items: stretch;
    grid-template-columns: 1fr;
    min-height: auto;
  }
}
</style>
