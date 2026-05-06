"""
Correction strategies for different drift severities.

Each strategy generates a prompt designed to re-anchor the LLM
to its original task. Strategies are pluggable - users can add custom ones.

Copyright (c) 2026 Stable-Agent Contributors
Licensed under MIT License
"""

from abc import ABC, abstractmethod
from typing import List, Optional


class CorrectionStrategy(ABC):
    """
    Abstract base class for correction strategies.
    
    Each strategy generates a corrective prompt to re-anchor the LLM.
    Different strategies are appropriate for different drift severities.
    """
    
    @abstractmethod
    def generate(self,
                 goal: str,
                 constraints: List[str],
                 drift_score: float,
                 violated_constraints: Optional[List[str]] = None) -> str:
        """
        Generate a correction prompt.
        
        Args:
            goal: The original task/objective
            constraints: All original constraints
            drift_score: Current drift score (0-1)
            violated_constraints: Specific constraints that were violated
        
        Returns:
            Prompt to inject into the conversation
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Strategy name for logging/debugging."""
        pass


class GentleReminderStrategy(CorrectionStrategy):
    """
    Gentle reminder for low drift situations.
    
    Use when drift is minor and just needs a soft nudge.
    Best for: drift_score < 0.30
    """
    
    @property
    def name(self) -> str:
        return "gentle_reminder"
    
    def generate(self, goal: str, constraints: List[str],
                 drift_score: float,
                 violated_constraints: Optional[List[str]] = None) -> str:
        constraints_text = "\n".join(f"- {c}" for c in constraints)
        
        return f"""[REMINDER]
Remember your core objective: {goal}

Key constraints:
{constraints_text}

Stay focused on the above."""


class StructuredAnchorStrategy(CorrectionStrategy):
    """
    Structured anchor for moderate drift.
    
    Explicitly calls out drift and demands recommitment.
    Best for: 0.30 <= drift_score < 0.60
    """
    
    @property
    def name(self) -> str:
        return "structured_anchor"
    
    def generate(self, goal: str, constraints: List[str],
                 drift_score: float,
                 violated_constraints: Optional[List[str]] = None) -> str:
        constraints_text = "\n".join(f"- {c}" for c in constraints)
        
        violations_text = ""
        if violated_constraints:
            violations_text = (
                f"\nViolated constraints:\n"
                + "\n".join(f"- {c}" for c in violated_constraints)
            )
        
        return f"""[IMPORTANT - REFOCUS NEEDED]
You have drifted from your original objective.

ORIGINAL TASK: {goal}

CRITICAL CONSTRAINTS (you must follow these):
{constraints_text}{violations_text}

Recommit to the above constraints in your next response."""


class EmergencyResetStrategy(CorrectionStrategy):
    """
    Emergency reset for severe drift.
    
    Hard reset of agent behavior - use sparingly.
    Best for: drift_score >= 0.60
    """
    
    @property
    def name(self) -> str:
        return "emergency_reset"
    
    def generate(self, goal: str, constraints: List[str],
                 drift_score: float,
                 violated_constraints: Optional[List[str]] = None) -> str:
        constraints_text = "\n".join(f"- {c}" for c in constraints)
        
        violations_text = ""
        if violated_constraints:
            violations_text = (
                f"\nYou have violated these specific constraints:\n"
                + "\n".join(f"- {c}" for c in violated_constraints)
            )
        
        return f"""[CRITICAL - RESET REQUIRED]
Your responses have significantly diverged from your original task.

RESET TO: {goal}

NON-NEGOTIABLE CONSTRAINTS:
{constraints_text}{violations_text}

You must strictly follow all constraints above for the remainder of this 
conversation. Acknowledge this reset and continue."""


class AdaptiveStrategy(CorrectionStrategy):
    """
    Adaptive strategy that picks the right approach based on drift level.
    
    Combines all three strategies and chooses based on severity.
    Recommended default for most use cases.
    """
    
    def __init__(self,
                 gentle_threshold: float = 0.30,
                 structured_threshold: float = 0.60):
        """
        Args:
            gentle_threshold: Below this = gentle reminder
            structured_threshold: Below this = structured, above = emergency
        """
        self.gentle_threshold = gentle_threshold
        self.structured_threshold = structured_threshold
        
        self._gentle = GentleReminderStrategy()
        self._structured = StructuredAnchorStrategy()
        self._emergency = EmergencyResetStrategy()
    
    @property
    def name(self) -> str:
        return "adaptive"
    
    def generate(self, goal: str, constraints: List[str],
                 drift_score: float,
                 violated_constraints: Optional[List[str]] = None) -> str:
        if drift_score < self.gentle_threshold:
            return self._gentle.generate(
                goal, constraints, drift_score, violated_constraints
            )
        elif drift_score < self.structured_threshold:
            return self._structured.generate(
                goal, constraints, drift_score, violated_constraints
            )
        else:
            return self._emergency.generate(
                goal, constraints, drift_score, violated_constraints
            )
    
    def get_strategy_name(self, drift_score: float) -> str:
        """Get which underlying strategy will be used for this score."""
        if drift_score < self.gentle_threshold:
            return self._gentle.name
        elif drift_score < self.structured_threshold:
            return self._structured.name
        else:
            return self._emergency.name
