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
                <select v-model="selection.pos1" :disabled="locked">
                    <option value="">Seleccionar</option>
                    <option v-for="e in equipos" :key="e.codigo_fifa" :value="e.codigo_fifa">
                        {{ e.nombre }}
                    </option>
                </select>
            </div>

            <div class="card">
                <label>🥈 Segundo lugar</label>
                <select v-model="selection.pos2" :disabled="locked">
                    <option value="">Seleccionar</option>
                    <option v-for="e in equipos" :key="e.codigo_fifa" :value="e.codigo_fifa">
                        {{ e.nombre }}
                    </option>
                </select>
            </div>

            <div class="card">
                <label>🥉 Tercer lugar</label>
                <select v-model="selection.pos3" :disabled="locked">
                    <option value="">Seleccionar</option>
                    <option v-for="e in equipos" :key="e.codigo_fifa" :value="e.codigo_fifa">
                        {{ e.nombre }}
                    </option>
                </select>
            </div>

            <div class="card">
                <label>🏅 Cuarto lugar</label>
                <select v-model="selection.pos4" :disabled="locked">
                    <option value="">Seleccionar</option>
                    <option v-for="e in equipos" :key="e.codigo_fifa" :value="e.codigo_fifa">
                        {{ e.nombre }}
                    </option>
                </select>
            </div>

        </div>
        <div v-if="saved?.pos1" class="podium-container">

            <h3>🏆 Podio Mundial</h3>

            <div class="podium">

                <div class="podium-item second">
                    <div class="position">2</div>
                    <div class="team">{{ getTeamName(saved.pos2) }}</div>
                </div>

                <div class="podium-item first">
                    <div class="position">1</div>
                    <div class="team">{{ getTeamName(saved.pos1) }}</div>
                </div>

                <div class="podium-item third">
                    <div class="position">3</div>
                    <div class="team">{{ getTeamName(saved.pos3) }}</div>
                </div>

                <div class="podium-item fourth">
                    <div class="position">4</div>
                    <div class="team">{{ getTeamName(saved.pos4) }}</div>
                </div>

            </div>

            <p v-if="locked" class="locked-msg">
                🔒 Predicción bloqueada
            </p>

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
            },
            saved: null as any,
            locked: false,
        }
    },

    mounted() {
        this.fetchEquipos()
        this.fetchSaved()
    },

    methods: {

        validateUniqueSelection(): boolean {
            const values = [
                this.selection.pos1,
                this.selection.pos2,
                this.selection.pos3,
                this.selection.pos4
            ].filter(Boolean)

            const unique = new Set(values)

            if (unique.size !== values.length) {
                this.error = 'No puedes repetir equipos en el Top 4'
                return false
            }

            return true
        },

        getTeamName(code: string) {
            const team = this.equipos.find(e => e.codigo_fifa === code)
            return team ? team.nombre : code
        },

        async fetchSaved() {
            try {
                const res = await fetch(
                    `${API_BASE_URL}/apuestas/top4/mundial/me?usuarioId=${this.currentUser.id}`
                )

                const data = await res.json()

                if (!res.ok) return

                this.saved = data
                this.locked = data.locked

                // precargar selección si ya existe
                if (data.pos1) {
                    this.selection.pos1 = data.pos1
                    this.selection.pos2 = data.pos2
                    this.selection.pos3 = data.pos3
                    this.selection.pos4 = data.pos4
                }
            } catch {
                // silencioso
            }
        },

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

            if (!this.validateUniqueSelection()) {
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

.result-box {
    margin-top: 20px;
    padding: 16px;
    border-radius: 10px;
    background: #f8fafc;
    border: 1px solid #d9e2ec;
}

.result-box h3 {
    margin: 0 0 10px;
}

.locked-msg {
    margin-top: 10px;
    color: #b91c1c;
    font-weight: 800;
}


.podium-container {
  margin-top: 24px;
  padding: 20px;
  background: #0f172a;
  border-radius: 14px;
  color: white;
  text-align: center;
  overflow: hidden;
}

.podium {
  display: flex;
  justify-content: center;
  align-items: flex-end;
  gap: 12px;
  margin-top: 20px;
  height: 180px;
}

.podium-item {
  width: 90px;
  background: #1e293b;
  border-radius: 10px;
  padding: 10px;
  animation: popIn 0.6s ease forwards;
  opacity: 0;
  transform: translateY(30px);
}

.podium-item .position {
  font-size: 1.2rem;
  font-weight: 900;
  margin-bottom: 6px;
}

.podium-item .team {
  font-size: 0.75rem;
  font-weight: 700;
}

.first {
  height: 140px;
  background: gold;
  color: #1a1a1a;
  animation-delay: 0.1s;
}

.second {
  height: 110px;
  background: silver;
  color: #1a1a1a;
  animation-delay: 0.2s;
}

.third {
  height: 90px;
  background: #cd7f32;
  color: #1a1a1a;
  animation-delay: 0.3s;
}

.fourth {
  height: 80px;
  background: #334155;
  animation-delay: 0.4s;
}

@keyframes popIn {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>