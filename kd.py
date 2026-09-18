#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
kd.py – PlantUML-Klassen-/Objektdiagramme erzeugen, mit fertigem Design-Preset.

Voraussetzung: 'plantuml' muss lokal installiert sein (z. B. `brew install plantuml`
auf macOS), inklusive Java. Das Skript ruft es nur per Kommandozeile auf.

Nutzung:
    uv run kd.py diagramm.puml
    uv run kd.py "class Foo { +bar: Text }"
    echo "class Foo" | uv run kd.py -
    uv run kd.py diagramm.puml --theme dark -o ausgabe.svg

Enthält der Input schon einen eigenen 'skinparam'-Block, wird dieser respektiert
und kein Preset injiziert – so lässt sich das Design bei Bedarf komplett selbst
bestimmen.
"""
import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

THEMES = {
    "tgi": """skinparam {
  classAttributeIconSize 0
  shadowing false
  defaultFontName "Arial"
  defaultFontSize 13
  BackgroundColor transparent
  ClassBackgroundColor #FAFAFA
  ClassBorderColor #555555
  ClassArrowColor #333333
  ObjectBackgroundColor #FAFAFA
  ObjectBorderColor #555555
}
hide circle""",
    "dark": """skinparam {
  classAttributeIconSize 0
  shadowing false
  defaultFontName "Arial"
  defaultFontSize 13
  BackgroundColor #1e1e1e
  ClassBackgroundColor #2d2d2d
  ClassBorderColor #888888
  ClassArrowColor #aaaaaa
  ClassFontColor #eeeeee
  ObjectBackgroundColor #2d2d2d
  ObjectBorderColor #888888
  ObjectFontColor #eeeeee
}
hide circle""",
    "minimal": """skinparam {
  classAttributeIconSize 0
  shadowing false
  defaultFontName "Helvetica"
  defaultFontSize 12
  BackgroundColor transparent
  ClassBackgroundColor white
  ClassBorderColor black
  ClassArrowColor black
}
hide circle""",
}


def build_source(body: str, theme: str) -> tuple[str, bool]:
    """Baut den vollständigen PlantUML-Quelltext. Gibt (quelltext, preset_angewendet) zurück."""
    body = body.strip()
    has_startuml = body.startswith("@startuml")
    has_skinparam = "skinparam" in body

    if has_skinparam:
        if not has_startuml:
            body = f"@startuml\n{body}\n@enduml"
        return body, False

    style = THEMES.get(theme, THEMES["tgi"])
    if has_startuml:
        body = body.replace("@startuml", f"@startuml\n{style}", 1)
    else:
        body = f"@startuml\n{style}\n{body}\n@enduml"
    return body, True


def render(source: str) -> str:
    if not shutil.which("plantuml"):
        sys.exit(
            "Fehler: 'plantuml' ist nicht installiert oder nicht im PATH.\n"
            "Installation z. B. mit: brew install plantuml (macOS)\n"
            "oder siehe https://plantuml.com/download"
        )
    with tempfile.TemporaryDirectory() as tmp:
        puml = Path(tmp) / "diagramm.puml"
        puml.write_text(source, encoding="utf-8")
        result = subprocess.run(
            ["plantuml", "-tsvg", str(puml)],
            capture_output=True, text=True, timeout=30,
        )
        svg_path = puml.with_suffix(".svg")
        if result.returncode != 0 or not svg_path.exists():
            sys.exit(f"PlantUML-Fehler:\n{result.stderr}")
        return svg_path.read_text(encoding="utf-8")


def clean_for_embed(svg: str) -> str:
    """Entfernt PlantUML-Metadaten, die zum Einbetten (z. B. in Jupyter-Markdown) nicht gebraucht werden."""
    svg = re.sub(r"<\?plantuml[^>]*\?>", "", svg)
    svg = re.sub(r"<!--[^>]*-->", "", svg)
    svg = re.sub(r'\s+data-[a-zA-Z0-9-]+="[^"]*"', "", svg)
    svg = re.sub(r'\s+contentStyleType="[^"]*"', "", svg)
    svg = re.sub(r'\s+preserveAspectRatio="[^"]*"', "", svg)
    svg = re.sub(r'\s+version="[^"]*"', "", svg)
    svg = re.sub(r'\s+zoomAndPan="[^"]*"', "", svg)
    svg = re.sub(r"font-family=\"'([^']*)'\"", r'font-family="\1"', svg)
    svg = svg.replace("<defs/>", "")
    svg = re.sub(r"[ \t]{2,}", " ", svg)
    return svg.strip()


def copy_to_clipboard(text: str) -> bool:
    if shutil.which("pbcopy"):
        cmd = ["pbcopy"]
    elif shutil.which("clip"):
        cmd = ["clip"]
    elif shutil.which("xclip"):
        cmd = ["xclip", "-selection", "clipboard"]
    elif shutil.which("xsel"):
        cmd = ["xsel", "--clipboard", "--input"]
    else:
        return False
    try:
        subprocess.run(cmd, input=text.encode("utf-8"), check=True)
        return True
    except Exception:
        return False


def read_input(arg: str) -> str:
    if arg == "-":
        return sys.stdin.read()
    path = Path(arg)
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return arg


def main() -> None:
    parser = argparse.ArgumentParser(description="PlantUML-Klassendiagramm erzeugen (TGI-Stil als Standard).")
    parser.add_argument("input", help="Pfad zu einer .puml-Datei, PlantUML-Text direkt, oder '-' für stdin")
    parser.add_argument("-o", "--out", help="Ziel-SVG-Datei (Standard: neben dem Input, sonst diagramm.svg)")
    parser.add_argument(
        "--theme", choices=sorted(THEMES.keys()), default="tgi",
        help="Vordefiniertes Design (wird ignoriert, wenn der Input schon einen eigenen skinparam-Block enthält)",
    )
    parser.add_argument("--no-clipboard", action="store_true", help="Nicht in die Zwischenablage kopieren")
    args = parser.parse_args()

    body = read_input(args.input)
    source, preset_applied = build_source(body, args.theme)
    svg = render(source)

    in_path = Path(args.input)
    if args.out:
        out_path = Path(args.out)
    elif args.input != "-" and in_path.is_file():
        out_path = in_path.with_suffix(".svg")
    else:
        out_path = Path("diagramm.svg")
    out_path.write_text(svg, encoding="utf-8")
    print(f"✓ SVG gespeichert: {out_path}")
    if not preset_applied:
        print("ℹ eigener skinparam-Block im Input erkannt – Preset wurde nicht angewendet")

    embed = clean_for_embed(svg)
    if not args.no_clipboard:
        if copy_to_clipboard(embed):
            print("✓ Embed-Code (für Jupyter/Markdown) in die Zwischenablage kopiert")
        else:
            print("ℹ Zwischenablage nicht verfügbar – hier der Embed-Code:\n")
            print(embed)


if __name__ == "__main__":
    main()
