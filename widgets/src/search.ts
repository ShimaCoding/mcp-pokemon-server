import { displayName, h, mountWidget, renderError, sprite } from './shared'

interface SearchData {
  count: number
  limit: number
  offset: number
  results: { id: number; name: string; sprite: string | null }[]
}

/** Clicking a Pokémon asks Dexter for its card: the host routes it to the chat. */
function askFor(name: string, tile: HTMLButtonElement): void {
  tile.classList.add('picked')
  void app.sendMessage({
    role: 'user',
    content: [{ type: 'text', text: `Muéstrame la entrada de la Pokédex de ${displayName(name)}` }],
  })
}

/** Pages are fetched straight from the server tool; the chat isn't involved. */
async function goTo(root: HTMLElement, d: SearchData, offset: number): Promise<void> {
  root.querySelectorAll<HTMLButtonElement>('.pager button').forEach((b) => (b.disabled = true))
  try {
    const result = await app.callServerTool({ name: 'search_pokemon', arguments: { limit: d.limit, offset } })
    if (result.isError || !result.structuredContent) throw new Error('Sin datos para mostrar.')
    render(root, result.structuredContent as unknown as SearchData)
  } catch (err) {
    renderError(root, err instanceof Error ? err.message : 'No se pudo cargar la página.')
  }
}

function render(root: HTMLElement, d: SearchData): void {
  const first = d.offset + 1
  const last = d.offset + d.results.length

  const tiles = d.results.map((p) => {
    const name = displayName(p.name)
    const tile = h('button', { class: 'dex-tile', attrs: { type: 'button', title: `Ver la ficha de ${name}` } }, [
      sprite(p.sprite, name, 'sprite-sm'),
      h('span', { class: 'dex-num', text: `#${String(p.id).padStart(3, '0')}` }),
      h('span', { class: 'tile-name', text: name }),
    ])
    tile.addEventListener('click', () => askFor(p.name, tile))
    return tile
  })

  const prev = h('button', { class: 'pager-btn', text: '◀ Anteriores', attrs: { type: 'button' } })
  const next = h('button', { class: 'pager-btn', text: 'Siguientes ▶', attrs: { type: 'button' } })
  prev.disabled = d.offset <= 0
  next.disabled = last >= d.count
  prev.addEventListener('click', () => void goTo(root, d, Math.max(0, d.offset - d.limit)))
  next.addEventListener('click', () => void goTo(root, d, d.offset + d.limit))

  root.replaceChildren(
    h('article', { class: 'card' }, [
      h('header', { class: 'search-head' }, [
        h('span', { class: 'types-title', text: 'Pokédex' }),
        h('span', { class: 'dex-num', text: d.results.length ? `#${first}-${last} de ${d.count}` : 'Sin resultados' }),
      ]),
      h('div', { class: 'dex-grid' }, tiles),
      h('div', { class: 'pager' }, [prev, h('span', { class: 'hint', text: 'Toca un Pokémon para ver su ficha' }), next]),
    ]),
  )
}

const app = mountWidget<SearchData>('pokedex-search', render)
