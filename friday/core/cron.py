"""FRIDAY Cron — Lightweight background task scheduler.

No external DB. Stores jobs in a JSON file.
Runs standalone without full FRIDAY engine.
"""

import asyncio
import json
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


class Job:
    """Represents a scheduled job."""

    def __init__(self, name: str, interval_seconds: int, task: Callable,
                 args: tuple = None, kwargs: dict = None, enabled: bool = True):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.interval = interval_seconds
        self.task = task
        self.args = args or ()
        self.kwargs = kwargs or {}
        self.enabled = enabled
        self.last_run: Optional[datetime] = None
        self.next_run: Optional[datetime] = None
        self.run_count = 0
        self._calculate_next()

    def _calculate_next(self):
        base = self.last_run or datetime.now()
        self.next_run = base + timedelta(seconds=self.interval)

    def should_run(self) -> bool:
        if not self.enabled or not self.next_run:
            return False
        return datetime.now() >= self.next_run

    async def run(self):
        self.last_run = datetime.now()
        self.run_count += 1
        self._calculate_next()
        try:
            result = self.task(*self.args, **self.kwargs)
            if asyncio.iscoroutine(result):
                await result
            return result
        except Exception as e:
            return f"Error: {e}"


class CronScheduler:
    """Lightweight background scheduler with JSON persistence."""

    def __init__(self, state_file: str = "friday_cron.json"):
        self.state_file = Path(state_file).expanduser()
        self.jobs: Dict[str, Job] = {}
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._load_state()

    def schedule(self, name: str, interval_seconds: int, task: Callable,
                 args: tuple = None, kwargs: dict = None) -> Job:
        """Schedule a new repeating job."""
        job = Job(name, interval_seconds, task, args, kwargs)
        self.jobs[job.id] = job
        self._save_state()
        return job

    def cancel(self, job_id: str) -> bool:
        """Cancel a job by ID."""
        if job_id in self.jobs:
            del self.jobs[job_id]
            self._save_state()
            return True
        return False

    def list_jobs(self) -> List[Dict]:
        """Return job summaries."""
        return [
            {
                "id": j.id,
                "name": j.name,
                "interval_sec": j.interval,
                "enabled": j.enabled,
                "last_run": j.last_run.isoformat() if j.last_run else None,
                "next_run": j.next_run.isoformat() if j.next_run else None,
                "run_count": j.run_count,
            }
            for j in self.jobs.values()
        ]

    def _save_state(self):
        """Persist job metadata (not callable objects)."""
        data = {
            "jobs": [
                {
                    "id": j.id,
                    "name": j.name,
                    "interval": j.interval,
                    "enabled": j.enabled,
                    "last_run": j.last_run.isoformat() if j.last_run else None,
                    "run_count": j.run_count,
                }
                for j in self.jobs.values()
            ]
        }
        self.state_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _load_state(self):
        """Load persisted job metadata."""
        if not self.state_file.exists():
            return
        try:
            data = json.loads(self.state_file.read_text(encoding="utf-8"))
            # Note: task callables cannot be restored from JSON
            # They must be re-registered on startup
            # This is a known limitation; production would use a registry
        except Exception:
            pass

    async def start(self):
        """Start the scheduler loop."""
        self._running = True
        self._task = asyncio.create_task(self._loop())

    async def stop(self):
        """Stop the scheduler."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _loop(self):
        """Main scheduler loop — checks jobs every second."""
        while self._running:
            now = time.time()
            for job in self.jobs.values():
                if job.should_run():
                    asyncio.create_task(job.run())
            # Sleep until next second
            await asyncio.sleep(1 - (time.time() % 1))


# Singleton
_scheduler: Optional[CronScheduler] = None

def get_scheduler(state_file: str = "friday_cron.json") -> CronScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = CronScheduler(state_file)
    return _scheduler
