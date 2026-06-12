<template>
  <article class="match-card">
    <div class="match-meta">
      <span>{{ match.group }}</span>
      <time :datetime="match.startsAt">{{ formattedDate }}</time>
    </div>

    <div class="teams-grid">
      <div class="team">
        <span class="flag">{{ match.homeTeam.flag }}</span>
        <div>
          <strong>{{ match.homeTeam.name }}</strong>
          <small>{{ match.homeTeam.shortName }}</small>
        </div>
      </div>

      <div class="score-inputs" aria-label="Marcador apostado">
        <input
          v-model.number="localHomeScore"
          aria-label="Goles equipo local"
          min="0"
          type="number"
        />
        <span>-</span>
        <input
          v-model.number="localAwayScore"
          aria-label="Goles equipo visitante"
          min="0"
          type="number"
        />
      </div>

      <div class="team team-away">
        <span class="flag">{{ match.awayTeam.flag }}</span>
        <div>
          <strong>{{ match.awayTeam.name }}</strong>
          <small>{{ match.awayTeam.shortName }}</small>
        </div>
      </div>
    </div>

    <footer class="card-actions">
      <p v-if="hasPrediction">Guardado: {{ predictionLabel }}</p>
      <p v-else>Sin prediccion guardada</p>
      <button :disabled="!canSave" type="button" @click="save">
        Guardar marcador
      </button>
    </footer>
  </article>
</template>

<script lang="ts">
import { defineComponent, PropType } from 'vue';
import type { Match, Prediction } from '../types';

export default defineComponent({
  name: 'MatchCard',
  props: {
    match: {
      type: Object as PropType<Match>,
      required: true,
    },
    prediction: {
      type: Object as PropType<Prediction | undefined>,
      default: undefined,
    },
  },
  emits: ['save'],
  data() {
    return {
      localHomeScore: this.prediction?.homeScore ?? null as number | null,
      localAwayScore: this.prediction?.awayScore ?? null as number | null,
    };
  },
  computed: {
    canSave(): boolean {
      return this.isValidScore(this.localHomeScore) && this.isValidScore(this.localAwayScore);
    },
    formattedDate(): string {
      return new Intl.DateTimeFormat('es-EC', {
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        month: 'short',
      }).format(new Date(this.match.startsAt));
    },
    hasPrediction(): boolean {
      return Boolean(this.prediction);
    },
    predictionLabel(): string {
      if (!this.prediction) {
        return '';
      }

      return `${this.prediction.homeScore} - ${this.prediction.awayScore}`;
    },
  },
  watch: {
    prediction: {
      handler(nextPrediction?: Prediction) {
        this.localHomeScore = nextPrediction?.homeScore ?? null;
        this.localAwayScore = nextPrediction?.awayScore ?? null;
      },
      deep: true,
    },
  },
  methods: {
    isValidScore(value: number | null): boolean {
      return Number.isInteger(value) && value >= 0 && value <= 20;
    },
    save() {
      if (!this.canSave || this.localHomeScore === null || this.localAwayScore === null) {
        return;
      }

      this.$emit('save', {
        matchId: this.match.id,
        homeScore: this.localHomeScore,
        awayScore: this.localAwayScore,
      } as Prediction);
    },
  },
});
</script>

<style scoped>
.match-card {
  background: #fff;
  border: 1px solid #d9e2ec;
  border-radius: 8px;
  box-shadow: 0 18px 45px rgba(15, 23, 42, 0.08);
  display: grid;
  gap: 22px;
  padding: 22px;
}

.match-meta,
.card-actions {
  align-items: center;
  display: flex;
  justify-content: space-between;
}

.match-meta {
  color: #65758b;
  font-size: 0.84rem;
  font-weight: 700;
  text-transform: uppercase;
}

.teams-grid {
  align-items: center;
  display: grid;
  gap: 16px;
  grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
}

.team {
  align-items: center;
  display: flex;
  gap: 12px;
  min-width: 0;
}

.team-away {
  flex-direction: row-reverse;
  text-align: right;
}

.flag {
  align-items: center;
  background: #eff6ff;
  border-radius: 8px;
  display: inline-flex;
  flex-shrink: 0;
  font-size: 1.7rem;
  height: 50px;
  justify-content: center;
  width: 50px;
}

.team strong {
  color: #102033;
  display: block;
  font-size: 1rem;
  overflow-wrap: anywhere;
}

.team small {
  color: #64748b;
  display: block;
  font-size: 0.76rem;
  font-weight: 800;
  margin-top: 4px;
}

.score-inputs {
  align-items: center;
  display: grid;
  gap: 8px;
  grid-template-columns: 64px 12px 64px;
}

.score-inputs input {
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  color: #0f172a;
  font-size: 1.35rem;
  font-weight: 800;
  height: 56px;
  text-align: center;
  width: 64px;
}

.score-inputs span {
  color: #94a3b8;
  font-weight: 800;
  text-align: center;
}

.card-actions {
  border-top: 1px solid #e2e8f0;
  gap: 14px;
  padding-top: 18px;
}

.card-actions p {
  color: #64748b;
  font-size: 0.9rem;
  margin: 0;
}

button {
  background: #0f766e;
  border: 0;
  border-radius: 8px;
  color: #fff;
  cursor: pointer;
  font-weight: 800;
  min-height: 42px;
  padding: 0 16px;
}

button:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}

@media (max-width: 720px) {
  .teams-grid {
    grid-template-columns: 1fr;
  }

  .team-away {
    flex-direction: row;
    text-align: left;
  }

  .score-inputs {
    grid-template-columns: 1fr 12px 1fr;
  }

  .score-inputs input {
    width: 100%;
  }

  .card-actions {
    align-items: stretch;
    flex-direction: column;
  }
}
</style>
