"""Python-compatible Julia router powered by compiled Bend trees."""
from .native import BendReducer
from .router import Router, RouteResult

__all__ = ['BendReducer', 'Router', 'RouteResult', 'FastEngine']


def __getattr__(name):
    if name == 'FastEngine':
        from .engine import FastEngine
        return FastEngine
    raise AttributeError(name)
