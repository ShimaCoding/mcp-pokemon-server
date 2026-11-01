import { STAT_KEYS, STAT_LABELS, displayName, h, mountWidget, sprite } from './shared'
import type { Stats } from './shared'

interface StatsEntry {
  id: number
  name: string
  sprite: string | null
  types: string[]
  stats: Stats
  total: number
}

interface StatsData {
  pokemon: StatsEntry[]
}

// Distinct hues that hold up on light and dark backgrounds.
const SERIES = ['#e5484d', '#3e7bfa', '#30a46c', '#f5a524', '#8e4ec6', '#12a594']

const SVG_NS = 'http://www.w3.org/2000/svg'

function svg(tag: string, attrs: Record<string, string | number>, text?: string): SVGElement {
  const el = document.createElementNS(SVG_NS, tag)
  for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, String(v))
  if (text !== undefined) el.textContent = text
  return el
}

function radar(entries: StatsEntry[], colors: string[]): SVGElement {
  const size = 300
  const c = size / 2
  const r = 110
  // Scale to the largest stat shown (min 150) so small Pokémon don't collapse to a dot.
  const peak = Math.max(150, ...entries.flatMap((e) => STAT_KEYS.map((k) => e.stats[k] ?? 0)))
  const max = Math.ceil(peak / 50) * 50
  const angle = (i: number) => (Math.PI * 2 * i) / STAT_KEYS.length - Math.PI / 2
  const point = (i: number, v: number) => {
    const d = (v / max) * r
    return [c + d * Math.cos(angle(i)), c + d * Math.sin(angle(i))] as const
  }

  const root = svg('svg', { class: 'radar', viewBox: `0 0 ${size} ${size}`, role: 'img' })
  root.append(svg('title', {}, `Estadísticas base: ${entries.map((e) => displayName(e.name)).join(', ')}`))

  for (const f of [0.25, 0.5, 0.75, 1]) {
    const pts = STAT_KEYS.map((_, i) => point(i, max * f).join(',')).join(' ')
    root.append(svg('polygon', { class: 'grid', points: pts }))
  }
  STAT_KEYS.forEach((key, i) => {
    const [x, y] = point(i, max)
    root.append(svg('line', { class: 'axis', x1: c, y1: c, x2: x, y2: y }))
    const [lx, ly] = point(i, max * 1.2)
    const anchor = Math.abs(lx - c) < 4 ? 'middle' : lx > c ? 'start' : 'end'
    root.append(svg('text', { class: 'label', x: lx, y: ly, 'text-anchor': anchor, 'dominant-baseline': 'middle' }, STAT_LABELS[key]))
  })

  entries.forEach((e, idx) => {
    const pts = STAT_KEYS.map((k, i) => point(i, e.stats[k] ?? 0).join(',')).join(' ')
    root.append(svg('polygon', { class: 'series', points: pts, fill: colors[idx], stroke: colors[idx] }))
  })
  return root
}

function legend(entries: StatsEntry[], colors: string[]): HTMLElement {
  return h(
    'div',
    { class: 'legend' },
    entries.map((e, i) =>
      h('span', { class: 'legend-item', style: `--series:${colors[i]}` }, [
        h('span', { class: 'legend-swatch' }),
        sprite(e.sprite, displayName(e.name), 'sprite-sm'),
        document.createTextNode(displayName(e.name)),
        h('span', { class: 'legend-total', text: e.total }),
      ]),
    ),
  )
}

function compareTable(entries: StatsEntry[], colors: string[]): HTMLElement {
  const best = Object.fromEntries(
    [...STAT_KEYS, 'total'].map((k) => [
      k,
      Math.max(...entries.map((e) => (k === 'total' ? e.total : e.stats[k] ?? 0))),
    ]),
  )
  const head = h('tr', {}, [
    h('th', { text: '' }),
    ...entries.map((e, i) => h('th', { text: displayName(e.name), style: `color:${colors[i]}` })),
  ])
  const rows = [...STAT_KEYS, 'total'].map((k) =>
    h('tr', {}, [
      h('td', { text: k === 'total' ? 'Total' : STAT_LABELS[k] }),
      ...entries.map((e, i) => {
        const v = k === 'total' ? e.total : e.stats[k] ?? 0
        const isBest = entries.length > 1 && v === best[k]
        return h('td', { text: v, class: isBest ? 'best' : '', style: `--series:${colors[i]}` })
      }),
    ]),
  )
  return h('table', { class: 'compare' }, [h('thead', {}, [head]), h('tbody', {}, rows)])
}

function render(root: HTMLElement, data: StatsData): void {
  const entries = data.pokemon ?? []
  if (entries.length === 0) {
    root.replaceChildren(h('p', { class: 'error', text: 'Sin datos para mostrar.' }))
    return
  }
  const colors =
    entries.length === 1 ? [`var(--type-${entries[0].types[0] ?? 'normal'})`] : SERIES.slice(0, entries.length)

  const body =
    entries.length === 1
      ? h('div', { class: 'chart-layout single' }, [radar(entries, colors), compareTable(entries, colors)])
      : h('div', { class: 'chart-layout' }, [legend(entries, colors), radar(entries, colors), compareTable(entries, colors)])

  root.replaceChildren(h('article', { class: 'card' }, [body]))
}

mountWidget<StatsData>('pokedex-stats', render)
