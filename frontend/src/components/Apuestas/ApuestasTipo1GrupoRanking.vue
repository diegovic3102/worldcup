<template>
  <section class="panel">
    <header class="panel-header">
      <h2>Grupo E - Posiciones al final de fase</h2>
      <p class="panel-sub">
        Predice el ranking (1º..4º)
      </p>
    </header>

    <div v-if="officialResultDefined" class="state-msg state-ok">
      Resultado oficial definido.
    </div>

    <form class="form" @submit.prevent="save">

      <div class="grid">
        <label>
          1º
          <select v-model="prediction.pos1" :disabled="officialResultDefined">
            <option value="">Selecciona…</option>
            <option v-for="team in groupTeams" :key="team.codigo_fifa" :value="team.codigo_fifa">
              {{ team.nombre }} ({{ team.codigo_fifa }})
            </option>
          </select>
        </label>

        <label>
          2º
          <select v-model="prediction.pos2" :disabled="officialResultDefined">
            <option value="">Selecciona…</option>
            <option v-for="team in groupTeams" :key="team.codigo_fifa" :value="team.codigo_fifa">
              {{ team.nombre }} ({{ team.codigo_fifa }})
            </option>
          </select>
        </label>

        <label>
          3º
          <select v-model="prediction.pos3" :disabled="officialResultDefined">
            <option value="">Selecciona…</option>
            <option v-for="team in groupTeams" :key="team.codigo_fifa" :value="team.codigo_fifa">
              {{ team.nombre }} ({{ team.codigo_fifa }})
            </option>
          </select>
        </label>

        <label>
          4º
          <select v-model="prediction.pos4" :disabled="officialResultDefined">
            <option value="">Selecciona…</option>
            <option v-for="team in groupTeams" :key="team.codigo_fifa" :value="team.codigo_fifa">
              {{ team.nombre }} ({{ team.codigo_fifa }})
            </option>
          </select>
        </label>
      </div>

      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

      <button
        class="submit"
        type="submit"
        :disabled="officialResultDefined || hasSavedPrediction || hasCompletedPrediction"

      >
        Guardar predicción
      </button>

    </form>

    <div class="divider" />

    <div class="leaderboard">
      <div class="leaderboard-header">
        <h3>Leaderboard</h3>
        <button
          v-if="isAdmin"
          type="button"
          class="admin-button"
          @click="defineOfficialResult"
          :disabled="!canAdminDefine"
        >
          Definir resultados
        </button>
      </div>

      <div v-if="loading" class="state-msg">Cargando…</div>
      <div v-else-if="leaderboard.length === 0" class="state-msg">Sin datos todavía.</div>
      <ul v-else class="list">
        <li v-for="row in leaderboard" :key="row.userId">
          <span class="pos">{{ row.position }}</span>
          <span class="user">{{ row.userName }}</span>
          <strong class="score">{{ row.score }}</strong>
        
          <div v-if="!isAdmin" class="row-body">
            <div class="team-pos">
              <span>1º</span>
              <strong>{{ row.pos1_codigo_fifa || '—' }}</strong>
            </div>
            <div class="team-pos">
              <span>2º</span>
              <strong>{{ row.pos2_codigo_fifa || '—' }}</strong>
            </div>
            <div class="team-pos">
              <span>3º</span>
              <strong>{{ row.pos3_codigo_fifa || '—' }}</strong>
            </div>
            <div class="team-pos">
              <span>4º</span>
              <strong>{{ row.pos4_codigo_fifa || '—' }}</strong>
            </div>
          </div>
        </li>
      </ul>
    </div>
  </section>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import type { AppUser, ApiEquipo } from '../../types';

type Grupo = 'E';

type GroupRankingPredictionPayload = {
  grupo: Grupo;
  pos1_codigo_fifa: string;
  pos2_codigo_fifa: string;
  pos3_codigo_fifa: string;
  pos4_codigo_fifa: string;
};

type DefineOfficialResultPayload = {
  grupo: Grupo;
  pos1_codigo_fifa: string;
  pos2_codigo_fifa: string;
  pos3_codigo_fifa: string;
  pos4_codigo_fifa: string;
};

type LeaderboardRow = {
  id?: number;
  userId: number;
  userName: string;
  score: string;
  position: number;
  grupo: string;
  pos1_codigo_fifa: string;
  pos2_codigo_fifa: string;
  pos3_codigo_fifa: string;
  pos4_codigo_fifa: string;
};




export default defineComponent({
  name: 'ApuestasTipo1GrupoRanking',
  props: {
    currentUser: {
      type: Object as () => AppUser | null,
      required: true,
    },
  },
  data() {
    return {
      groupTeams: [] as ApiEquipo[],
      prediction: {
        pos1: '',
        pos2: '',
        pos3: '',
        pos4: '',
      },
      officialResultDefined: false,
      myScore: null as string | null,
      hasSavedPrediction: false,
      hasCompletedPrediction: false,


      loading: false,


      errorMessage: '',
      leaderboard: [] as LeaderboardRow[],
    };
  },
  computed: {
    isAdmin(): boolean {
      return Boolean(this.currentUser?.es_administrador);
    },
    canAdminDefine(): boolean {
      // Para la versión inicial: admin define manualmente un ejemplo.
      return true;
    },
  },
  mounted() {
    this.init();
  },
  methods: {
    async init() {
      await this.loadTeams();
      await this.loadMyPredictionIfAny();
      await this.loadLeaderboard();
      this.hasCompletedPrediction = this.prediction.pos1 !== '' &&
        this.prediction.pos2 !== '' &&
        this.prediction.pos3 !== '' &&
        this.prediction.pos4 !== '';

    },
    async loadTeams() {
      const res = await fetch('/api/equipos');
      const equipos = (await res.json()) as ApiEquipo[];
      this.groupTeams = equipos.filter((e) => e.grupo === 'E');
    },
    async loadMyPredictionIfAny() {
      if (!this.currentUser) return;
      const userId = this.currentUser.id;

      const res = await fetch(`/api/apuestas/tipo1/grupo-ranking/me?grupo=E&usuarioId=${userId}`);
      if (!res.ok) return;

      const data = await res.json();

      // Aunque no haya puntos calculados, sí mostramos/precargamos la predicción
      // para que el usuario vea y pueda editar su apuesta.
      this.prediction.pos1 = data?.pos1_codigo_fifa ?? '';
      this.prediction.pos2 = data?.pos2_codigo_fifa ?? '';
      this.prediction.pos3 = data?.pos3_codigo_fifa ?? '';
      this.prediction.pos4 = data?.pos4_codigo_fifa ?? '';

      if (data && data.puntos_obtenidos !== null && data.puntos_obtenidos !== undefined) {
        this.myScore = String(data.puntos_obtenidos);
      }
    },

    async loadLeaderboard() {
      // Admin ve el leaderboard completo; usuario normal solo su propia fila.
      this.loading = true;
      try {
        let res: Response;
        if (this.isAdmin) {
          res = await fetch(`/api/apuestas/tipo1/grupo-ranking/leaderboard?grupo=E`);
        } else {
          res = await fetch(
            `/api/apuestas/tipo1/grupo-ranking/me?grupo=E&usuarioId=${this.currentUser?.id ?? ''}`,
          );
        }

        if (!res.ok) {
          this.leaderboard = [];
          return;
        }

        if (this.isAdmin) {
          const data = await res.json();
          this.leaderboard = (data.items || []).map((r: any, i: number) => ({
            userId: r.user_id,
            userName: r.user_name,
            score: String(r.score),
            position: i + 1,
            grupo: 'E',
            pos1_codigo_fifa: r.pos1_codigo_fifa ?? '',
            pos2_codigo_fifa: r.pos2_codigo_fifa ?? '',
            pos3_codigo_fifa: r.pos3_codigo_fifa ?? '',
            pos4_codigo_fifa: r.pos4_codigo_fifa ?? '',
          }));

          this.officialResultDefined = Boolean(data.official_defined);
        } else {
          const data = await res.json();

          // Para usuarios normales, siempre mostramos su fila aunque no haya puntos calculados.
          const score = data?.puntos_obtenidos ?? null;
          this.leaderboard = [
            {
              userId: this.currentUser?.id ?? -1,
              userName: this.currentUser?.nombres
                ? `${this.currentUser.nombres} ${this.currentUser.apellidos || ''}`.trim() || this.currentUser?.usuario || ''
                : this.currentUser?.usuario || '',
              score: score === null ? '—' : String(score),
              position: 1,
              grupo: 'E',
              pos1_codigo_fifa: data?.pos1_codigo_fifa ?? '',
              pos2_codigo_fifa: data?.pos2_codigo_fifa ?? '',
              pos3_codigo_fifa: data?.pos3_codigo_fifa ?? '',
              pos4_codigo_fifa: data?.pos4_codigo_fifa ?? '',
            },
          ];
          this.officialResultDefined = false;
        }


        this.errorMessage = '';
      } finally {
        this.loading = false;
      }
    },

    validatePrediction(): string | null {
      const values = [
        this.prediction.pos1,
        this.prediction.pos2,
        this.prediction.pos3,
        this.prediction.pos4,
      ];

      if (values.some((v) => !v)) return 'Completa todas las posiciones.';
      const unique = new Set(values);
      if (unique.size !== 4) return 'No repitas equipos en el ranking.';
      return null;
    },
    async save() {
      this.errorMessage = '';
      const msg = this.validatePrediction();
      if (msg) {
        this.errorMessage = msg;
        return;
      }

      if (!this.currentUser) return;

      const payload: GroupRankingPredictionPayload = {
        grupo: 'E',
        pos1_codigo_fifa: this.prediction.pos1,
        pos2_codigo_fifa: this.prediction.pos2,
        pos3_codigo_fifa: this.prediction.pos3,
        pos4_codigo_fifa: this.prediction.pos4,
      };

      const userId = this.currentUser.id;
      const res = await fetch(`/api/apuestas/tipo1/grupo-ranking/me?grupo=E&usuarioId=${userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });


      let data: any = null;
      try {
        data = await res.json();
      } catch {
        // Si el backend devuelve HTML (500) u otro formato, evita romper el flujo.
        const txt = await res.text();
        data = { message: txt };
      }

      if (!res.ok) {
        this.errorMessage = data?.message || 'No se pudo guardar.';
        return;
      }

      await this.loadMyPredictionIfAny();
      await this.loadLeaderboard();

    },
    async defineOfficialResult() {
      // Para no bloquearte con UI de selección oficial todavía:
      // admin pone un ejemplo editable; cuando conectemos tablas reales lo hacemos bien.
      if (!this.currentUser?.es_administrador) return;

      const payload: DefineOfficialResultPayload = {
        grupo: 'E',
        // Debe coincidir EXACTAMENTE con los códigos FIFA usados en las apuestas:
        // GER, CIV, ECU, CUW
        pos1_codigo_fifa: 'GER',
        pos2_codigo_fifa: 'CIV',
        pos3_codigo_fifa: 'ECU',
        pos4_codigo_fifa: 'CUW',
      };

      const res = await fetch(`/api/apuestas/tipo1/grupo-ranking/define-official?usuarioId=${this.currentUser.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });


      const data = await res.json();
      if (!res.ok) {
        window.alert(data?.message || 'No se pudo definir resultados');
        return;
      }

      await this.loadLeaderboard();
    },
  },
});
</script>

<style scoped>
.panel {
  background: #fff;
  border: 1px solid #d9e2ec;
  border-radius: 8px;
  box-shadow: 0 18px 45px rgba(15, 23, 42, 0.08);
  padding: 24px;
}

.panel-header {
  margin-bottom: 18px;
}

.panel-header h2 {
  color: #102033;
  font-size: 1.35rem;
  margin: 0;
}

.panel-sub {
  color: #536171;
  font-size: 1rem;
  line-height: 1.5;
  margin: 10px 0 0;
  font-weight: 700;
}

.state-msg {
  background: #fff;
  border: 1px solid #d9e2ec;
  border-radius: 8px;
  color: #536171;
  font-weight: 700;
  margin: 0 0 16px;
  padding: 14px;
}

.state-ok {
  border-color: #99f6e4;
  background: #ecfdf5;
  color: #0f766e;
}

.state-msg.state-error,
.error-message {
  background: #fee2e2;
  border-color: #fecaca;
  color: #991b1b;
}

.form {
  display: grid;
  gap: 14px;
}

.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

label {
  color: #334155;
  display: grid;
  font-size: 0.88rem;
  font-weight: 800;
  gap: 8px;
}

select {
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  color: #102033;
  font: inherit;
  font-weight: 700;
  min-height: 46px;
  padding: 0 12px;
}

select:focus {
  border-color: #0f766e;
  outline: 3px solid rgba(15, 118, 110, 0.16);
}

.error-message {
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 700;
  padding: 12px;
  margin: 0;
}

button.submit {
  background: #0f766e;
  border: 0;
  border-radius: 8px;
  color: #fff;
  cursor: pointer;
  font-weight: 800;
  min-height: 48px;
}

button.submit:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}

.divider {
  height: 1px;
  background: #e2e8f0;
  margin: 18px 0;
}

.leaderboard {
  display: grid;
  gap: 12px;
}

.leaderboard-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.leaderboard-header h3 {
  color: #102033;
  margin: 0;
  font-size: 1.1rem;
}

.admin-button {
  background: #edf2f7;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  color: #102033;
  cursor: pointer;
  font-weight: 900;
  min-height: 42px;
  padding: 0 14px;
}

.admin-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 12px;
}

.list li {
  align-items: center;
  background: rgba(15, 118, 110, 0.08);
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  min-height: 46px;
  padding: 10px 12px;
  border: 1px solid rgba(15, 118, 110, 0.14);
}

.pos {
  color: #0f766e;
  font-weight: 900;
}

.user {
  color: #334155;
  font-weight: 900;
}

.score {
  color: #102033;
  font-size: 1.05rem;
}

@media (max-width: 720px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>



