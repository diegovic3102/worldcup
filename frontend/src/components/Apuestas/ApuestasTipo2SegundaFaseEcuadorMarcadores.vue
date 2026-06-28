
<template>
  <section class="panel">
    <header class="panel-header">
      <h2>Segunda fase - Ecuador (marcadores)</h2>
      <p class="panel-sub">Pronostica: ECU vs Curazao, ECU vs Alemania, ECU vs Costa de Marfíl</p>
    </header>

    <div v-if="isAdmin" class="state-msg state-ok">
      Completadas por usuarios: <strong>{{ completedCount }}</strong>
    </div>

    <div v-else class="state-msg">
      Guarda tus marcadores para completar la fase.
    </div>

    <form class="form" @submit.prevent="save">
      <div class="match-block">
        <h4 class="match-title">Ecuador vs Curazao</h4>
        <div class="score-grid">
          <label class="score-with-flag">
            <img class="team-flag" :src="ecuImg" alt="ECU" />
            <input
              class="score-input"
              type="number"
              min="0"
              step="1"
              v-model.number="form.ecu_cur_local_goles"
              :disabled="hasCompletedPrediction"
            />
          </label>
          <label class="score-with-flag">
            <img class="team-flag" :src="cuwImg" alt="CUW" />
            <input
              class="score-input"
              type="number"
              min="0"
              step="1"
              v-model.number="form.ecu_cur_visitante_goles"
              :disabled="hasCompletedPrediction"
            />
          </label>

        </div>
      </div>

      <div class="match-block">
        <h4 class="match-title">Ecuador vs Alemania</h4>
        <div class="score-grid">
          <label class="score-with-flag">
            <img class="team-flag" :src="ecuImg" alt="ECU" />
            <input
              class="score-input"
              type="number"
              min="0"
              step="1"
              v-model.number="form.ecu_ger_local_goles"
              :disabled="hasCompletedPrediction"
            />
          </label>
          <label>
            <img class="team-flag" :src="gerImg" alt="GER" />
            Alemania
            <input
              class="score-input"
              type="number"
              min="0"
              step="1"
              v-model.number="form.ecu_ger_visitante_goles"
              :disabled="hasCompletedPrediction"
            />
          </label>
        </div>
      </div>

      <div class="match-block">
        <h4 class="match-title">Ecuador vs Costa de Marfíl</h4>
        <div class="score-grid">
          <label>
            <img class="team-flag" :src="ecuImg" alt="ECU" />
            <input
              class="score-input"
              type="number"
              min="0"
              step="1"
              v-model.number="form.ecu_civ_local_goles"
              :disabled="hasCompletedPrediction"
            />
          </label>
          <label>
            <img class="team-flag" :src="civImg" alt="CIV" />
            <input
              class="score-input"
              type="number"
              min="0"
              step="1"
              v-model.number="form.ecu_civ_visitante_goles"
              :disabled="hasCompletedPrediction"
            />
          </label>
        </div>
      </div>

      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

      <button
        class="submit"
        type="submit"
        :disabled="hasCompletedPrediction"
      >
        Guardar marcadores
      </button>

    </form>
  </section>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import type { AppUser } from '../../types';

import ecuImg from '../../assets/ECU.png';
import cuwImg from '../../assets/CUW.png';
import gerImg from '../../assets/GER.png';
import civImg from '../../assets/CIV.png';

// Aseguramos que el scope del componente tenga las propiedades usadas en el template

// Las banderas se renderizan en el template.

type SegundaFasePayload = {
  usuario_id: number;
  ecu_cur_local_goles: number | null;
  ecu_cur_visitante_goles: number | null;
  ecu_ger_local_goles: number | null;
  ecu_ger_visitante_goles: number | null;
  ecu_civ_local_goles: number | null;
  ecu_civ_visitante_goles: number | null;
};

type SegundaFaseResponse = {
  ecu_cur_local_goles: number | null;
  ecu_cur_visitante_goles: number | null;
  ecu_ger_local_goles: number | null;
  ecu_ger_visitante_goles: number | null;
  ecu_civ_local_goles: number | null;
  ecu_civ_visitante_goles: number | null;
};

export default defineComponent({
  name: 'ApuestasTipo2SegundaFaseEcuadorMarcadores',
  props: {
    currentUser: {
      type: Object as () => AppUser | null,
      required: true,
    },
  },
  data() {
    return {
      loading: false,
      errorMessage: '',
      completedCount: 0,
      hasCompletedPrediction: false,

      ecuImg,
      cuwImg,
      gerImg,
      civImg,
      form: {
        ecu_cur_local_goles: null as number | null,
        ecu_cur_visitante_goles: null as number | null,
        ecu_ger_local_goles: null as number | null,
        ecu_ger_visitante_goles: null as number | null,
        ecu_civ_local_goles: null as number | null,
        ecu_civ_visitante_goles: null as number | null,
      },
    };
  },
  computed: {
    isAdmin(): boolean {
      return Boolean(this.currentUser?.es_administrador);
    },
  },
  mounted() {
    this.init();
  },
  methods: {
    async init() {
      if (!this.currentUser) return;
      await this.loadMyPred();

      this.hasCompletedPrediction =
        this.form.ecu_cur_local_goles !== null &&
        this.form.ecu_cur_visitante_goles !== null &&
        this.form.ecu_ger_local_goles !== null &&
        this.form.ecu_ger_visitante_goles !== null &&
        this.form.ecu_civ_local_goles !== null &&
        this.form.ecu_civ_visitante_goles !== null;

      // Si el usuario ya tiene los 6 marcadores guardados, no puede editar nuevamente.
      // (El estado se calcula a partir de lo que retorna /me.)

      if (this.isAdmin) {
        await this.loadCompletedCount();
      }
    },

    async loadMyPred() {
      if (!this.currentUser) return;
      const userId = this.currentUser.id;
      const res = await fetch(
        `/worldcup/api/apuestas/tipo2/ecuador-marcadores/me?usuarioId=${userId}`,
      );
      if (!res.ok) return;
      const data = (await res.json()) as SegundaFaseResponse;
      this.form.ecu_cur_local_goles = data.ecu_cur_local_goles;
      this.form.ecu_cur_visitante_goles = data.ecu_cur_visitante_goles;
      this.form.ecu_ger_local_goles = data.ecu_ger_local_goles;
      this.form.ecu_ger_visitante_goles = data.ecu_ger_visitante_goles;
      this.form.ecu_civ_local_goles = data.ecu_civ_local_goles;
      this.form.ecu_civ_visitante_goles = data.ecu_civ_visitante_goles;
    },

    async loadCompletedCount() {
      if (!this.currentUser) return;
      const res = await fetch(
        `/worldcup/api/apuestas/tipo2/ecuador-marcadores/contador?usuarioId=${this.currentUser.id}`,
      );
      if (!res.ok) return;
      const data = await res.json();
      this.completedCount = Number(data?.completed_count ?? 0);
    },

    validate(): string | null {
      // Solo pedimos que sean números o null; la completitud la maneja el contador.
      return null;
    },

    async save() {
      this.errorMessage = '';
      if (!this.currentUser) return;

      const msg = this.validate();
      if (msg) {
        this.errorMessage = msg;
        return;
      }

      const payload: SegundaFasePayload = {
        usuario_id: this.currentUser.id,
        ecu_cur_local_goles: this.form.ecu_cur_local_goles,
        ecu_cur_visitante_goles: this.form.ecu_cur_visitante_goles,
        ecu_ger_local_goles: this.form.ecu_ger_local_goles,
        ecu_ger_visitante_goles: this.form.ecu_ger_visitante_goles,
        ecu_civ_local_goles: this.form.ecu_civ_local_goles,
        ecu_civ_visitante_goles: this.form.ecu_civ_visitante_goles,
      };

      // A nivel frontend evitamos el re-envío; el bloqueo real debe venir del backend.
      if (this.hasCompletedPrediction) {
        return;
      }


      const res = await fetch('/worldcup/api/apuestas/tipo2/ecuador-marcadores/me', {

        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        try {
          const data = await res.json();
          this.errorMessage = data?.message || 'No se pudo guardar.';
        } catch {
          this.errorMessage = 'No se pudo guardar.';
        }
        return;
      }

      await this.loadMyPred();
      if (this.isAdmin) {
        await this.loadCompletedCount();
      }
    },
  },
});
</script>

<style scoped>
.score-with-flag {
  display: grid;
  grid-template-columns: 1fr;
  gap: 6px;
}

.team-flag {
  width: 28px;
  height: 28px;
  object-fit: contain;
  justify-self: center;
}

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

.form {
  display: grid;
  gap: 18px;
}

.match-block {
  border: 1px solid rgba(15, 118, 110, 0.16);
  border-radius: 10px;
  padding: 14px;
  background: rgba(15, 118, 110, 0.04);
}

.match-title {
  margin: 0 0 12px;
  color: #0f766e;
  font-size: 1.05rem;
}

.score-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

label {
  display: grid;
  gap: 6px;
  color: #334155;
  font-size: 0.88rem;
  font-weight: 800;
}

.flag {
  font-size: 1.05rem;
  line-height: 1;
}


.score-input {
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  color: #102033;
  font: inherit;
  font-weight: 700;
  min-height: 46px;
  padding: 0 12px;
}

.score-input:focus {
  border-color: #0f766e;
  outline: 3px solid rgba(15, 118, 110, 0.16);
}

.error-message {
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 700;
  padding: 12px;
  margin: 0;
  background: #fee2e2;
  border-color: #fecaca;
  color: #991b1b;
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

@media (max-width: 720px) {
  .score-grid {
    grid-template-columns: 1fr;
  }
}
</style>
