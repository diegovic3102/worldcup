<template>
  <aside class="summary">
    <h2>Mis predicciones</h2>

    <div v-if="items.length === 0" class="empty-state">
      Todavia no tienes marcadores guardados.
    </div>

    <ul v-else>
      <li v-for="item in items" :key="item.match.id">
        <span>{{ item.match.homeTeam.shortName }} vs {{ item.match.awayTeam.shortName }}</span>
        <strong>{{ item.prediction.homeScore }} - {{ item.prediction.awayScore }}</strong>
      </li>
    </ul>
  </aside>
</template>

<script lang="ts">
import { defineComponent, PropType } from 'vue';
import type { Match, Prediction } from '../types';

interface SummaryItem {
  match: Match;
  prediction: Prediction;
}

export default defineComponent({
  name: 'PredictionSummary',
  props: {
    matches: {
      type: Array as PropType<Match[]>,
      required: true,
    },
    predictions: {
      type: Object as PropType<Record<string, Prediction>>,
      required: true,
    },
  },
  computed: {
    items(): SummaryItem[] {
      return this.matches
        .filter((match) => Boolean(this.predictions[match.id]))
        .map((match) => ({
          match,
          prediction: this.predictions[match.id],
        }));
    },
  },
});
</script>

<style scoped>
.summary {
  background: #102033;
  border-radius: 8px;
  color: #fff;
  padding: 22px;
  position: sticky;
  top: 20px;
}

h2 {
  font-size: 1.15rem;
  margin: 0 0 18px;
}

.empty-state {
  color: #cbd5e1;
  font-size: 0.95rem;
  line-height: 1.5;
}

ul {
  display: grid;
  gap: 12px;
  list-style: none;
  margin: 0;
  padding: 0;
}

li {
  align-items: center;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  min-height: 46px;
  padding: 10px 12px;
}

li span {
  color: #dbeafe;
  font-size: 0.88rem;
  font-weight: 700;
}

li strong {
  font-size: 1.05rem;
}

@media (max-width: 980px) {
  .summary {
    position: static;
  }
}
</style>
