"""Burn an .ass file into a video with ffmpeg (needs ffmpeg built with libass)."""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Union

PathLike = Union[str, os.PathLike]


def burn(video: PathLike, ass: str, out: PathLike, *, ffmpeg: Optional[str] = None,
         fonts_dir: Optional[PathLike] = None, crf: int = 20, extra_args: tuple = ()) -> Path:
    """Render `video` with the subtitle text `ass` burned in, to `out`.

    ass:       the .ass file text (from build_ass).
    fonts_dir: a folder of .ttf/.otf files for libass to use (handy if the
               caption fonts aren't installed system-wide).
    """
    exe = ffmpeg or shutil.which("ffmpeg")
    if not exe:
        raise RuntimeError("ffmpeg not found; install it or pass ffmpeg='path/to/ffmpeg'")
    video, out = Path(video).resolve(), Path(out).resolve()
    with tempfile.TemporaryDirectory() as tmp:
        # The ass filter's path escaping is painful (esp. on Windows), so run
        # ffmpeg inside the temp folder and use plain relative names.
        Path(tmp, "captions.ass").write_text(ass, encoding="utf-8")
        vf = "ass=captions.ass"
        if fonts_dir:
            fonts = Path(tmp, "fonts")
            shutil.copytree(fonts_dir, fonts)
            vf += ":fontsdir=fonts"
        cmd = [exe, "-hide_banner", "-loglevel", "error", "-nostdin", "-y", "-i", str(video),
               "-vf", vf, "-c:v", "libx264", "-crf", str(crf), "-preset", "veryfast",
               "-c:a", "copy", *extra_args, str(out)]
        proc = subprocess.run(cmd, cwd=tmp, capture_output=True, text=True, errors="replace")
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed ({proc.returncode}):\n{proc.stderr[-3000:]}")
    return out
