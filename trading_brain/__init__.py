"""Trading brain module for MT4 connection and trading logic."""

# Only expose MT4 and Mt4Tick to avoid importing trading_logic
# which has platform-specific dependencies (keyboard, msvcrt)
from .metatrader4 import MT4, Mt4Tick

__all__ = ["MT4", "Mt4Tick"]
