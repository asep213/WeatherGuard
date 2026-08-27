"""Vercel ASGI entrypoint for the WeatherGuard API."""

from src.backend.main import app

__all__ = ["app"]