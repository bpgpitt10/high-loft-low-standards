from pathlib import Path

path = Path('index.html')
html = path.read_text()

tagline = '<p class="sectionlead">The numbers change. The tendencies linger. This is the closest thing we have to each player’s golfing DNA.</p>'
search = '<label class="player-search scouting-player-search"><input type="search" data-profile-search placeholder="Search player…" autocomplete="off" aria-label="Search player"></label>'
if tagline not in html:
    raise SystemExit('Could not find scouting tagline')
html = html.replace(tagline, search, 1)

old_tools = '''<div class="large-field-tools profile-directory" data-profile-tools hidden>\n  <label class="player-search"><span>Find a player</span><input type="search" data-profile-search placeholder="Type a player name…" autocomplete="off"></label>\n  <div class="large-field-status" data-profile-count aria-live="polite"></div>\n</div>'''
new_tools = '''<div class="large-field-tools profile-directory" data-profile-tools hidden>\n  <div class="large-field-status" data-profile-count aria-live="polite"></div>\n</div>'''
if old_tools not in html:
    raise SystemExit('Could not find current profile directory tools')
html = html.replace(old_tools, new_tools, 1)

css_needle = '.player-search input::placeholder{color:#6f7b72}\n.large-field-status'
css_replacement = '.player-search input::placeholder{color:#6f7b72}\n.scouting-head .scouting-meta{max-width:none;gap:28px}\n.scouting-head .scouting-player-search{flex:0 1 320px;min-width:260px}\n.profile-directory{justify-content:flex-end}\n.large-field-status'
if css_needle not in html:
    raise SystemExit('Could not find homepage search CSS insertion point')
html = html.replace(css_needle, css_replacement, 1)

path.write_text(html)

check = path.read_text()
assert tagline not in check
assert '<span>Find a player</span>' not in check
assert 'class="player-search scouting-player-search"' in check
assert 'placeholder="Search player…"' in check
print('Moved scouting search into header')
