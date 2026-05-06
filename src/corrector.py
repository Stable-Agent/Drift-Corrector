"""
Main DriftCorrector class.

Generates corrective prompts to re-anchor LLM agents that have drifted
from their original tasks.

Copyright (c) 2026 Stable-Agent Contributors
Licensed under MIT License
"""

from typing import List, Optional, Dict
from dataclasses import dataclass, field

from .strategies import CorrectionStrategy, AdaptiveStrategy


@dataclass
class CorrectionRecord:
    """Record of a correction that was generated."""
    turn: int
    drift_score: float
    strategy_used: str
    prompt: str
    violated_constraints: List[str] = field(default_factory=list)


class DriftCorrector:
    """
    Generate corrective prompts when drift is detected.
    
    Works with drift-detector or any drift detection system that provides:
    - Drift score (0-1)
    - Original goal
    - Original constraints
    - Optionally: which constraints were violated
    
    Example:
        >>> from drift_detector import DriftDetector
        >>> from drift_corrector import DriftCorrector
        >>> 
        >>> detector = DriftDetector()
        >>> detector.setup(goal="...", constraints=[...])
        >>> 
        >>> corrector = DriftCorrector()
        >>> 
        >>> result = detector.check_response(response, turn=5)
        >>> if result.is_drift:
        ...     correction = corrector.generate_correction(
        ...         goal=detector.original_goal,
        ...         constraints=detector.original_constraints,
        ...         drift_score=result.total_drift,
        ...         violated_constraint_indices=result.violated_constraints,
        ...     )
        ...     # Inject correction into next prompt
    """
    
    def __init__(self, strategy: Optional[CorrectionStrategy] = None):
        """
        Initialize corrector.
        
        Args:
            strategy: Correction strategy to use (default: AdaptiveStrategy)
        """
        self.strategy = strategy or AdaptiveStrategy()
        self.correction_history: List[CorrectionRecord] = []
    
    def generate_correction(self,
                            goal: str,
                            constraints: List[str],
                            drift_score: float,
                            turn: int,
                            violated_constraint_indices: Optional[List[int]] = None
                            ) -> str:
        """
        Generate a correction prompt for the current drift level.
        
        Args:
            goal: The original task/objective
            constraints: All original constraints
            drift_score: Current drift score (0-1)
            turn: Current conversation turn
            violated_constraint_indices: Indices into constraints list
        
        Returns:
            Correction prompt to inject into the conversation
        """
        # Resolve violated constraints from indices
        violated_constraints = []
        if violated_constraint_indices:
            violated_constraints = [
                constraints[i] for i in violated_constraint_indices
                if i < len(constraints)
            ]
        
        # Generate using strategy
        prompt = self.strategy.generate(
            goal=goal,
            constraints=constraints,
            drift_score=drift_score,
            violated_constraints=violated_constraints,
        )
        
        # Record this correction
        record = CorrectionRecord(
            turn=turn,
            drift_score=drift_score,
            strategy_used=self._get_strategy_name(drift_score),
            prompt=prompt,
            violated_constraints=violated_constraints,
        )
        self.correction_history.append(record)
        
        return prompt
    
    def _get_strategy_name(self, drift_score: float) -> str:
        """Get the name of the strategy used for this drift score."""
        if isinstance(self.strategy, AdaptiveStrategy):
            return self.strategy.get_strategy_name(drift_score)
        return self.strategy.name
    
    def get_correction_history(self) -> List[CorrectionRecord]:
        """Get all corrections that have been generated."""
        return self.correction_history.copy()
    
    def get_correction_summary(self) -> Dict:
        """
        Get summary statistics about corrections applied.
        
        Returns:
            Dictionary with correction statistics
        """
        if not self.correction_history:
            return {
                "total_corrections": 0,
                "by_strategy": {},
                "by_turn": [],
            }
        
        # Count by strategy
        by_strategy: Dict[str, int] = {}
        for record in self.correction_history:
            by_strategy[record.strategy_used] = (
                by_strategy.get(record.strategy_used, 0) + 1
            )
        
        return {
            "total_corrections": len(self.correction_history),
            "by_strategy": by_strategy,
            "by_turn": [
                {
                    "turn": r.turn,
                    "drift_score": round(r.drift_score, 3),
                    "strategy": r.strategy_used,
                }
                for r in self.correction_history
            ],
        }
    
    def reset(self) -> None:
        """Reset correction history."""
        self.correction_history = []
