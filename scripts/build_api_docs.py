"""Generate API reference documentation from docstrings.

Usage: python scripts/build_api_docs.py
Output: docs/api.html

Introspects code_music's public API and generates a single-page HTML
reference with function signatures, docstrings, and module groupings.
"""

from __future__ import annotations

import html
import importlib
import inspect
import sys
import textwrap
from pathlib import Path


def _get_public_members(module) -> list[tuple[str, object]]:
    """Get all public callable members from a module."""
    members = []
    all_names = getattr(module, "__all__", None) or dir(module)
    for name in sorted(all_names):
        if name.startswith("_"):
            continue
        obj = getattr(module, name, None)
        if obj is None:
            continue
        if callable(obj) or isinstance(obj, type):
            members.append((name, obj))
    return members


def _get_signature(obj) -> str:
    """Get a clean function signature string."""
    try:
        sig = inspect.signature(obj)
        return str(sig)
    except (ValueError, TypeError):
        return "(...)"


def _get_docstring(obj) -> str:
    """Get cleaned docstring."""
    doc = inspect.getdoc(obj)
    if not doc:
        return ""
    return doc


def _get_source_module(obj) -> str:
    """Get the source module path for an object."""
    try:
        mod = inspect.getmodule(obj)
        if mod:
            return mod.__name__
    except Exception:
        pass
    return ""


def _categorize(module_path: str) -> str:
    """Map a module path to a human-readable category."""
    if "harmony" in module_path:
        return "Harmony"
    if "rhythm" in module_path:
        return "Rhythm"
    if "melody" in module_path:
        return "Melody"
    if "analysis" in module_path:
        return "Analysis"
    if "generation" in module_path:
        return "Generation"
    if "serial" in module_path:
        return "Serial / Post-Tonal"
    if "engine" in module_path:
        return "Engine"
    if "synth" in module_path:
        return "Synth"
    if "effects" in module_path:
        return "Effects"
    if "sound_design" in module_path:
        return "Sound Design"
    if "composition" in module_path:
        return "Composition"
    if "notation" in module_path:
        return "Notation"
    if "midi" in module_path:
        return "MIDI"
    if "export" in module_path:
        return "Export"
    if "mastering" in module_path:
        return "Mastering"
    if "automation" in module_path:
        return "Automation"
    if "pattern" in module_path:
        return "Pattern"
    if "playback" in module_path:
        return "Playback"
    if "serialization" in module_path:
        return "Serialization"
    if "cli" in module_path:
        return "CLI"
    return "Other"


def _docstring_to_html(doc: str) -> str:
    """Convert a docstring to HTML with basic formatting."""
    if not doc:
        return ""

    lines = doc.split("\n")
    html_parts: list[str] = []
    in_code = False
    in_list = False

    for line in lines:
        stripped = line.strip()

        # Code blocks
        if stripped.startswith(">>>") or stripped.startswith("..."):
            if not in_code:
                html_parts.append('<pre class="example">')
                in_code = True
            html_parts.append(html.escape(line))
            continue
        elif (
            in_code
            and stripped
            and not stripped.startswith(">>>")
            and not stripped.startswith("...")
        ):
            html_parts.append("</pre>")
            in_code = False

        # Section headers (Args:, Returns:, Example::, etc.)
        if stripped in ("Args:", "Returns:", "Raises:", "Example::", "Example:", "Note:", "Notes:"):
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            html_parts.append(f'<h4 class="doc-section">{html.escape(stripped.rstrip(":"))}</h4>')
            continue

        # Argument descriptions (indented with name: desc)
        if (
            stripped
            and ":" in stripped
            and line.startswith("    ")
            and not line.startswith("        ")
        ):
            parts = stripped.split(":", 1)
            if len(parts) == 2 and len(parts[0].split()) <= 3:
                if not in_list:
                    html_parts.append("<ul>")
                    in_list = True
                html_parts.append(
                    f"<li><code>{html.escape(parts[0].strip())}</code>: "
                    f"{html.escape(parts[1].strip())}</li>"
                )
                continue

        if in_list and (not stripped or not line.startswith("    ")):
            html_parts.append("</ul>")
            in_list = False

        # Empty lines
        if not stripped:
            if in_code:
                html_parts.append("")
            continue

        # Regular text
        html_parts.append(f"<p>{html.escape(stripped)}</p>")

    if in_code:
        html_parts.append("</pre>")
    if in_list:
        html_parts.append("</ul>")

    return "\n".join(html_parts)


def build_api_docs():
    """Generate docs/api.html from code_music's public API."""
    # Add project root to path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

    import code_music

    # Collect all public members
    members = _get_public_members(code_music)

    # Categorize by source module
    categories: dict[str, list[dict]] = {}
    for name, obj in members:
        source_mod = _get_source_module(obj)
        category = _categorize(source_mod)
        sig = _get_signature(obj)
        doc = _get_docstring(obj)
        is_class = isinstance(obj, type)

        if category not in categories:
            categories[category] = []

        entry = {
            "name": name,
            "signature": sig,
            "docstring": doc,
            "source": source_mod,
            "is_class": is_class,
        }

        # For classes, also get methods
        if is_class:
            methods = []
            for method_name in sorted(dir(obj)):
                if method_name.startswith("_") and method_name != "__init__":
                    continue
                method = getattr(obj, method_name, None)
                if method and callable(method) and not isinstance(method, type):
                    method_sig = _get_signature(method)
                    method_doc = _get_docstring(method)
                    if method_doc or method_name == "__init__":
                        methods.append(
                            {
                                "name": method_name,
                                "signature": method_sig,
                                "docstring": method_doc,
                            }
                        )
            entry["methods"] = methods

        categories[category].append(entry)

    # Sort categories by relevance
    category_order = [
        "Engine",
        "Harmony",
        "Melody",
        "Rhythm",
        "Generation",
        "Analysis",
        "Composition",
        "Effects",
        "Sound Design",
        "Synth",
        "Pattern",
        "Notation",
        "MIDI",
        "Export",
        "Mastering",
        "Automation",
        "Playback",
        "Serialization",
        "Serial / Post-Tonal",
        "CLI",
        "Other",
    ]

    total_functions = sum(len(entries) for entries in categories.values())
    total_categories = len(categories)

    # Generate HTML
    nav_items = []
    content_sections = []

    for cat in category_order:
        entries = categories.get(cat)
        if not entries:
            continue

        cat_id = cat.lower().replace(" ", "-").replace("/", "-")
        nav_items.append(
            f'<a href="#{cat_id}" class="nav-link">{html.escape(cat)} ({len(entries)})</a>'
        )

        section_html = [f'<section id="{cat_id}">']
        section_html.append(
            f'<h2>{html.escape(cat)} <span class="count">({len(entries)})</span></h2>'
        )

        for entry in entries:
            kind = "class" if entry["is_class"] else "def"
            section_html.append(f'<div class="func" id="{entry["name"]}">')
            section_html.append(
                f'<div class="func-header">'
                f'<span class="kind">{kind}</span> '
                f'<span class="func-name">{html.escape(entry["name"])}</span>'
                f'<span class="sig">{html.escape(entry["signature"])}</span>'
                f"</div>"
            )

            if entry["source"]:
                section_html.append(
                    f'<div class="source">from {html.escape(entry["source"])}</div>'
                )

            if entry["docstring"]:
                doc_html = _docstring_to_html(entry["docstring"])
                section_html.append(f'<div class="doc">{doc_html}</div>')

            # Class methods
            if entry.get("methods"):
                section_html.append('<div class="methods">')
                for method in entry["methods"]:
                    section_html.append(
                        f'<div class="method">'
                        f'<span class="method-name">.{html.escape(method["name"])}</span>'
                        f'<span class="sig">{html.escape(method["signature"])}</span>'
                    )
                    if method["docstring"]:
                        # First line only for methods
                        first_line = method["docstring"].split("\n")[0]
                        section_html.append(f'<p class="method-doc">{html.escape(first_line)}</p>')
                    section_html.append("</div>")
                section_html.append("</div>")

            section_html.append("</div>")

        section_html.append("</section>")
        content_sections.append("\n".join(section_html))

    version = getattr(code_music, "__version__", "dev")

    page_html = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>code-music API Reference</title>
<style>
:root {{
  --bg: #0a0a10;
  --bg2: #12121a;
  --bg3: #1a1a25;
  --fg: #e0e0e0;
  --fg2: #888;
  --accent: #7755ff;
  --accent2: #55aaff;
  --green: #44cc88;
  --orange: #ffaa44;
  --mono: "SF Mono", "Fira Code", "JetBrains Mono", Menlo, Consolas, monospace;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
  font-family: var(--mono);
  background: var(--bg);
  color: var(--fg);
  line-height: 1.6;
  font-size: 14px;
}}
.layout {{
  display: flex;
  min-height: 100vh;
}}
.sidebar {{
  width: 260px;
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  overflow-y: auto;
  background: var(--bg2);
  border-right: 1px solid var(--bg3);
  padding: 20px 16px;
}}
.sidebar h1 {{
  font-size: 16px;
  color: var(--accent);
  margin-bottom: 4px;
}}
.sidebar .version {{
  font-size: 12px;
  color: var(--fg2);
  margin-bottom: 4px;
}}
.sidebar .stats {{
  font-size: 11px;
  color: var(--fg2);
  margin-bottom: 16px;
}}
.sidebar input {{
  width: 100%;
  padding: 6px 10px;
  background: var(--bg3);
  border: 1px solid #333;
  border-radius: 4px;
  color: var(--fg);
  font-family: var(--mono);
  font-size: 12px;
  margin-bottom: 12px;
}}
.sidebar input:focus {{
  outline: none;
  border-color: var(--accent);
}}
.nav-link {{
  display: block;
  color: var(--fg2);
  text-decoration: none;
  font-size: 12px;
  padding: 3px 0;
}}
.nav-link:hover {{ color: var(--accent); }}
.main {{
  margin-left: 260px;
  padding: 30px 40px;
  max-width: 900px;
}}
section {{
  margin-bottom: 40px;
}}
h2 {{
  color: var(--accent);
  font-size: 18px;
  margin-bottom: 16px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--bg3);
}}
h2 .count {{ color: var(--fg2); font-size: 13px; }}
.func {{
  background: var(--bg2);
  border: 1px solid var(--bg3);
  border-radius: 6px;
  padding: 14px 18px;
  margin-bottom: 12px;
}}
.func-header {{
  font-size: 14px;
  margin-bottom: 6px;
  word-break: break-all;
}}
.kind {{
  color: var(--orange);
  font-size: 11px;
  font-weight: bold;
  text-transform: uppercase;
}}
.func-name {{
  color: var(--green);
  font-weight: bold;
}}
.sig {{ color: var(--fg2); }}
.source {{
  font-size: 11px;
  color: var(--fg2);
  margin-bottom: 8px;
}}
.doc {{ font-size: 13px; color: var(--fg); }}
.doc p {{ margin-bottom: 6px; }}
.doc h4.doc-section {{
  color: var(--accent2);
  font-size: 12px;
  margin: 10px 0 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}}
.doc ul {{
  list-style: none;
  padding-left: 12px;
  margin: 4px 0 8px;
}}
.doc ul li {{
  font-size: 12px;
  margin-bottom: 3px;
}}
.doc ul li code {{
  color: var(--green);
  font-weight: bold;
}}
.doc pre.example {{
  background: var(--bg);
  border: 1px solid var(--bg3);
  border-radius: 4px;
  padding: 8px 12px;
  font-size: 12px;
  overflow-x: auto;
  margin: 6px 0;
  color: var(--fg2);
}}
.methods {{
  border-top: 1px solid var(--bg3);
  margin-top: 10px;
  padding-top: 8px;
}}
.method {{
  padding: 4px 0;
}}
.method-name {{
  color: var(--accent2);
  font-weight: bold;
  font-size: 13px;
}}
.method .sig {{ font-size: 12px; }}
.method-doc {{ font-size: 12px; color: var(--fg2); margin-top: 2px; }}
</style>
</head>
<body>
<div class="layout">
<nav class="sidebar">
  <h1>code-music</h1>
  <div class="version">v{html.escape(version)}</div>
  <div class="stats">{total_functions} functions, {total_categories} modules</div>
  <input type="text" id="search" placeholder="Search functions..." autocomplete="off">
  {chr(10).join(f"  {item}" for item in nav_items)}
</nav>
<main class="main">
  <h1 style="color:var(--accent);margin-bottom:8px;">API Reference</h1>
  <p style="color:var(--fg2);margin-bottom:30px;">
    {total_functions} public functions and classes across {total_categories} modules.
    Auto-generated from docstrings.
  </p>
  {chr(10).join(content_sections)}
</main>
</div>
<script>
const search = document.getElementById('search');
const funcs = document.querySelectorAll('.func');
search.addEventListener('input', () => {{
  const q = search.value.toLowerCase();
  funcs.forEach(f => {{
    const name = f.id.toLowerCase();
    const text = f.textContent.toLowerCase();
    f.style.display = (name.includes(q) || text.includes(q)) ? '' : 'none';
  }});
}});
</script>
</body>
</html>"""

    out_path = project_root / "docs" / "api.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(page_html)
    print(f"Generated {out_path} ({total_functions} functions, {total_categories} modules)")


if __name__ == "__main__":
    build_api_docs()
