"""
Trade Journal & Notes System
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytz

IST = pytz.timezone("Asia/Kolkata")


class TradeJournal:
    """
    Trade journal and notes system
    """

    def __init__(self, journal_file: Optional[Path] = None):
        if journal_file is None:
            journal_file = Path(__file__).parent.parent.parent / "outputs" / "trade_journal.jsonl"
        self.journal_file = journal_file
        self.journal_file.parent.mkdir(parents=True, exist_ok=True)

    def add_note(
        self, position_id: str, note: str, tags: Optional[List[str]] = None, note_type: str = "general"
    ) -> Dict[str, Any]:
        """Add a note to a position"""
        journal_entry = {
            "id": f"NOTE_{datetime.now(IST).strftime('%Y%m%d%H%M%S%f')}",
            "position_id": position_id,
            "note": note,
            "tags": tags or [],
            "type": note_type,
            "timestamp": datetime.now(IST).isoformat(),
        }

        # Append to journal file
        with open(self.journal_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(journal_entry, default=str) + "\n")

        return journal_entry

    def get_notes(
        self, position_id: Optional[str] = None, tags: Optional[List[str]] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get notes"""
        notes = []

        if not self.journal_file.exists():
            return notes

        with open(self.journal_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entry = json.loads(line)

                        # Filter by position_id
                        if position_id and entry.get("position_id") != position_id:
                            continue

                        # Filter by tags
                        if tags:
                            entry_tags = entry.get("tags", [])
                            if not any(tag in entry_tags for tag in tags):
                                continue

                        notes.append(entry)
                    except:
                        pass

        # Sort by timestamp (newest first)
        notes.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        return notes[:limit]

    def search_notes(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search notes by text"""
        notes = []
        query_lower = query.lower()

        if not self.journal_file.exists():
            return notes

        with open(self.journal_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entry = json.loads(line)
                        note_text = entry.get("note", "").lower()

                        if query_lower in note_text:
                            notes.append(entry)
                    except:
                        pass

        notes.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return notes[:limit]

    def get_position_notes(self, position_id: str) -> List[Dict[str, Any]]:
        """Get all notes for a position"""
        return self.get_notes(position_id=position_id)

    def add_trade_analysis(self, position_id: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Add trade analysis"""
        analysis_entry = {
            "id": f"ANALYSIS_{datetime.now(IST).strftime('%Y%m%d%H%M%S%f')}",
            "position_id": position_id,
            "analysis": analysis,
            "timestamp": datetime.now(IST).isoformat(),
        }

        with open(self.journal_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(analysis_entry, default=str) + "\n")

        return analysis_entry


# Global instance
_trade_journal = TradeJournal()


def get_trade_journal() -> TradeJournal:
    """Get global trade journal instance"""
    return _trade_journal
