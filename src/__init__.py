"""
Drift Corrector: Automatic correction prompts for LLM drift.

Copyright (c) 2026 Stable-Agent Contributors
Licensed under MIT License - See LICENSE file for details

Part of the Stable-Agent ecosystem: https://github.com/Stable-Agent
"""

__version__ = "0.1.0"
__author__ = "Stable-Agent Contributors"
__license__ = "MIT"

from .corrector import DriftCorrector
from .strategies import (
    CorrectionStrategy,
    GentleReminderStrategy,
    StructuredAnchorStrategy,
    EmergencyResetStrategy,
    AdaptiveStrategy,
)

__all__ = [
    "DriftCorrector",
    "CorrectionStrategy",
    "GentleReminderStrategy",
    "StructuredAnchorStrategy",
    "EmergencyResetStrategy",
    "AdaptiveStrategy",
]
