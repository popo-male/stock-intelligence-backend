from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, ValidationError, model_validator


class WatchList(BaseModel):
    tickers: list[str] = Field(default_factory=list)  # type: ignore


class AppConfig(BaseModel):
    watchlist: WatchList = Field(default_factory=WatchList)  # type: ignore

    @model_validator(mode="before")
    @classmethod
    def normalize_legacy_watchlist(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        watchlist = data.get("watchlist")
        if isinstance(watchlist, list):
            normalized = dict(data)
            normalized["watchlist"] = {"tickers": watchlist}
            return normalized

        return data


def load_config() -> AppConfig:
    config_path = Path(__file__).resolve().parents[2] / "config.yaml"
    if not config_path.exists():
        return AppConfig()

    with config_path.open("r", encoding="utf-8") as f:
        raw_config = yaml.safe_load(f) or {}

    try:
        return AppConfig.model_validate(raw_config)
    except ValidationError as exc:
        raise ValueError(f"Invalid configuration in {config_path}: {exc}") from exc


config = load_config()
