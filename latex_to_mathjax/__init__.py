import re
import json
import weakref
from anki.notes import Note
from aqt import gui_hooks
from aqt.editor import Editor

_enabled: bool = False
_active_editor: "weakref.ref[Editor] | None" = None


def _convert(text: str) -> str:
    saved: list[str] = []

    def save(s: str) -> str:
        saved.append(s)
        return f"\x00{len(saved) - 1}\x00"

    text = re.sub(r'\\\[[\s\S]*?\\\]', lambda m: save(m.group()), text)
    text = re.sub(r'\\\([\s\S]*?\\\)', lambda m: save(m.group()), text)
    text = re.sub(
        r'\\begin\{equation\*?\}([\s\S]*?)\\end\{equation\*?\}',
        lambda m: save(r'\[' + m.group(1) + r'\]'), text)
    text = re.sub(
        r'\\begin\{align\*?\}([\s\S]*?)\\end\{align\*?\}',
        lambda m: save(r'\[\begin{aligned}' + m.group(1) + r'\end{aligned}\]'), text)
    text = re.sub(r'\$\$([\s\S]*?)\$\$',
                  lambda m: save(r'\[' + m.group(1) + r'\]'), text)
    text = re.sub(r'\$([^$\n]+?)\$',
                  lambda m: save(r'\(' + m.group(1) + r'\)'), text)
    text = re.sub(r'\x00(\d+)\x00', lambda m: saved[int(m.group(1))], text)
    return text


def _needs_conversion(text: str) -> bool:
    return '$' in text or r'\begin' in text


_PASTE_JS = r"""
(function () {
  if (window.__mjInstalled) return;
  window.__mjInstalled = true;
  window.__mjEnabled   = false;

  function mjConvert(text) {
    var saved = [];
    function save(s) { saved.push(s); return '\x00' + (saved.length - 1) + '\x00'; }
    text = text.replace(/\\\[[\s\S]*?\\\]/g,  function(m){ return save(m); });
    text = text.replace(/\\\([\s\S]*?\\\)/g,  function(m){ return save(m); });
    text = text.replace(/\\begin\{equation\*?\}([\s\S]*?)\\end\{equation\*?\}/g,
      function(_,b){ return save('\\[' + b + '\\]'); });
    text = text.replace(/\\begin\{align\*?\}([\s\S]*?)\\end\{align\*?\}/g,
      function(_,b){ return save('\\[\\begin{aligned}' + b + '\\end{aligned}\\]'); });
    text = text.replace(/\$\$([\s\S]*?)\$\$/g,
      function(_,b){ return save('\\[' + b + '\\]'); });
    text = text.replace(/\$([^$\n]+?)\$/g,
      function(_,b){ return save('\\(' + b + '\\)'); });
    text = text.replace(/\x00(\d+)\x00/g, function(_,i){ return saved[+i]; });
    return text;
  }

  document.addEventListener('paste', function (e) {
    if (!window.__mjEnabled) return;
    var plain = e.clipboardData && e.clipboardData.getData('text/plain');
    if (!plain) return;
    if (plain.indexOf('$') === -1 && plain.indexOf('\\begin') === -1) return;

    var converted = mjConvert(plain);
    if (converted === plain) return;

    e.preventDefault();
    e.stopImmediatePropagation();
    document.execCommand('insertText', false, converted);
  }, true);

})();
"""


def _push_state(editor: Editor) -> None:
    label = "MJ ●" if _enabled else "MJ ○"
    color = "#4ade80" if _enabled else "#888888"
    tip = "MathJax: ON — click to disable" if _enabled else "MathJax: OFF — click to enable"
    js = (
        "(function(){"
        f"  var b = document.getElementById('__mjbtn');"
        f"  if (b) {{"
        f"    b.innerHTML = {json.dumps(label)};"
        f"    b.title     = {json.dumps(tip)};"
        f"    b.style.color      = '{color}';"
        f"    b.style.fontWeight = '700';"
        f"  }}"
        f"  window.__mjEnabled = {'true' if _enabled else 'false'};"
        "})();"
    )
    editor.web.eval(js)


def _on_init_buttons(buttons: list, editor: Editor) -> None:
    def toggle(ed: Editor = editor) -> None:
        global _enabled
        _enabled = not _enabled
        _push_state(ed)

    btn = editor.addButton(
        icon=None,
        cmd="mj_toggle",
        func=toggle,
        tip="MathJax: OFF — click to enable",
        label="MJ ○",
        id="__mjbtn",
    )
    buttons.append(btn)


def _on_init(editor: Editor) -> None:
    global _active_editor
    _active_editor = weakref.ref(editor)
    editor.web.eval(_PASTE_JS)
    _push_state(editor)


def _on_load_note(editor: Editor) -> None:
    global _active_editor
    _active_editor = weakref.ref(editor)
    editor.web.eval(_PASTE_JS)
    _push_state(editor)


def _on_typing_timer(note: Note) -> None:
    if not _enabled:
        return

    editor = _active_editor() if _active_editor else None

    changed_indices: list[int] = []
    for i, field_html in enumerate(note.fields):
        if not _needs_conversion(field_html):
            continue
        converted = _convert(field_html)
        if converted != field_html:
            note.fields[i] = converted
            changed_indices.append(i)

    if not changed_indices or editor is None:
        return

    for i in changed_indices:
        safe_html = json.dumps(note.fields[i])
        js = f"""
        (function() {{
            var fields = document.querySelectorAll('.field anki-editable, .field [contenteditable]');
            if (fields[{i}]) {{
                var f = fields[{i}];
                f.innerHTML = {safe_html};
                f.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }}
        }})();
        """
        editor.web.eval(js)


gui_hooks.editor_did_init_buttons.append(_on_init_buttons)
gui_hooks.editor_did_init.append(_on_init)
gui_hooks.editor_did_load_note.append(_on_load_note)
gui_hooks.editor_did_fire_typing_timer.append(_on_typing_timer)
