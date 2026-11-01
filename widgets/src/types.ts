import { ALL_TYPES, h, mountWidget, typeChip } from './shared'

interface Relations {
  double: string[]
  half: string[]
  none: string[]
}

interface TypesData {
  type: string
  attack: Relations
  defense: Relations
}

// Plain ASCII labels: the pixel font may lack "×" and "½".
const MULTIPLIERS = [
  { key: 'double', label: 'x2', name: 'Súper eficaz', className: 'm-double' },
  { key: 'half', label: 'x0.5', name: 'Poco eficaz', className: 'm-half' },
  { key: 'none', label: 'x0', name: 'Sin efecto', className: 'm-none' },
] as const

function multiplierOf(rel: Relations, type: string) {
  return MULTIPLIERS.find((m) => rel[m.key].includes(type)) ?? { label: 'x1', className: 'm-normal' }
}

/** One cell per type, like a row of the games' type chart. */
function chart(title: string, hint: string, rel: Relations): HTMLElement {
  return h('section', {}, [
    h('h2', { class: 'section-title', text: title }),
    h('p', { class: 'hint', text: hint }),
    h(
      'div',
      { class: 'type-grid' },
      ALL_TYPES.map((t) => {
        const m = multiplierOf(rel, t)
        return h('div', { class: `type-cell ${m.className}` }, [typeChip(t), h('span', { class: 'mult', text: m.label })])
      }),
    ),
  ])
}

function render(root: HTMLElement, d: TypesData): void {
  root.replaceChildren(
    h('article', { class: 'card' }, [
      h('header', { class: 'types-head' }, [typeChip(d.type), h('span', { class: 'types-title', text: 'Tabla de tipos' })]),
      chart('Ataque', 'Daño que hace a cada tipo', d.attack),
      chart('Defensa', 'Daño que recibe de cada tipo', d.defense),
      h('div', { class: 'types-legend' }, [
        ...MULTIPLIERS.map((m) => h('span', { class: `legend-mult ${m.className}`, text: `${m.label} ${m.name}` })),
        h('span', { class: 'legend-mult m-normal', text: 'x1 Normal' }),
      ]),
    ]),
  )
}

mountWidget<TypesData>('pokedex-types', render)
