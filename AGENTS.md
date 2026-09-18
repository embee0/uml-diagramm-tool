# Anleitung für KI-Agenten: kd.py

`kd.py` erzeugt aus PlantUML-Text ein Klassen- oder Objektdiagramm als SVG, mit einem fertigen, konsistenten Design-Preset. Nutze es immer, wenn ein UML-Klassen- oder Objektdiagramm gebraucht wird – nicht selbst ein SVG von Hand bauen.

## Aufruf

```bash
uv run /pfad/zu/kd.py <input> [-o ausgabe.svg] [--theme tgi|dark|minimal] [--no-clipboard]
```

Ist `kd` als Symlink im PATH eingerichtet, reicht `kd <input> ...`.

`<input>` kann sein:
- Pfad zu einer `.puml`-Datei
- PlantUML-Text direkt als Argument (mehrzeilig, in Anführungszeichen)
- `-` für stdin

**In automatisierten/nicht-interaktiven Kontexten immer `--no-clipboard` setzen** – sonst versucht das Skript, die Zwischenablage zu belegen, was in einer Agenten-Umgebung meist unerwünscht oder wirkungslos ist.

## Vorbedingung prüfen

`plantuml` (inkl. Java) muss lokal installiert sein. Falls nicht: das Skript bricht mit einer klaren Fehlermeldung samt Installationshinweis ab (`brew install plantuml` auf macOS). Nicht versuchen, das selbst zu umgehen oder ein anderes Rendering-Verfahren zu improvisieren – stattdessen die Fehlermeldung an den Nutzer weiterreichen.

## Design

- Standard-Preset ist `tgi` (heller, warmer Stil). Alternativen: `--theme dark`, `--theme minimal`.
- Enthält der PlantUML-Input bereits einen eigenen `skinparam`-Block, wird **kein** Preset angewendet – der eigene Stil hat automatisch Vorrang. So kann das Design bei Bedarf komplett frei bestimmt werden, ohne einen Parameter zu setzen.

## Output

- Die vollständige SVG-Datei wird gespeichert (Pfad wird ausgegeben) – Standardort neben dem Input, sonst `diagramm.svg`.
- Zusätzlich wird eine aufgeräumte, embed-taugliche SVG-Version (ohne PlantUML-Metadaten) in die Zwischenablage kopiert – nützlich zum direkten Einfügen in Markdown/Jupyter, aber in Skripten mit `--no-clipboard` unterdrücken.

## Beispiele

Lauffähige `.puml`-Beispiele liegen in `examples/`, darunter auch eines mit **reflexiver Assoziation** (`Knoten -> Knoten : naechster`) als Vorlage für Selbstbezüge (z. B. verkettete Listen, Bäume).
