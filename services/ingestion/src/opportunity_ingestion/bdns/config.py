from dataclasses import dataclass
import os


@dataclass(frozen=True, slots=True)
class BdnsConfig:
    """Runtime settings with conservative defaults for manual exploration."""

    base_url: str = "https://www.infosubvenciones.es/bdnstrans/api"
    timeout_seconds: float = 20.0
    pause_seconds: float = 0.2
    max_retries: int = 2
    page_size: int = 5
    user_agent: str = "OpportunityIntel-ingestion-explorer/0.1"

    @classmethod
    def from_env(cls) -> "BdnsConfig":
        defaults = cls()
        return cls(
            base_url=os.getenv("BDNS_API_BASE_URL", defaults.base_url).rstrip("/"),
            timeout_seconds=float(os.getenv("BDNS_TIMEOUT_SECONDS", defaults.timeout_seconds)),
            pause_seconds=float(os.getenv("BDNS_PAUSE_SECONDS", defaults.pause_seconds)),
            max_retries=int(os.getenv("BDNS_MAX_RETRIES", defaults.max_retries)),
            page_size=int(os.getenv("BDNS_PAGE_SIZE", defaults.page_size)),
            user_agent=os.getenv("BDNS_USER_AGENT", defaults.user_agent),
        )

    def __post_init__(self) -> None:
        if not self.base_url:
            raise ValueError("base_url must not be empty")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if self.pause_seconds < 0:
            raise ValueError("pause_seconds must not be negative")
        if self.max_retries < 0:
            raise ValueError("max_retries must not be negative")
        if not 1 <= self.page_size <= 10_000:
            raise ValueError("page_size must be between 1 and 10000")
