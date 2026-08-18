# High Loft / Low Standards

Static league site generated from SGT JSON exports.

## Update workflow
1. Put new `SGT_*.json` exports in `/mnt/data` (or adjust `SRC` in `build_site.py`).
2. Update recap/profile copy as needed.
3. Run `python build_site.py`.
4. Commit/push the generated site. GitHub Pages or Cloudflare Pages can publish automatically.

The site deliberately keeps gross and net separate and uses SGT-supplied strokes-gained values.
