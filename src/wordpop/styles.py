"""Caption style presets.

Each preset is a `Style`. You can use one by name ("pop", "beast", ...) or build
your own with `Style(...)` / `STYLES["pop"].replace(highlight="#FF00AA")`.
"""
from __future__ import annotations

import dataclasses
import re
from dataclasses import dataclass
from typing import Optional

_ASS_COLOUR = re.compile(r"^&H[0-9A-F]{8}$", re.IGNORECASE)
_HEX_COLOUR = re.compile(r"^#?([0-9A-Fa-f]{6})([0-9A-Fa-f]{2})?$")


def colour(value: str) -> str:
    """Turn "#RRGGBB" / "#RRGGBBAA" (CSS order, AA = opacity) into ASS "&HAABBGGRR".

    ASS colours ("&H00FFFFFF") are passed through unchanged.
    """
    value = value.strip()
    if _ASS_COLOUR.match(value):
        return value.upper()
    m = _HEX_COLOUR.match(value)
    if not m:
        raise ValueError(f"not a colour: {value!r} (use '#RRGGBB' or ASS '&HAABBGGRR')")
    rgb, alpha = m.group(1), m.group(2)
    r, g, b = rgb[0:2], rgb[2:4], rgb[4:6]
    # ASS alpha is transparency (00 = solid), CSS alpha is opacity (FF = solid).
    a = f"{255 - int(alpha, 16):02X}" if alpha else "00"
    return f"&H{a}{b}{g}{r}".upper()


# ASS colours are &HAABBGGRR
YELLOW = "&H004DE1FF"
ICE = "&H00EBBEA5"
INK = "&H001E1E1E"
WHITE = "&H00FFFFFF"
BLACK = "&H00000000"
GREEN = "&H003CFF3C"
RED = "&H003B3BFF"
CYAN = "&H00FFE500"


@dataclass(frozen=True)
class Style:
    """How a caption line looks and how words are grouped into lines.

    font:        font family name (must be installed / visible to libass).
                 None = the `font` passed to build_ass (default "Anton").
    size:        font size on a 1080x1920 canvas.
    bold:        draw the font bold.
    uppercase:   SHOUT THE WORDS.
    max_words:   words per caption line.
    max_span:    a line never stays up longer than this many seconds.
    highlight:   colour of the word being spoken ("#RRGGBB" or ASS colour).
    outline:     outline thickness.
    shadow:      shadow distance.
    pop_scale:   the spoken word starts this % big and settles (100 = no pop).
    glow:        blur the outline in the highlight colour (neon look).
    box:         put the spoken word on a coloured block instead of recolouring it.
    box_colour:  block colour when box=True.
    dim_upcoming: words not said yet are faded out a bit.
    plate:       whole line on a soft dark plate, no per-word highlight.
    """

    font: Optional[str] = None
    size: int = 84
    bold: bool = True
    uppercase: bool = True
    max_words: int = 3
    max_span: float = 1.6
    highlight: str = YELLOW
    outline: int = 7
    shadow: int = 3
    pop_scale: int = 100
    glow: bool = False
    box: bool = False
    box_colour: str = ICE
    dim_upcoming: bool = False
    plate: bool = False

    def replace(self, **changes) -> "Style":
        """A copy with some fields changed."""
        return dataclasses.replace(self, **changes)


STYLES: dict[str, Style] = {
    # Anton caps, live word yellow (the classic short-form clipper look)
    "pop": Style(),
    # heavy white caps, thick black outline, live word pops bigger
    "classic": Style(font="Archivo Black", size=78, bold=False, highlight=WHITE, outline=9, shadow=2,
                     pop_scale=118),
    # rounded cartoon caps, live word green and bouncing
    "beast": Style(font="Luckiest Guy", size=88, bold=False, max_words=2, max_span=1.3, highlight=GREEN,
                   outline=9, shadow=4, pop_scale=120),
    # comic-book caps, live word red
    "comic": Style(font="Bangers", size=96, bold=False, highlight=RED, outline=8, shadow=4, pop_scale=112),
    # heavy caps, live word glowing cyan (gaming)
    "neon": Style(font="Archivo Black", size=76, bold=False, highlight=CYAN, outline=6, shadow=0,
                  pop_scale=110, glow=True),
    # heavy caps, live word sits on a bright block
    "box": Style(highlight=INK, box=True),
    # small sentence case, words fade in as they're said
    "minimal": Style(font="Poppins", size=60, uppercase=False, max_words=5, max_span=2.4, highlight=WHITE,
                     outline=2, shadow=2, dim_upcoming=True),
    # sentence case on a soft dark plate, no per-word highlight
    "clean": Style(font="Poppins", size=62, uppercase=False, max_words=5, max_span=2.4, plate=True),
}


def get_style(style: "str | Style") -> Style:
    if isinstance(style, Style):
        return style
    try:
        return STYLES[style]
    except KeyError:
        raise ValueError(f"unknown style {style!r}; pick one of {', '.join(STYLES)} "
                         f"or pass a Style(...)") from None
