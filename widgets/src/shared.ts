import {
  App,
  applyDocumentTheme,
  applyHostFonts,
  applyHostStyleVariables,
} from '@modelcontextprotocol/ext-apps'
import type { McpUiHostContext } from '@modelcontextprotocol/ext-apps'
import './style.css'

export const STAT_KEYS = [
  'hp',
  'attack',
  'defense',
  'special-attack',
  'special-defense',
  'speed',
] as const

export const STAT_LABELS: Record<string, string> = {
  hp: 'PS',
  attack: 'ATK',
  defense: 'DEF',
  'special-attack': 'SATK',
  'special-defense': 'SDEF',
  speed: 'SPD',
}

const TYPE_LABELS: Record<string, string> = {
  normal: 'Normal', fire: 'Fuego', water: 'Agua', electric: 'Eléctrico',
  grass: 'Planta', ice: 'Hielo', fighting: 'Lucha', poison: 'Veneno',
  ground: 'Tierra', flying: 'Volador', psychic: 'Psíquico', bug: 'Bicho',
  rock: 'Roca', ghost: 'Fantasma', dragon: 'Dragón', dark: 'Siniestro',
  steel: 'Acero', fairy: 'Hada',
}

export type Stats = Record<string, number>

/** Minimal `h()` helper: text goes through textContent, never innerHTML. */
export function h<K extends keyof HTMLElementTagNameMap>(
  tag: K,
  props: { class?: string; text?: string | number; style?: string; attrs?: Record<string, string> } = {},
  children: (Node | null | undefined | false)[] = [],
): HTMLElementTagNameMap[K] {
  const el = document.createElement(tag)
  if (props.class) el.className = props.class
  if (props.text !== undefined) el.textContent = String(props.text)
  if (props.style) el.setAttribute('style', props.style)
  for (const [k, v] of Object.entries(props.attrs ?? {})) el.setAttribute(k, v)
  for (const child of children) if (child) el.append(child)
  return el
}

export function displayName(name: string): string {
  return name
    .split('-')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ')
}

export function typeChip(type: string): HTMLElement {
  return h('span', {
    class: 'type-chip',
    text: TYPE_LABELS[type] ?? displayName(type),
    style: `--type: var(--type-${type}, var(--gbc-mid))`,
  })
}

export function sprite(url: string | null | undefined, alt: string, className = 'sprite'): HTMLElement | null {
  if (!url) return null
  return h('img', { class: className, attrs: { src: url, alt, loading: 'lazy' } })
}

export function renderError(root: HTMLElement, message: string): void {
  root.replaceChildren(h('p', { class: 'error', text: message }))
}

function applyContext(ctx: McpUiHostContext | undefined): void {
  if (!ctx) return
  if (ctx.theme) applyDocumentTheme(ctx.theme)
  if (ctx.styles?.variables) applyHostStyleVariables(ctx.styles.variables)
  if (ctx.styles?.css?.fonts) applyHostFonts(ctx.styles.css.fonts)
}

/**
 * Connect to the host and call `render` with each tool result's
 * `structuredContent`. Handlers are registered before `connect()` so the
 * one-shot tool-result notification can't be missed.
 */
export function mountWidget<T>(name: string, render: (root: HTMLElement, data: T) => void): App {
  const root = document.getElementById('root')!
  root.replaceChildren(h('p', { class: 'loading', text: 'CARGANDO...' }))

  const app = new App({ name, version: '1.0.0' }, {})
  app.ontoolresult = (result) => {
    if (result.isError || !result.structuredContent) {
      const text = result.content?.find((c) => c.type === 'text')
      renderError(root, text && 'text' in text ? text.text : 'Sin datos para mostrar.')
      return
    }
    render(root, result.structuredContent as T)
  }
  app.onhostcontextchanged = (ctx) => applyContext(ctx)
  app.connect().then(() => applyContext(app.getHostContext()))
  return app
}
