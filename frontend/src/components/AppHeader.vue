<template>
  <header class="app-header">
    <div>
      <p class="eyebrow">Polla mundialista</p>
      <h1>Predicciones</h1>
    </div>
    <div class="header-actions">
      <div class="user-card">
        <small>Usuario</small>
        <strong>{{ userName }}</strong>
      </div>
      <button type="button" @click="$emit('logout')">Salir</button>
    </div>
  </header>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'AppHeader',
  props: {
    savedCount: {
      type: Number,
      required: true,
    },
    userName: {
      type: String,
      required: true,
    },
  },
  emits: ['logout'],
  computed: {
    savedLabel(): string {
      return this.savedCount === 1 ? 'prediccion' : 'predicciones';
    },
  },
});
</script>

<style scoped>
.app-header {
  align-items: center;
  display: flex;
  gap: 24px;
  justify-content: space-between;
  padding: 36px 0 28px;
}

.eyebrow {
  color: #0f766e;
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0;
  margin: 0 0 8px;
  text-transform: uppercase;
}

h1 {
  color: #102033;
  font-size: clamp(2rem, 4vw, 3.4rem);
  line-height: 1;
  margin: 0;
}

.subtitle {
  color: #536171;
  font-size: 1rem;
  line-height: 1.6;
  margin: 14px 0 0;
  max-width: 660px;
}

.summary-pill {
  align-items: center;
  background: #102033;
  border-radius: 8px;
  color: #fff;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  gap: 2px;
  min-width: 132px;
  padding: 16px;
}

.user-card {
  background: #102033;
  border: 1px solid #d9e2ec;
  border-radius: 8px;
  color: #fff;
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-width: 150px;
  padding: 12px 14px;
}

.header-actions {
  align-items: stretch;
  display: flex;
  flex-shrink: 0;
  gap: 10px;
}

.user-card small {
  color: #64748b;
  font-size: 0.72rem;
  font-weight: 800;
  text-transform: uppercase;
}

.user-card strong {
  color: #ffffff;
  font-size: 0.94rem;
  margin-top: 4px;
  overflow-wrap: anywhere;
}

button {
  background: #fff;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  color: #102033;
  cursor: pointer;
  font-weight: 800;
  padding: 0 16px;
}

.summary-pill span {
  font-size: 2rem;
  font-weight: 800;
}

.summary-pill small {
  color: #cbd5e1;
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
}

@media (max-width: 720px) {
  .app-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .summary-pill {
    align-items: flex-start;
    width: 100%;
  }

  .header-actions {
    display: grid;
    grid-template-columns: 1fr;
    width: 100%;
  }

  button {
    min-height: 42px;
  }
}
</style>
