<template>
  <div class="app-shell">
    <AuthPanel v-if="!currentUser" @submit-auth="handleAuth" />

    <template v-else>
      <AppHeader
        :saved-count="savedCount"
        :user-name="userDisplayName"
        @logout="logout"
      />

      <section class="type1-apuestas" aria-label="Apuestas Tipo 1" v-if="currentUser">
        <ApuestasTipo1GrupoRanking :current-user="currentUser" />
      </section>

      <section class="type2-apuestas" aria-label="Apuestas Tipo 2" v-if="currentUser">
        <ApuestasTipo2SegundaFaseEcuadorMarcadores :current-user="currentUser" />
      </section>

    </template>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import AppHeader from './components/AppHeader.vue';
import AuthPanel from './components/AuthPanel.vue';
import ApuestasTipo1GrupoRanking from './components/Apuestas/ApuestasTipo1GrupoRanking.vue';
import ApuestasTipo2SegundaFaseEcuadorMarcadores from './components/Apuestas/ApuestasTipo2SegundaFaseEcuadorMarcadores.vue';
import type { AppUser, Prediction } from './types';




const SESSION_KEY = 'sucesores-worldcup.session';
const PREDICTIONS_KEY_PREFIX = 'sucesores-worldcup.predictions';
const API_BASE_URL = '/worldcup/api';

type AuthMode = 'login' | 'register';

interface AuthSubmitPayload {
  mode: AuthMode;
  usuario: string;
  contrasena: string;
  nombres: string;
  apellidos: string;
}

interface AuthResponse {
  usuario: AppUser;
  message?: string;
}

export default defineComponent({
  name: 'App',
  components: {
    AppHeader,
    AuthPanel,
    ApuestasTipo1GrupoRanking,
    ApuestasTipo2SegundaFaseEcuadorMarcadores,
  },


  data() {
    return {
      partidos: [] as any[],

      selectedGroup: '' as string,
      loadingMatches: false,
      matchesError: '',
      currentUser: null as AppUser | null,
    predictions: {} as Record<string, Prediction>,

    };
  },
  computed: {
    savedCount(): number {
      return Object.keys(this.predictions).length;
    },
    userDisplayName(): string {
      if (!this.currentUser) {
        return '';
      }

      return `${this.currentUser.nombres} ${this.currentUser.apellidos || ''}`.trim()
        || this.currentUser.usuario;
    },
  },
  mounted() {
    this.currentUser = this.readSession();

    if (this.currentUser) {
      this.loadPredictions();
    }
  },
  methods: {
    async handleAuth(payload: AuthSubmitPayload) {
      const endpoint = payload.mode === 'login' ? 'login' : 'register';
      let response: Response;
      let data: AuthResponse;

      try {
        response = await fetch(`${API_BASE_URL}/auth/${endpoint}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        });
        data = await response.json() as AuthResponse;
      } catch {
        window.alert('No se pudo conectar con el servidor.');
        return;
      }

      if (!response.ok) {
        window.alert(data.message || 'No se pudo completar el acceso.');
        return;
      }

      this.startSession(data.usuario);
    },

    loadPredictions() {
      if (!this.currentUser) {
        this.predictions = {};
        return;
      }

      const storageKey = this.predictionsStorageKey(String(this.currentUser.id));
      const storedPredictions = window.localStorage.getItem(storageKey);

      if (!storedPredictions) {
        this.predictions = {};
        return;
      }

      try {
        this.predictions = JSON.parse(storedPredictions);
      } catch {
        this.predictions = {};
        window.localStorage.removeItem(storageKey);
      }
    },
    logout() {
      window.localStorage.removeItem(SESSION_KEY);
      this.currentUser = null;
      this.predictions = {};
    },
    predictionsStorageKey(userId: string): string {
      return `${PREDICTIONS_KEY_PREFIX}.${userId}`;
    },
    readSession(): AppUser | null {
      const storedSession = window.localStorage.getItem(SESSION_KEY);

      if (!storedSession) {
        return null;
      }

      try {
        const parsedSession = JSON.parse(storedSession) as AppUser;

        if (
          typeof parsedSession.id !== 'number'
          || !parsedSession.usuario
          || !parsedSession.nombres
        ) {
          window.localStorage.removeItem(SESSION_KEY);
          return null;
        }

        return parsedSession;
      } catch {
        window.localStorage.removeItem(SESSION_KEY);
        return null;
      }
    },
    savePrediction(prediction: Prediction) {
      if (!this.currentUser) {
        return;
      }

      this.predictions = {
        ...this.predictions,
        [prediction.matchId]: prediction,
      };

      window.localStorage.setItem(
        this.predictionsStorageKey(String(this.currentUser.id)),
        JSON.stringify(this.predictions),
      );
    },
    startSession(user: AppUser) {
      this.currentUser = {
        id: user.id,
        usuario: user.usuario,
        nombres: user.nombres,
        apellidos: user.apellidos,
        es_administrador: user.es_administrador,
      };
      window.localStorage.setItem(SESSION_KEY, JSON.stringify(this.currentUser));
      this.loadPredictions();
    
      // Dentro de este proyecto, la UI de Apuestas carga los partidos/teams
      // desde sus propios endpoints. Evitamos llamar a funciones no existentes.
    
    },
  },
});
</script>

<style>
* {
  box-sizing: border-box;
}

body {
  background: #edf2f7;
  margin: 0;
}

#app {
  color: #102033;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.app-shell {
  margin: 0 auto;
  max-width: 1180px;
  padding: 0 24px 48px;
}

.main-layout {
  align-items: start;
  display: grid;
  gap: 24px;
  grid-template-columns: minmax(0, 1fr) 320px;
}

.matches-section {
  display: grid;
  gap: 18px;
}

.section-heading {
  align-items: end;
  display: flex;
  justify-content: space-between;
}

.section-heading p {
  color: #0f766e;
  font-size: 0.78rem;
  font-weight: 800;
  margin: 0 0 6px;
  text-transform: uppercase;
}

.section-heading h2 {
  color: #102033;
  font-size: 1.5rem;
  margin: 0;
}

.section-heading span {
  color: #64748b;
  font-weight: 700;
}

.group-picker {
  color: #334155;
  display: grid;
  font-size: 0.78rem;
  font-weight: 800;
  gap: 6px;
  text-transform: uppercase;
}

.group-picker select {
  background: #fff;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  color: #102033;
  font: inherit;
  font-weight: 700;
  min-height: 44px;
  min-width: 160px;
  padding: 0 12px;
}

.group-picker select:focus {
  border-color: #0f766e;
  outline: 3px solid rgba(15, 118, 110, 0.16);
}

.state-msg {
  background: #fff;
  border: 1px solid #d9e2ec;
  border-radius: 8px;
  color: #536171;
  font-weight: 700;
  margin: 0;
  padding: 20px;
}

.state-error {
  background: #fee2e2;
  border-color: #fecaca;
  color: #991b1b;
}

.match-list {
  display: grid;
  gap: 16px;
}

@media (max-width: 980px) {
  .main-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .app-shell {
    padding: 0 16px 32px;
  }

  .section-heading {
    align-items: flex-start;
    flex-direction: column;
    gap: 8px;
  }
}

.type1-apuestas {
  margin-top: 24px;
}
</style>
