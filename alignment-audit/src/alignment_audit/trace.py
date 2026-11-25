"""Tamper-evident trace: each event embeds the SHA-256 of the previous one,."""

import hashlib
import json
from pathlib import Path

GENESIS = "0" * 64


def _digest(prev: str, body: dict) -> str:
    """Return the SHA-256 hex digest of the previous hash joined with this event body."""
    return hashlib.sha256((prev + json.dumps(body, sort_keys=True)).encode()).hexdigest()


class Trace:
    """An append-only list of hash-chained events."""

    def __init__(self) -> None:
        """Create an empty trace."""
        self.events: list[dict] = []

    def add(self, kind: str, **data) -> dict:
        """Append an event linked to the previous one.

        Args:
            kind: Event type: start, executed or halt.
            **data: Event payload.

        Returns:
            The stored event, including seq, prev and hash.
        """
        prev = self.events[-1]["hash"] if self.events else GENESIS
        body = {"seq": len(self.events), "kind": kind, "data": data}
        event = {**body, "prev": prev, "hash": _digest(prev, body)}
        self.events.append(event)
        return event

    def save(self, path: Path) -> None:
        """Write the events to `path`, one JSON object per line."""
        path.write_text("".join(json.dumps(e, sort_keys=True) + "\n" for e in self.events))


# NOTE: there is no proof check yet. A verifier would need to confirm that:
#   1. the hash chain is intact (recompute each hash with _digest, check every `prev` link),
#   2. the last event is a `halt` carrying the auditor verdict, and
#   3. the halted action never appears in an `executed` event.
