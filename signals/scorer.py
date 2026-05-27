import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

def score_signal(keywords: List[str], numbers: List[int]) -> Tuple[int, str]:
    """Compute a confidence score (0-100) and a human‑readable reason.
    Heuristic:
    * Base score 30.
    * +15 for each distinct keyword (max +45).
    * If any number >= 1000, +20.
    * Else if any number >= 500, +15.
    * If both keywords and numbers present, add extra +10.
    The final score is capped at 100.
    """
    base = 30
    kw_score = min(len(set(keywords)) * 15, 45)
    num_score = 0
    if numbers:
        max_num = max(numbers)
        if max_num >= 1000:
            num_score = 20
        elif max_num >= 500:
            num_score = 15
    bonus = 10 if keywords and numbers else 0
    total = min(base + kw_score + num_score + bonus, 100)
    reason_parts = []
    if keywords:
        reason_parts.append(f"found keywords: {', '.join(set(keywords))}")
    if numbers:
        reason_parts.append(f"numeric hiring signal(s): {', '.join(map(str, numbers))}")
    if not reason_parts:
        reason_parts.append("no clear hiring signal detected")
    reason = "; ".join(reason_parts)
    logger.debug("Score %d for reason: %s", total, reason)
    return total, reason
