// Los partidos del backend traen el codigo FIFA del equipo (ej. "MEX"),
// pero no el emoji de la bandera. Aqui mapeamos cada codigo FIFA a su
// codigo ISO-3166 alpha-2 y de ahi construimos el emoji con los
// "regional indicator symbols". Si un codigo no esta mapeado, devolvemos
// el propio codigo FIFA como texto para no romper la vista.

const FIFA_TO_ISO2: Record<string, string> = {
  // Grupo A
  KOR: 'KR', MEX: 'MX', CZE: 'CZ', RSA: 'ZA',
  // Grupo B
  BIH: 'BA', CAN: 'CA', QAT: 'QA', SUI: 'CH',
  // Grupo C
  BRA: 'BR', HAI: 'HT', MAR: 'MA',
  // Grupo D
  AUS: 'AU', USA: 'US', PAR: 'PY', TUR: 'TR',
  // Grupo E
  GER: 'DE', CIV: 'CI', CUW: 'CW', ECU: 'EC',
  // Grupo F
  JPN: 'JP', NED: 'NL', SWE: 'SE', TUN: 'TN',
  // Grupo G
  BEL: 'BE', EGY: 'EG', IRN: 'IR', NZL: 'NZ',
  // Grupo H
  KSA: 'SA', CPV: 'CV', ESP: 'ES', URU: 'UY',
  // Otros grupos del torneo (equipos que ya existen en la base)
  FRA: 'FR', IRQ: 'IQ', NOR: 'NO', SEN: 'SN',
  ALG: 'DZ', ARG: 'AR', AUT: 'AT', JOR: 'JO',
  COL: 'CO', POR: 'PT', COD: 'CD', UZB: 'UZ',
  CRO: 'HR', GHA: 'GH', PAN: 'PA',
};

// Banderas que no se pueden formar con dos letras (subdivisiones del Reino
// Unido): usan secuencias de etiquetas Unicode.
const SPECIAL_FLAGS: Record<string, string> = {
  SCO: '\u{1F3F4}\u{E0067}\u{E0062}\u{E0073}\u{E0063}\u{E0074}\u{E007F}', // Escocia
  ENG: '\u{1F3F4}\u{E0067}\u{E0062}\u{E0065}\u{E006E}\u{E0067}\u{E007F}', // Inglaterra
};

function iso2ToEmoji(iso2: string): string {
  return iso2
    .toUpperCase()
    .split('')
    .map((char) => String.fromCodePoint(0x1f1e6 + char.charCodeAt(0) - 65))
    .join('');
}

export function fifaToFlag(codigoFifa: string): string {
  const code = codigoFifa.toUpperCase();

  if (SPECIAL_FLAGS[code]) {
    return SPECIAL_FLAGS[code];
  }

  const iso2 = FIFA_TO_ISO2[code];

  if (!iso2) {
    return code;
  }

  return iso2ToEmoji(iso2);
}