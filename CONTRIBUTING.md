# Contributing

Thanks for wanting to help! Small PRs are great.

## Setup

```bash
git clone https://github.com/tamim0077/wordpop
cd wordpop
python -m venv .venv
.venv/bin/pip install -e ".[test]"     # Windows: .venv\Scripts\pip
pytest
```

You need `ffmpeg` only if you want to burn captions into a video.

## Good things to work on

Look for issues labelled [`good first issue`](https://github.com/tamim0077/wordpop/labels/good%20first%20issue).

**A new style**
1. Add it to `STYLES` in `src/wordpop/styles.py`
2. Use a free font (Google Fonts) and say which one in the README table
3. Re-render the demo (`python docs/make_demo.py <folder with fonts/>`) or attach a screenshot to the PR

**A new transcript format**
Add a test in `tests/test_wordpop.py` with a small real sample, then make `normalize_words` read it.

## Rules of thumb

- Keep it dependency-free.
- Add a test for anything you change.
- Don't change the output of existing styles unless that's the point of the PR (people's videos depend on it).

## Questions

Open an issue, happy to help.
