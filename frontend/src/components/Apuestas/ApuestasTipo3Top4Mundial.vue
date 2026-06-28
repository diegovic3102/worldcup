<template>
  <div class="top4-module">

    <div class="section-heading">
      <div>
        <p>APUESTA</p>
        <h2>Top 4 Mundial</h2>
      </div>

      <button class="btn-save" @click="save" :disabled="loading">
        {{ loading ? 'Guardando...' : 'Guardar predicción' }}
      </button>
    </div>

    <p v-if="error" class="state-msg state-error">
      {{ error }}
    </p>

    <div v-if="loadingTeams" class="state-msg">
      Cargando equipos...
    </div>

    <div v-else class="grid">

      <div class="card">
        <label>🏆 Campeón</label>
        <select v-model="selection.pos1">
          <option value="">Seleccionar</option>
          <option v-for="e in equipos" :key="e.codigo_fifa" :value="e.codigo_fifa">
            {{ e.nombre }}
          </option>
        </select>
      </div>

      <div class="card">
        <label>🥈 Segundo lugar</label>
        <select v-model="selection.pos2">
          <option value="">Seleccionar</option>
          <option v-for="e in equipos" :key="e.codigo_fifa" :value="e.codigo_fifa">
            {{ e.nombre }}
          </option>
        </select>
      </div>

      <div class="card">
        <label>🥉 Tercer lugar</label>
        <select v-model="selection.pos3">
          <option value="">Seleccionar</option>
          <option v-for="e in equipos" :key="e.codigo_fifa" :value="e.codigo_fifa">
            {{ e.nombre }}
          </option>
        </select>
      </div>

      <div class="card">
        <label>🏅 Cuarto lugar</label>
        <select v-model="selection.pos4">
          <option value="">Seleccionar</option>
          <option v-for="e in equipos" :key="e.codigo_fifa" :value="e.codigo_fifa">
            {{ e.nombre }}
          </option>
        </select>
      </div>

    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import type { AppUser } from '../../types'

const API_BASE_URL = '/worldcup/api'

interface Equipo {
  codigo_fifa: string
  nombre: string
  grupo: string
}

export default defineComponent({
  name: 'ApuestasTipo3Top4Mundial',

  props: {
    currentUser: {
      type: Object as () => AppUser,
      required: true
    }
  },

  data() {
    return {
      equipos: [] as Equipo[],
      loadingTeams: false,
      loading: false,
      error: '',

      selection: {
        pos1: '',
        pos2: '',
        pos3: '',
        pos4: ''
      }
    }
  },

  mounted() {
    this.fetchEquipos()
  },

  methods: {

    async fetchEquipos() {
      this.loadingTeams = true
      this.error = ''

      try {
        const res = await fetch(`${API_BASE_URL}/apuestas/top4/equipos`)
        const data = await res.json()

        if (!res.ok) {
          this.error = data.message || 'Error cargando equipos'
          return
        }

        this.equipos = data
      } catch {
        this.error = 'No se pudo conectar con el servidor'
      } finally {
        this.loadingTeams = false
      }
    },

    async save() {
      this.error = ''

      if (!this.selection.pos1 || !this.selection.pos2 || !this.selection.pos3 || !this.selection.pos4) {
        this.error = 'Debes seleccionar los 4 lugares'
        return
      }

      this.loading = true

      try {
        const res = await fetch(`${API_BASE_URL}/apuestas/top4/mundial/me`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            usuario_id: this.currentUser.id,
            pos1: this.selection.pos1,
            pos2: this.selection.pos2,
            pos3: this.selection.pos3,
            pos4: this.selection.pos4
          })
        })

        const data = await res.json()

        if (!res.ok) {
          this.error = data.message || 'Error guardando predicción'
          return
        }

        alert('Predicción guardada correctamente')
      } catch {
        this.error = 'Error de conexión con el servidor'
      } finally {
        this.loading = false
      }
    }
  }
})
</script>

<style scoped>
.top4-module {
  background: #fff;
  border: 1px solid #d9e2ec;
  border-radius: 12px;
  padding: 20px;
  margin-top: 20px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-top: 16px;
}

.card {
  display: grid;
  gap: 6px;
}

label {
  font-weight: 800;
  font-size: 0.85rem;
  color: #334155;
}

select {
  min-height: 44px;
  border-radius: 8px;
  border: 1px solid #cbd5e1;
  padding: 0 10px;
  font-weight: 600;
}

select:focus {
  outline: 3px solid rgba(15, 118, 110, 0.15);
  border-color: #0f766e;
}

.btn-save {
  background: #0f766e;
  color: white;
  border: none;
  padding: 10px 14px;
  border-radius: 8px;
  font-weight: 800;
  cursor: pointer;
}

.btn-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.state-msg {
  margin-top: 10px;
  padding: 12px;
  border-radius: 8px;
  font-weight: 700;
}

.state-error {
  background: #fee2e2;
  color: #991b1b;
}
</style>