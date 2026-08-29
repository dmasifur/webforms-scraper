from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_BASE_URL = "http://localhost:51286"


@dataclass(frozen=True)
class ScraperConfig:
    base_url: str
    username: str
    password: str
    output_path: str
    delay_seconds: float
    verify_ssl: bool

    @classmethod
    def from_env(cls) -> ScraperConfig:
        return cls(
            base_url=os.environ.get("WEBFORMS_BASE_URL", DEFAULT_BASE_URL),
            username=os.environ.get("WEBFORMS_USERNAME", "demo"),
            password=os.environ.get("WEBFORMS_PASSWORD", "demo123"),
            output_path=os.environ.get("WEBFORMS_OUTPUT_PATH", "output/students.xlsx"),
            delay_seconds=float(os.environ.get("WEBFORMS_DELAY_SECONDS", "1.0")),
            verify_ssl=os.environ.get("WEBFORMS_VERIFY_SSL", "false").lower() == "true",
        )
