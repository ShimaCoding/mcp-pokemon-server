"""PokéAPI client with error handling and retries."""

import asyncio
from typing import Any
from urllib.parse import urljoin

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from ..config.logging import get_logger
from ..config.settings import get_settings
from ..models.pokemon_models import Pokemon, PokemonSearchResult, PokemonSpecies

logger = get_logger(__name__)


class PokemonAPIError(Exception):
    """Base exception for PokéAPI errors."""

    pass


class PokemonNotFoundError(PokemonAPIError):
    """Exception raised when Pokemon is not found."""

    pass


class PokemonAPITimeoutError(PokemonAPIError):
    """Exception raised when API request times out."""

    pass


class PokemonAPIRateLimitError(PokemonAPIError):
    """Exception raised when rate limit is exceeded."""

    pass


class PokemonAPIClient:
    """Async client for PokéAPI with retry logic and error handling."""

    def __init__(self, base_url: str | None = None, timeout: int | None = None):
        """Initialize the PokéAPI client."""
        settings = get_settings()
        self.base_url = base_url or settings.pokeapi_base_url
        self.timeout = timeout or settings.pokeapi_timeout
        self.client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def start(self):
        """Start the HTTP client."""
        if self.client is None:
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
            )
            logger.info("PokéAPI client started", base_url=self.base_url)

    async def close(self):
        """Close the HTTP client."""
        if self.client:
            await self.client.aclose()
            self.client = None
            logger.info("PokéAPI client closed")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
    )
    async def _make_request(self, endpoint: str) -> dict[str, Any]:
        """Make HTTP request with retry logic."""
        if not self.client:
            await self.start()

        url = urljoin(self.base_url, endpoint)
        logger.debug("Making API request", url=url)

        try:
            response = await self.client.get(endpoint)

            if response.status_code == 404:
                raise PokemonNotFoundError(f"Resource not found: {endpoint}")
            elif response.status_code == 429:
                raise PokemonAPIRateLimitError("Rate limit exceeded")
            elif response.status_code >= 400:
                raise PokemonAPIError(
                    f"API error {response.status_code}: {response.text}"
                )

            data = response.json()
            logger.debug("API request successful", url=url, status=response.status_code)
            return data

        except httpx.TimeoutException as e:
            logger.warning("API request timeout", url=url, timeout=self.timeout)
            raise PokemonAPITimeoutError(f"Request timeout for {url}") from e
        except httpx.ConnectError as e:
            logger.error("API connection error", url=url, error=str(e))
            raise PokemonAPIError(f"Connection error for {url}") from e

    async def get_pokemon(self, identifier: str) -> Pokemon:
        """Get Pokemon by name or ID."""
        logger.info("Fetching Pokemon", identifier=identifier)

        try:
            data = await self._make_request(f"pokemon/{identifier.lower()}")
            pokemon = Pokemon(**data)
            logger.info(
                "Pokemon fetched successfully", name=pokemon.name, id=pokemon.id
            )
            return pokemon
        except Exception as e:
            logger.error("Failed to fetch Pokemon", identifier=identifier, error=str(e))
            raise

    async def get_pokemon_species(self, identifier: str) -> PokemonSpecies:
        """Get Pokemon species by name or ID."""
        logger.info("Fetching Pokemon species", identifier=identifier)

        try:
            data = await self._make_request(f"pokemon-species/{identifier.lower()}")
            species = PokemonSpecies(**data)
            logger.info(
                "Pokemon species fetched successfully", name=species.name, id=species.id
            )
            return species
        except Exception as e:
            logger.error(
                "Failed to fetch Pokemon species", identifier=identifier, error=str(e)
            )
            raise

    async def search_pokemon(
        self, limit: int = 20, offset: int = 0
    ) -> PokemonSearchResult:
        """Search Pokemon with pagination."""
        logger.info("Searching Pokemon", limit=limit, offset=offset)

        try:
            data = await self._make_request(f"pokemon?limit={limit}&offset={offset}")
            result = PokemonSearchResult(**data)
            logger.info(
                "Pokemon search successful",
                count=result.count,
                returned=len(result.results),
            )
            return result
        except Exception as e:
            logger.error(
                "Failed to search Pokemon", limit=limit, offset=offset, error=str(e)
            )
            raise

    async def get_type_info(self, type_name: str) -> dict[str, Any]:
        """Get type information including effectiveness."""
        logger.info("Fetching type info", type_name=type_name)

        try:
            data = await self._make_request(f"type/{type_name.lower()}")
            logger.info("Type info fetched successfully", type_name=type_name)
            return data
        except Exception as e:
            logger.error("Failed to fetch type info", type_name=type_name, error=str(e))
            raise

    async def get_type_data(self, type_name: str) -> dict[str, Any]:
        """Alias for get_type_info for consistency with resource manager."""
        return await self.get_type_info(type_name)

    async def get_multiple_pokemon(self, identifiers: list[str]) -> list[Pokemon]:
        """Get multiple Pokemon concurrently."""
        logger.info("Fetching multiple Pokemon", count=len(identifiers))

        tasks = [self.get_pokemon(identifier) for identifier in identifiers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        pokemon_list = []
        errors = []

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                errors.append(f"Failed to fetch {identifiers[i]}: {result}")
            else:
                pokemon_list.append(result)

        if errors:
            logger.warning("Some Pokemon failed to fetch", errors=errors)

        logger.info(
            "Multiple Pokemon fetch completed",
            requested=len(identifiers),
            successful=len(pokemon_list),
            failed=len(errors),
        )

        return pokemon_list


# Global client instance (will be managed by the server)
_client: PokemonAPIClient | None = None


async def get_pokemon_client() -> PokemonAPIClient:
    """Get or create the global Pokemon API client."""
    global _client
    if _client is None:
        _client = PokemonAPIClient()
        await _client.start()
    return _client


async def close_pokemon_client():
    """Close the global Pokemon API client."""
    global _client
    if _client:
        await _client.close()
        _client = None
