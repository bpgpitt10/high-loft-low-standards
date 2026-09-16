from pathlib import Path

SYNC_SCRIPT = r'''
<script id="recap-linked-search-runtime">
(() => {
  let syncing=false;
  document.addEventListener('input', e => {
    if(syncing || !e.target.matches('[data-carnage-search],[data-round-player-search]')) return;
    const other = e.target.matches('[data-carnage-search]')
      ? document.querySelector('[data-round-player-search]')
      : document.querySelector('[data-carnage-search]');
    if(!other || other.value===e.target.value) return;
    syncing=true;
    other.value=e.target.value;
    other.dispatchEvent(new Event('input',{bubbles:true}));
    syncing=false;
  }, true);
})();
</script>
'''

changed=[]
for path in sorted(Path('recaps').glob('*.html')):
    html=path.read_text()
    if '<input type="search" data-carnage-search' not in html or '<input type="search" data-round-player-search' not in html:
        continue
    original=html
    html=html.replace('<label class="recap-header-search"><span>Search player</span><input', '<label class="recap-header-search"><input')
    if 'id="recap-linked-search-runtime"' not in html:
        html=html.replace('</body>', SYNC_SCRIPT + '</body>', 1)
    if html != original:
        path.write_text(html)
        changed.append(path.name)

if not changed:
    raise SystemExit('No recap pages needed linked-search patching')

for path in sorted(Path('recaps').glob('*.html')):
    html=path.read_text()
    if '<input type="search" data-carnage-search' not in html or '<input type="search" data-round-player-search' not in html:
        continue
    assert '<span>Search player</span>' not in html, path
    assert 'id="recap-linked-search-runtime"' in html, path

print(f'Patched {len(changed)} recap pages: ' + ', '.join(changed))
