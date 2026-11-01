import { STAT_KEYS, STAT_LABELS, displayName, h, mountWidget, sprite, typeChip } from './shared'
import type { Stats } from './shared'

interface CardData {
  id: number
  name: string
  sprite: string | null
  artwork: string | null
  types: string[]
  height_m: number
  weight_kg: number
  stats: Stats
  abilities: { name: string; hidden: boolean }[]
  // Only present when the card comes from get_pokedex_entry
  genus?: string | null
  flavor_text?: string | null
  generation?: string
  habitat?: string
  is_legendary?: boolean
  is_mythical?: boolean
}

const SEGMENTS = 12

// PokeAPI only names habitats in English.
const HABITATS: Record<string, string> = {
  cave: 'Cueva',
  forest: 'Bosque',
  grassland: 'Pradera',
  mountain: 'Montaña',
  rare: 'Raro',
  'rough-terrain': 'Terreno agreste',
  sea: 'Mar',
  urban: 'Ciudad',
  'waters-edge': 'Orilla del agua',
}

function statRow(key: string, value: number, color: string): HTMLElement {
  // 12 cells of 15 points: typical stats stay readable; outliers (Blissey's HP 255) fill the bar.
  const filled = Math.min(SEGMENTS, Math.max(value > 0 ? 1 : 0, Math.round(value / 15)))
  const cells = Array.from({ length: SEGMENTS }, (_, i) => h('span', { class: i < filled ? 'on' : '' }))
  return h('div', { class: 'stat-row' }, [
    h('span', { class: 'stat-label', text: STAT_LABELS[key] ?? key }),
    h('div', { class: 'stat-bar', style: `--bar:${color}` }, cells),
    h('span', { class: 'stat-value', text: value }),
  ])
}

function render(root: HTMLElement, d: CardData): void {
  const name = displayName(d.name)
  const color = `var(--type-${d.types[0] ?? 'normal'})`
  const total = Object.values(d.stats).reduce((a, b) => a + b, 0)

  const facts: [string, string][] = [
    ['Altura', `${d.height_m.toFixed(1)} m`],
    ['Peso', `${d.weight_kg.toFixed(1)} kg`],
  ]
  if (d.generation) facts.push(['Generación', d.generation])
  if (d.habitat && d.habitat !== 'unknown') facts.push(['Hábitat', HABITATS[d.habitat] ?? displayName(d.habitat)])
  if (d.is_legendary) facts.push(['Clase', 'Legendario'])
  else if (d.is_mythical) facts.push(['Clase', 'Singular'])

  root.replaceChildren(
    h('article', { class: 'card' }, [
      h('header', { class: 'dex-head' }, [
        h('div', { class: 'sprite-frame' }, [sprite(d.sprite ?? d.artwork, name, '')]),
        h('div', { class: 'dex-title' }, [
          h('h1', { class: 'dex-name' }, [
            document.createTextNode(`${name} `),
            h('span', { class: 'dex-num', text: `#${String(d.id).padStart(3, '0')}` }),
          ]),
          d.genus ? h('p', { class: 'dex-genus', text: d.genus }) : null,
          h('div', { class: 'chips' }, d.types.map(typeChip)),
        ]),
      ]),
      d.flavor_text ? h('p', { class: 'dex-flavor', text: d.flavor_text }) : null,
      h(
        'div',
        { class: 'dex-facts' },
        facts.map(([k, v]) => h('div', { class: 'fact' }, [document.createTextNode(k), h('b', { text: v })])),
      ),
      h('h2', { class: 'section-title', text: 'Estadísticas base' }),
      h('div', {}, STAT_KEYS.map((k) => statRow(k, d.stats[k] ?? 0, color))),
      h('div', { class: 'stat-total' }, [document.createTextNode('TOTAL '), h('b', { text: total })]),
      h('h2', { class: 'section-title', text: 'Habilidades' }),
      h(
        'div',
        { class: 'chips' },
        d.abilities.map((a) =>
          h('span', { class: a.hidden ? 'ability hidden' : 'ability', text: displayName(a.name) + (a.hidden ? ' (oculta)' : '') }),
        ),
      ),
    ]),
  )
}

mountWidget<CardData>('pokedex-card', render)
