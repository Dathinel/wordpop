# Renders docs/demo.gif: python docs/make_demo.py <folder with fonts/ subfolder>
import sys, subprocess
from pathlib import Path
from wordpop import STYLES, build_ass, burn
sp = Path(sys.argv[1]); fonts = sp / "fonts"; out = sp / "demo"
text = "no way he actually hit that shot from across the map"
words, t = [], 0.2
for w in text.split():
    words.append({"w": w, "s": t, "e": t + 0.28}); t += 0.34
dur = 4.0
bg = out / "bg.mp4"
subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","lavfi","-i",
  f"color=c=0x17171c:s=540x960:d={dur}:r=15","-pix_fmt","yuv420p",str(bg)],check=True)
for name in STYLES:
    ass = build_ass(words, dur, style=name, title=name, layout="blur", margin_v=1330)
    burn(bg, ass, out / f"{name}.mp4", fonts_dir=fonts, extra_args=("-an",))
print("ok")
