# Salis template examples

Static HTML previews of Django templates under `apps/api/templates`, filled with sample data for browser review.

## Open

Open [`index.html`](index.html) in a browser (double-click or):

```bash
open apps/api/templates/examples/index.html
```

Logo assets live in [`assets/salis-logo.png`](assets/salis-logo.png).

## Regenerating

From the repo root (Django required):

```bash
python3 apps/api/templates/examples/render_examples.py
```

These files are **previews only** — production emails still render from the live templates with real context.
