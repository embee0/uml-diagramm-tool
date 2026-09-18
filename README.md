# kd.py – Klassendiagramme aus PlantUML

Ein einzelnes, abhängigkeitsfreies Python-Skript, das aus PlantUML-Text ein Klassen- oder Objektdiagramm als SVG erzeugt – mit einem fertigen Design-Preset, das sich bei Bedarf komplett überschreiben lässt.

## Voraussetzungen

- [uv](https://docs.astral.sh/uv/) (führt das Skript ohne Installationsschritt aus)
- [PlantUML](https://plantuml.com/download) lokal installiert, inklusive Java. Auf macOS z. B.:
  ```bash
  brew install plantuml
  ```

## Installation als Kommandozeilenbefehl (optional)

Wer `kd` direkt aufrufen möchte, statt jedes Mal `uv run kd.py` zu schreiben:

```bash
chmod +x kd.py
ln -s "$(pwd)/kd.py" ~/.local/bin/kd   # ~/.local/bin muss im PATH liegen
```

Danach funktioniert `kd diagramm.puml` von überall aus.

## Verwendung

```bash
# Aus einer .puml-Datei
uv run kd.py diagramm.puml

# Direkt als Text (mehrzeilig, in Anführungszeichen)
uv run kd.py "class Foo {
  +bar: Text
}"

# Über stdin
cat diagramm.puml | uv run kd.py -

# Anderes Design-Preset
uv run kd.py diagramm.puml --theme dark

# Ziel-Datei explizit festlegen
uv run kd.py diagramm.puml -o ausgabe.svg

# Ohne Zwischenablage (z. B. auf einem Server ohne Clipboard-Zugriff)
uv run kd.py diagramm.puml --no-clipboard
```

Nach dem Rendern:
- landet die vollständige SVG-Datei neben dem Input (bzw. als `diagramm.svg`, wenn kein Dateiname bekannt ist),
- wird zusätzlich eine leicht aufgeräumte Embed-Version (ohne PlantUML-Metadaten) in die Zwischenablage kopiert – zum direkten Einfügen in eine Markdown-Zelle (z. B. Jupyter Notebook) oder eine Webseite.

## Design anpassen

Drei eingebaute Presets: `tgi` (Standard, warmer Skript-Stil), `dark`, `minimal`.

Wer ein komplett eigenes Design will, schreibt einfach selbst einen `skinparam`-Block in den PlantUML-Input – das Skript erkennt das automatisch und wendet dann **kein** Preset an:

```plantuml
@startuml
skinparam {
  ClassBackgroundColor #E8F0FE
  ClassBorderColor #1A5FB4
}
class Beispiel {
  +eigenerStil: Boolean
}
@enduml
```

## Beispiele

In `examples/` liegen sechs lauffähige Beispiele – die ersten vier stammen direkt aus dem TGI-12-OOP-Skript:

- `klassendiagramm-kaempfer.puml` – einfaches Klassendiagramm
- `objektdiagramm-karl.puml` – dazugehöriges Objektdiagramm
- `vererbung-charakter.puml` – Vererbung (`Charakter` → `Kämpfer`/`Magier`/`Schurke`)
- `assoziation-charakter-waffe.puml` – Assoziation mit Rollenname (`Charakter -> Waffe : trägt`)
- `reflexive-assoziation-knoten.puml` – **reflexive Assoziation**: ein `Knoten` (z. B. für eine verkettete Liste), der über `naechster` auf einen Knoten *derselben* Klasse zeigt
- `eigenes-design.puml` – Beispiel für einen komplett selbst geschriebenen `skinparam`-Block

## Warum lokal statt Web-Dienst?

Es gibt Web-Dienste wie [Kroki.io](https://kroki.io), die PlantUML ohne lokale Installation rendern. Dieses Skript setzt bewusst auf die lokale `plantuml`-Installation, weil das Ergebnis dadurch exakt reproduzierbar bleibt und kein Diagrammtext an einen externen Dienst geschickt wird.
