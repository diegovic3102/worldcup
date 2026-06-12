export type MatchStatus = 'upcoming' | 'live' | 'finished';

export interface Team {
  id: string;
  name: string;
  shortName: string;
  flag: string;
}

export interface Match {
  id: string;
  homeTeam: Team;
  awayTeam: Team;
  startsAt: string;
  group: string;
  status: MatchStatus;
}

export interface Prediction {
  matchId: string;
  homeScore: number;
  awayScore: number;
}

export interface AppUser {
  id: number;
  usuario: string;
  nombres: string;
  apellidos: string | null;
  es_administrador: boolean;
}

export interface ApiEquipo {
  id: number;
  codigo_fifa: string;
  nombre: string;
  grupo: string | null;
}

export interface ApiPartido {
  id: number;
  fase: string;
  grupo: string | null;
  fecha_hora: string;
  goles_local: number | null;
  goles_visitante: number | null;
  cerrado: boolean;
  equipo_local: ApiEquipo;
  equipo_visitante: ApiEquipo;
}
