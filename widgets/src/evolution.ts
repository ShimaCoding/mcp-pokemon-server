import { TYPE_LABELS, displayName, h, mountWidget, sprite, typeChip } from './shared'

interface Via {
  trigger: string
  is_default?: boolean
  [key: string]: unknown
}

interface EvoNode {
  name: string
  id: number | null
  types: string[]
  total_bst: number | null
  sprite: string | null
  is_baby: boolean
  queried: boolean
  via: Via[]
  evolves_to: EvoNode[]
}

interface EvolutionData {
  queried: string
  stages: number
  root: EvoNode
}

const TRIGGERS: Record<string, string> = {
  trade: 'Intercambio',
  shed: 'Muda',
  spin: 'Giro',
  'tower-of-darkness': 'Torre Oscuridad',
  'tower-of-waters': 'Torre Agua',
  'three-critical-hits': '3 golpes críticos',
  'take-damage': 'Recibir daño',
  'agile-style-move': 'Estilo rápido',
  'strong-style-move': 'Estilo fuerte',
  'recoil-damage': 'Daño de retroceso',
  'use-move': 'Usar movimiento',
  'three-successful-hits': '3 golpes seguidos',
  'gimmighoul-coins': 'Monedas',
  'other': 'Especial',
}

const STONES: Record<string, string> = {
  water: 'Agua', fire: 'Fuego', thunder: 'Trueno', leaf: 'Hoja', moon: 'Lunar', sun: 'Solar',
  shiny: 'Día', dusk: 'Noche', dawn: 'Alba', ice: 'Hielo',
}

const TIMES: Record<string, string> = { day: 'de día', night: 'de noche', dusk: 'al atardecer' }
const GENDERS: Record<string, string> = { female: 'hembra', male: 'macho' }

function itemLabel(item: string): string {
  const stone = /^(.+)-stone$/.exec(item)
  if (stone) return `Piedra ${STONES[stone[1]] ?? displayName(stone[1])}`
  return displayName(item)
}

function str(v: unknown): string {
  return String(v)
}

/** One way of evolving, as a short Spanish phrase ("Nv. 25 · de noche"). */
export function viaLabel(v: Via): string {
  const parts: string[] = []
  if (v.min_level) parts.push(`Nv. ${str(v.min_level)}`)
  else if (v.item) parts.push(itemLabel(str(v.item)))
  else if (v.trigger !== 'level-up') parts.push(TRIGGERS[v.trigger] ?? displayName(v.trigger))

  if (v.item && v.min_level) parts.push(itemLabel(str(v.item)))
  if (v.trigger === 'trade' && v.trade_species) parts.push(`por ${displayName(str(v.trade_species))}`)
  if (v.min_happiness) parts.push('Amistad')
  if (v.min_affection) parts.push('Afecto')
  if (v.min_beauty) parts.push('Belleza')
  if (v.time_of_day) parts.push(TIMES[str(v.time_of_day)] ?? str(v.time_of_day))
  if (v.held_item) parts.push(`con ${itemLabel(str(v.held_item))}`)
  if (v.known_move) parts.push(`sabiendo ${displayName(str(v.known_move))}`)
  if (v.known_move_type) parts.push(`mov. ${TYPE_LABELS[str(v.known_move_type)] ?? displayName(str(v.known_move_type))}`)
  if (v.used_move) parts.push(`usando ${displayName(str(v.used_move))}`)
  if (v.location) parts.push(`en ${displayName(str(v.location))}`)
  if (v.near_special_rock) parts.push('cerca de roca especial')
  if (v.region) parts.push(`en ${displayName(str(v.region))}`)
  if (v.gender) parts.push(GENDERS[str(v.gender)] ?? str(v.gender))
  if (v.party_species) parts.push(`con ${displayName(str(v.party_species))} en el equipo`)
  if (v.party_type) parts.push(`con tipo ${TYPE_LABELS[str(v.party_type)] ?? displayName(str(v.party_type))} en el equipo`)
  if (v.needs_overworld_rain) parts.push('con lluvia')
  if (v.turn_upside_down) parts.push('consola boca abajo')
  if (v.relative_physical_stats !== undefined) {
    const r = Number(v.relative_physical_stats)
    parts.push(r > 0 ? 'ATK > DEF' : r < 0 ? 'ATK < DEF' : 'ATK = DEF')
  }
  if (v.min_move_count) parts.push(`${str(v.min_move_count)} usos`)
  if (v.min_steps) parts.push(`${str(v.min_steps)} pasos`)
  if (v.min_damage_taken) parts.push(`${str(v.min_damage_taken)} de daño`)
  if (v.chance_percent !== undefined) parts.push(`${str(v.chance_percent)}%`)
  // A plain level-up with no other condition (e.g. an unknown trigger detail).
  if (!parts.length) parts.push('Subir de nivel')
  return parts.join(' · ')
}

/**
 * PokéAPI lists one entry per game generation. Show the current-game ones
 * (`is_default`) and fall back to everything; identical labels collapse.
 */
export function viaLabels(via: Via[]): { shown: string[]; hidden: number } {
  const current = via.filter((v) => v.is_default)
  const pool = current.length ? current : via
  const shown = [...new Set(pool.map(viaLabel))]
  const all = new Set(via.map(viaLabel))
  return { shown, hidden: Math.max(0, all.size - shown.length) }
}

/** Clicking a stage asks Dexter for its card: the host routes it to the chat. */
function askFor(name: string, button: HTMLButtonElement): void {
  button.classList.add('picked')
  void app.sendMessage({
    role: 'user',
    content: [{ type: 'text', text: `Muéstrame la entrada de la Pokédex de ${displayName(name)}` }],
  })
}

function stage(n: EvoNode): HTMLElement {
  const name = displayName(n.name)
  const button = h(
    'button',
    {
      class: `evo-stage${n.queried ? ' queried' : ''}`,
      attrs: { type: 'button', title: `Ver la ficha de ${name}`, ...(n.queried ? { 'aria-current': 'true' } : {}) },
    },
    [
      sprite(n.sprite, name, 'sprite-sm'),
      h('span', { class: 'evo-info' }, [
        h('span', { class: 'tile-name', text: name }),
        n.id ? h('span', { class: 'dex-num', text: `#${String(n.id).padStart(3, '0')}` }) : null,
        n.types.length ? h('span', { class: 'chips' }, n.types.map(typeChip)) : null,
        n.total_bst !== null ? h('span', { class: 'dex-num', text: `BST ${n.total_bst}` }) : null,
        n.is_baby ? h('span', { class: 'role', text: 'BEBÉ' }) : null,
      ]),
    ],
  )
  button.addEventListener('click', () => askFor(n.name, button))
  return button
}

function edge(via: Via[]): HTMLElement {
  const { shown, hidden } = viaLabels(via)
  const lines = shown.map((t) => h('span', { class: 'evo-cond', text: t }))
  if (hidden) {
    lines.push(h('span', { class: 'evo-more', text: `+${hidden} en otros juegos`, attrs: { title: 'Otras condiciones según el juego' } }))
  }
  return h('div', { class: 'evo-edge' }, [h('span', { class: 'evo-conds' }, lines), h('span', { class: 'evo-arrow', text: '▶', attrs: { 'aria-hidden': 'true' } })])
}

function subtree(n: EvoNode): HTMLElement {
  const children = n.evolves_to.map((c) =>
    h('li', { class: 'evo-child' }, [edge(c.via), subtree(c)]),
  )
  return h('div', { class: 'evo-node' }, [
    stage(n),
    children.length ? h('ul', { class: 'evo-children' }, children) : null,
  ])
}

function render(root: HTMLElement, d: EvolutionData): void {
  const alone = d.root.evolves_to.length === 0
  root.replaceChildren(
    h('article', { class: 'card' }, [
      h('header', { class: 'search-head' }, [
        h('span', { class: 'types-title', text: 'Línea evolutiva' }),
        h('span', { class: 'dex-num', text: alone ? 'Sin evolución' : `${d.stages} etapas` }),
      ]),
      h('div', { class: 'evo-tree' }, [subtree(d.root)]),
      h('p', { class: 'hint', text: 'Toca una etapa para ver su ficha' }),
    ]),
  )
}

const app = mountWidget<EvolutionData>('pokedex-evolution', render)
