import type { Match } from '../types';

export const matches: Match[] = [
  {
    id: 'ecu-bra-001',
    group: 'Grupo A',
    startsAt: '2026-06-11T19:00:00-05:00',
    status: 'upcoming',
    homeTeam: {
      id: 'ecu',
      name: 'Ecuador',
      shortName: 'ECU',
      flag: '🇪🇨',
    },
    awayTeam: {
      id: 'bra',
      name: 'Brasil',
      shortName: 'BRA',
      flag: '🇧🇷',
    },
  },
  {
    id: 'arg-mex-001',
    group: 'Grupo B',
    startsAt: '2026-06-12T16:00:00-05:00',
    status: 'upcoming',
    homeTeam: {
      id: 'arg',
      name: 'Argentina',
      shortName: 'ARG',
      flag: '🇦🇷',
    },
    awayTeam: {
      id: 'mex',
      name: 'Mexico',
      shortName: 'MEX',
      flag: '🇲🇽',
    },
  },
  {
    id: 'esp-ger-001',
    group: 'Grupo C',
    startsAt: '2026-06-13T14:00:00-05:00',
    status: 'upcoming',
    homeTeam: {
      id: 'esp',
      name: 'Espana',
      shortName: 'ESP',
      flag: '🇪🇸',
    },
    awayTeam: {
      id: 'ger',
      name: 'Alemania',
      shortName: 'GER',
      flag: '🇩🇪',
    },
  },
  {
    id: 'fra-uru-001',
    group: 'Grupo D',
    startsAt: '2026-06-14T20:00:00-05:00',
    status: 'upcoming',
    homeTeam: {
      id: 'fra',
      name: 'Francia',
      shortName: 'FRA',
      flag: '🇫🇷',
    },
    awayTeam: {
      id: 'uru',
      name: 'Uruguay',
      shortName: 'URU',
      flag: '🇺🇾',
    },
  },
];
