from pathlib import Path
import re

CSS = r'''
<style id="recap-header-search-ui">
.recap-search-head{align-items:flex-end;gap:20px}
.recap-search-head .section-title{min-width:0}
.recap-header-search{display:grid;gap:7px;flex:0 1 320px;width:min(320px,100%);margin-left:auto}
.recap-header-search span{color:#9ba79d;font-size:10px;font-weight:900;letter-spacing:.08em;text-transform:uppercase}
.recap-header-search input{width:100%;border:1px solid #314137;border-radius:12px;background:#0f1711;color:#f2f4ef;padding:12px 14px;font:inherit;font-size:14px;outline:none}
.recap-header-search input:focus{border-color:#6c8c46;box-shadow:0 0 0 2px rgba(182,243,74,.08)}
.recap-header-search input::placeholder{color:#6f7b72}
@media(max-width:700px){.recap-search-head{align-items:stretch;flex-direction:column}.recap-header-search{width:100%;max-width:none;flex-basis:auto;margin-left:0}}
</style>
'''

JS = r'''
<script id="recap-header-search-runtime">
(() => {
  function playerName(card, selector){
    const node=card.querySelector(selector);
    if(!node)return '';
    if(selector==='h3')return (node.firstChild?.textContent||node.textContent||'').trim().toLowerCase();
    return (node.textContent||'').trim().toLowerCase();
  }
  function filterCards(input, sectionSelector, gridSelector, nameSelector){
    const section=document.querySelector(sectionSelector);
    const grid=section?.querySelector(gridSelector);
    if(!grid)return;
    const q=input.value.trim().toLowerCase();
    [...grid.children].forEach(card=>{
      if(card.tagName!=='ARTICLE')return;
      const match=!q||playerName(card,nameSelector).includes(q);
      card.hidden=!match;
    });
  }
  document.addEventListener('input',e=>{
    if(e.target.matches('[data-carnage-search]'))filterCards(e.target,'#carnage','.hole-grid','.player-name');
    if(e.target.matches('[data-round-player-search]'))filterCards(e.target,'#players','.recap-players','h3');
  });
})();
</script>
'''


def has_search_input(html: str, data_attr: str) -> bool:
    return bool(re.search(rf'<input[^>]*\b{re.escape(data_attr)}\b', html))


def add_header_search(html: str, section_class: str, data_attr: str) -> str:
    if has_search_input(html, data_attr):
        return html
    pattern = re.compile(
        rf'(<section class="section {section_class}"[^>]*><div class="wrap"><div class="sectionhead marked)(">)(.*?)(<p class="sectionlead">.*?</p>)(</div>)',
        flags=re.S,
    )
    match = pattern.search(html)
    if not match:
        raise RuntimeError(f'Could not find {section_class} header')
    opener = match.group(1) + ' recap-search-head' + match.group(2)
    search = (
        f'<label class="recap-header-search"><span>Search player</span>'
        f'<input type="search" {data_attr} placeholder="Search player…" autocomplete="off" aria-label="Search player"></label>'
    )
    replacement = opener + match.group(3) + search + match.group(5)
    return html[:match.start()] + replacement + html[match.end():]


def remove_old_directory_rows(html: str) -> str:
    html = re.sub(
        r'\s*<div class="large-field-tools carnage-directory"[^>]*>\s*<div class="large-field-status"[^>]*></div>\s*</div>\s*',
        '\n',
        html,
        count=1,
        flags=re.S,
    )
    html = re.sub(
        r'\s*<div class="large-field-tools player-directory"[^>]*>\s*<label class="player-search">.*?</label>\s*<div class="large-field-status"[^>]*></div>\s*</div>\s*',
        '\n',
        html,
        count=1,
        flags=re.S,
    )
    return html


def assert_header_clean(html: str, section_class: str, data_attr: str) -> None:
    assert has_search_input(html, data_attr), f'Missing real {data_attr} input'
    section = re.search(
        rf'<section class="section {section_class}".*?(?=<div class="hole-grid"|<div class="recap-players)',
        html,
        flags=re.S,
    )
    assert section, f'Missing {section_class} header block'
    assert '<p class="sectionlead">' not in section.group(0), f'Stale right-side tagline in {section_class}'


changed = []
for path in sorted(Path('recaps').glob('*.html')):
    html = path.read_text()
    if 'carnage-section' not in html or 'player-section' not in html:
        continue
    original = html
    html = remove_old_directory_rows(html)
    html = add_header_search(html, 'carnage-section', 'data-carnage-search')
    html = add_header_search(html, 'player-section', 'data-round-player-search')
    if 'id="recap-header-search-ui"' not in html:
        html = html.replace('</head>', CSS + '</head>', 1)
    if 'id="recap-header-search-runtime"' not in html:
        html = html.replace('</body>', JS + '</body>', 1)
    if html != original:
        path.write_text(html)
        changed.append(path.name)

for path in sorted(Path('recaps').glob('*.html')):
    html = path.read_text()
    if 'carnage-section' not in html or 'player-section' not in html:
        continue
    assert_header_clean(html, 'carnage-section', 'data-carnage-search')
    assert_header_clean(html, 'player-section', 'data-round-player-search')
    assert html.count('recap-search-head') >= 2, path

if not changed:
    raise SystemExit('No recap pages needed a patch')
print(f'Patched {len(changed)} recap pages: ' + ', '.join(changed))
