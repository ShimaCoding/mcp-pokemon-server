"""MCP Apps widgets (`ui://` resources) rendered by hosts in sandboxed iframes.

The HTML is built from `widgets/` (Vite + vite-plugin-singlefile) into
`src/widgets/html/`, with the ext-apps runtime inlined: the iframe CSP blocks
external scripts, so each widget must be a single self-contained document.
Rebuild with `make widgets` after editing the widget sources.
"""

from pathlib import Path

from mcp.server.apps import Apps, ResourceCsp

CARD_URI = "ui://pokedex/card.html"
STATS_URI = "ui://pokedex/stats.html"
TYPES_URI = "ui://pokedex/types.html"
TEAM_URI = "ui://pokedex/team.html"
SEARCH_URI = "ui://pokedex/search.html"

_HTML_DIR = Path(__file__).parent / "html"

# Sprites and official artwork are served from the PokeAPI sprites repo.
_CSP = ResourceCsp(resource_domains=["https://raw.githubusercontent.com"])


def _read(name: str) -> str:
    path = _HTML_DIR / name
    if not path.exists():
        raise FileNotFoundError(
            f"Widget {path} is missing; run `make widgets` to build it"
        )
    return path.read_text(encoding="utf-8")


def register_widgets(apps: Apps) -> None:
    """Register the widget HTML resources on the Apps extension."""
    apps.add_html_resource(
        CARD_URI,
        _read("card.html"),
        name="pokedex-card",
        title="Ficha Pokédex",
        description="Sprite, tipos, entrada de la Pokédex y estadísticas base.",
        csp=_CSP,
    )
    apps.add_html_resource(
        STATS_URI,
        _read("stats.html"),
        name="pokedex-stats",
        title="Gráfico de estadísticas",
        description="Radar de estadísticas base de uno o varios Pokémon superpuestos.",
        csp=_CSP,
    )
    apps.add_html_resource(
        TYPES_URI,
        _read("types.html"),
        name="pokedex-types",
        title="Tabla de tipos",
        description="Multiplicadores de daño de un tipo, en ataque y en defensa.",
        csp=_CSP,
    )
    apps.add_html_resource(
        TEAM_URI,
        _read("team.html"),
        name="pokedex-team",
        title="Análisis de equipo",
        description="Equipo de 2 a 6 Pokémon con roles, destacados y cobertura de tipos.",
        csp=_CSP,
    )
    apps.add_html_resource(
        SEARCH_URI,
        _read("search.html"),
        name="pokedex-search",
        title="Buscador Pokédex",
        description="Lista paginada de Pokémon; al hacer clic en uno se pide su ficha.",
        csp=_CSP,
    )
