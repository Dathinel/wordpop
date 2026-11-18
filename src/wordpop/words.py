"""Read word timings from whatever your transcriber gives you.

Everything is normalised to a list of {"w": text, "s": start_sec, "e": end_sec}.

Understood inputs:
  - a list of dicts with word/text + start/end keys
    (OpenAI Whisper verbose_json, faster-whisper, WhisperX, Deepgram, AssemblyAI*)
  - a list of objects with .word/.start/.end attributes (faster-whisper `Word`)
  - a full response dict: {"words": [...]}, {"segments": [{"words": [...]}]},
    or Deepgram's {"results": {"channels": [{"alternatives": [{"words": [...]}]}]}}

* AssemblyAI gives milliseconds: pass `ms=True`.
"""
from __future__ import annotations

from typing import Any, Iterable

Word = dict  # {"w": str, "s": float, "e": float}

_TEXT_KEYS = ("w", "punctuated_word", "word", "text")
_START_KEYS = ("s", "start")
_END_KEYS = ("e", "end")


def _get(item: Any, keys: tuple[str, ...]):
    for k in keys:
        if isinstance(item, dict):
            if item.get(k) is not None:
                return item[k]
        elif getattr(item, k, None) is not None:
            return getattr(item, k)
    return None


def _unwrap(data: Any) -> Iterable[Any]:
    if isinstance(data, dict):
        if "results" in data:  # Deepgram
            try:
                return data["results"]["channels"][0]["alternatives"][0]["words"]
            except (KeyError, IndexError, TypeError):
                raise ValueError("Deepgram response has no words") from None
        if isinstance(data.get("words"), list):
            return data["words"]
        if isinstance(data.get("segments"), list):
            out: list = []
            for seg in data["segments"]:
                ws = _get(seg, ("words",))
                if ws:
                    out.extend(ws)
            return out
        raise ValueError("no 'words' or 'segments' in this transcript")
    return data


def normalize_words(data: Any, ms: bool = False) -> list[Word]:
    """Return [{"w", "s", "e"}] sorted by start time. Empty words are dropped."""
    scale = 0.001 if ms else 1.0
    words: list[Word] = []
    for item in _unwrap(data):
        text, start, end = _get(item, _TEXT_KEYS), _get(item, _START_KEYS), _get(item, _END_KEYS)
        if text is None or start is None or end is None:
            raise ValueError(f"word needs text, start and end: {item!r}")
        text = str(text).strip()
        if not text:
            continue
        s, e = float(start) * scale, float(end) * scale
        words.append({"w": text, "s": s, "e": max(e, s)})
    words.sort(key=lambda w: w["s"])
    return words


def clip_words(words: list[Word], start: float, end: float) -> list[Word]:
    """Words between `start` and `end`, with times moved so `start` is 0.

    Use this when you cut a clip out of a long video and need its captions.
    """
    out = []
    for w in words:
        if w["e"] > start and w["s"] < end:
            out.append({"w": w["w"], "s": max(0.0, w["s"] - start), "e": min(end, w["e"]) - start})
    return out
