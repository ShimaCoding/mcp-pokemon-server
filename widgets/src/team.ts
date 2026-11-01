import { displayName, h, mountWidget, sprite, typeChip } from './shared'
import type { Stats } from './shared'

interface Member {
  id: number
  name: string
  sprite: string | null
  types: string[]
  stats: Stats
  total: number
  roles: string[]
}

interface TeamData {
  members: Member[]
  team_analysis: {
    avg_bst: number
    type_coverage: string[]
    fastest: { name: string; speed: number }
    strongest_physical: { name: string; attack: number }
    strongest_special: { name: string; special_attack: number }
    bulkiest: { name: string; bulk_score: number }
  }
  not_found?: string[]
}

const ROLE_LABELS: Record<string, string> = {
  Fast: 'Rápido',
  Attacker: 'Atacante',
  Tank: 'Tanque',
  Bulky: 'Resistente',
  Balanced: 'Equilibrado',
}

const PARTY_SIZE = 6

function slot(m: Member): HTMLElement {
  const name = displayName(m.name)
  return h('div', { class: 'party-slot' }, [
    h('div', { class: 'party-sprite' }, [sprite(m.sprite, name, 'sprite-sm')]),
    h('div', { class: 'party-info' }, [
      h('div', { class: 'party-name' }, [
        document.createTextNode(`${name} `),
        h('span', { class: 'dex-num', text: `#${String(m.id).padStart(3, '0')}` }),
      ]),
      h('div', { class: 'chips' }, m.types.map(typeChip)),
      h('div', { class: 'party-roles' }, m.roles.map((r) => h('span', { class: 'role', text: ROLE_LABELS[r] ?? r }))),
    ]),
    h('div', { class: 'party-bst' }, [document.createTextNode('BST'), h('b', { text: m.total })]),
  ])
}

function emptySlot(): HTMLElement {
  return h('div', { class: 'party-slot empty', text: '- vacío -' })
}

function render(root: HTMLElement, d: TeamData): void {
  const a = d.team_analysis
  const highlights: [string, string][] = [
    ['Más rápido', `${displayName(a.fastest.name)} · ${a.fastest.speed}`],
    ['Ataque físico', `${displayName(a.strongest_physical.name)} · ${a.strongest_physical.attack}`],
    ['Ataque especial', `${displayName(a.strongest_special.name)} · ${a.strongest_special.special_attack}`],
    ['Más resistente', `${displayName(a.bulkiest.name)} · ${a.bulkiest.bulk_score}`],
  ]
  const empty = Math.max(0, PARTY_SIZE - d.members.length)

  root.replaceChildren(
    h('article', { class: 'card' }, [
      h('div', { class: 'party' }, [...d.members.map(slot), ...Array.from({ length: empty }, emptySlot)]),
      h('h2', { class: 'section-title', text: 'Destacados' }),
      h(
        'div',
        { class: 'dex-facts' },
        [
          ...highlights.map(([k, v]) => h('div', { class: 'fact' }, [document.createTextNode(k), h('b', { text: v })])),
          h('div', { class: 'fact' }, [document.createTextNode('BST promedio'), h('b', { text: a.avg_bst })]),
        ],
      ),
      h('h2', { class: 'section-title', text: `Cobertura de tipos (${a.type_coverage.length})` }),
      h('div', { class: 'chips' }, a.type_coverage.map(typeChip)),
      d.not_found?.length
        ? h('p', { class: 'error', text: `No encontrados: ${d.not_found.map(displayName).join(', ')}` })
        : null,
    ]),
  )
}

mountWidget<TeamData>('pokedex-team', render)
