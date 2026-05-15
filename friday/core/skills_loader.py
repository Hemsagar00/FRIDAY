"""FRIDAY Skills Loader — Autodiscover and execute SKILL.md playbooks."""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional


class SkillLoader:
    """Discovers SKILL.md files and turns them into callable procedures."""

    def __init__(self, skills_root: str = "skills"):
        self.skills_root = Path(skills_root).expanduser()
        self._skills: Dict[str, Dict] = {}
        self._discover()

    def _discover(self):
        """Scan skills/ directory for SKILL.md files."""
        if not self.skills_root.exists():
            return
        for skill_dir in self.skills_root.iterdir():
            if skill_dir.is_dir():
                skill_file = skill_dir / "SKILL.md"
                if skill_file.exists():
                    self._parse_skill(skill_dir.name, skill_file)

    def _parse_skill(self, name: str, path: Path):
        """Parse trigger + steps from a SKILL.md."""
        text = path.read_text(encoding="utf-8")
        # Extract trigger
        trigger = ""
        trigger_match = re.search(r'##\s*Trigger\s*\n\s*\n?(.+?)(?=\n##|\Z)', text, re.S | re.I)
        if trigger_match:
            trigger = trigger_match.group(1).strip()
        # Extract steps
        steps = []
        steps_match = re.search(r'##\s*Steps?\s*\n\s*\n?(.+?)(?=\n##|\Z)', text, re.S | re.I)
        if steps_match:
            raw_steps = steps_match.group(1).strip()
            for line in raw_steps.splitlines():
                line = line.strip()
                if line.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "-", "*")):
                    step = re.sub(r'^[0-9]+[.\)]\s*', '', line)
                    step = re.sub(r'^[-*]\s*', '', step)
                    steps.append(step)
        self._skills[name] = {
            "trigger": trigger,
            "steps": steps,
            "path": str(path),
        }

    def list_skills(self) -> List[str]:
        return list(self._skills.keys())

    def get(self, name: str) -> Optional[Dict]:
        return self._skills.get(name)

    def match(self, query: str) -> Optional[str]:
        """Find a skill whose trigger loosely matches the query."""
        q = query.lower()
        for name, skill in self._skills.items():
            trigger = skill.get("trigger", "").lower()
            # Simple keyword overlap matching
            if any(word in q for word in trigger.split() if len(word) > 3):
                return name
            # Also check if skill name is in query
            if name.replace("-", " ") in q or name in q:
                return name
        return None

    def describe(self, name: str) -> str:
        skill = self._skills.get(name)
        if not skill:
            return f"No skill named '{name}'"
        lines = [f"# Skill: {name}", f"\n**Trigger:** {skill['trigger']}", "\n**Steps:**"]
        for i, step in enumerate(skill["steps"], 1):
            lines.append(f"{i}. {step}")
        return "\n".join(lines)


# Global singleton
_loader: Optional[SkillLoader] = None

def get_loader() -> SkillLoader:
    global _loader
    if _loader is None:
        _loader = SkillLoader()
    return _loader
