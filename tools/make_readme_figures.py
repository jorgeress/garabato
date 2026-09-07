"""
Render the figures the README uses, straight from the pipeline's own renderers.

Nothing here calls an image model or a GPU: the beats below are the two shot
types Garabato draws itself with PIL, so the figure always matches what the
pipeline actually produces.

Usage:
    python tools/make_readme_figures.py
"""

from __future__ import annotations
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image, ImageDraw, ImageFont

from config import find_fonts, FONT_PATHS_BOLD
from scripts._text_frame import render_text_frame
from scripts._diagram_frame import render_diagram_frame

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "img")

# The two beats shown in the figure, written exactly as they'd appear in a script.
BEATS = [
    (
        "(shot: text-frame | text: 'STATUS QUO BIAS')",
        lambda path: render_text_frame("large bold text 'STATUS QUO BIAS'", path),
    ),
    (
        "(shot: diagram | left: question-mark | right: lightbulb | "
        "arrow: right yellow | labels: 'QUESTION','DISCOVERY')",
        lambda path: render_diagram_frame({
            "shot": "diagram", "left": "question-mark", "right": "lightbulb",
            "arrow": "right yellow", "bg": "plain-white",
            "labels": "'QUESTION','DISCOVERY'",
        }, path),
    ),
]

WIDTH      = 1560
PAD        = 44
CODE_W     = 560
FRAME_W    = 800
FRAME_H    = FRAME_W * 9 // 16
ROW_GAP    = 34
INK        = (26, 26, 26)
MUTED      = (122, 122, 128)
CODE_BG    = (245, 245, 243)
BORDER     = (218, 218, 214)

_MONO = find_fonts("DejaVuSansMono", "LiberationMono-Regular", "JetBrainsMono-Regular",
                   "consola", "Menlo", "Courier New", "cour")


def _font(paths: list[str], size: int):
    for path in paths:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _wrap(draw, text: str, font, max_w: int) -> list[str]:
    lines, line = [], ""
    for word in text.split(" "):
        probe = f"{line} {word}".strip()
        if draw.textlength(probe, font=font) <= max_w or not line:
            line = probe
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)

    frames = []
    for i, (_beat, render) in enumerate(BEATS):
        path = os.path.join(OUT_DIR, f"_frame_{i}.png")
        render(path)
        frames.append(path)

    f_title = _font(FONT_PATHS_BOLD, 34)
    f_label = _font(FONT_PATHS_BOLD, 19)
    f_code  = _font(_MONO, 19)

    row_h  = FRAME_H + 30 + ROW_GAP
    height = PAD + 52 + 30 + row_h * len(BEATS) - ROW_GAP + PAD

    canvas = Image.new("RGB", (WIDTH, height), (255, 255, 255))
    draw   = ImageDraw.Draw(canvas)

    draw.text((PAD, PAD), "Del guion al fotograma", font=f_title, fill=INK)
    draw.text((PAD, PAD + 44),
              "Los campos son vocabulario cerrado, así que la misma línea da siempre la misma imagen.",
              font=_font(FONT_PATHS_BOLD, 18), fill=MUTED)

    y = PAD + 52 + 30
    for (beat, _render), frame_path in zip(BEATS, frames):
        # Left: the beat line as typed in the script, centred against the frame.
        code_lines = _wrap(draw, beat, f_code, CODE_W - 28)
        box_h  = 20 + len(code_lines) * 27
        group  = 26 + box_h                      # label + box
        code_y = y + 30 + (FRAME_H - group) // 2

        draw.text((PAD, code_y), "GUION", font=f_label, fill=MUTED)
        draw.rounded_rectangle([PAD, code_y + 26, PAD + CODE_W, code_y + 26 + box_h],
                               radius=8, fill=CODE_BG, outline=BORDER)
        for j, line in enumerate(code_lines):
            draw.text((PAD + 14, code_y + 36 + j * 27), line, font=f_code, fill=INK)

        # Middle: the arrow.
        ax = PAD + CODE_W + 30
        ay = y + 30 + FRAME_H // 2
        draw.line([(ax, ay), (ax + 44, ay)], fill=MUTED, width=4)
        draw.polygon([(ax + 56, ay), (ax + 40, ay - 11), (ax + 40, ay + 11)], fill=MUTED)

        # Right: the frame the pipeline rendered from that line.
        fx = PAD + CODE_W + 100
        draw.text((fx, y + 4), "FOTOGRAMA", font=f_label, fill=MUTED)
        frame = Image.open(frame_path).convert("RGB").resize((FRAME_W, FRAME_H), Image.LANCZOS)
        canvas.paste(frame, (fx, y + 30))
        draw.rectangle([fx, y + 30, fx + FRAME_W, y + 30 + FRAME_H], outline=BORDER, width=2)

        y += row_h

    out = os.path.join(OUT_DIR, "script-to-frame.png")
    canvas.save(out)
    for path in frames:
        os.remove(path)
    print(f"wrote {out}  ({canvas.width}x{canvas.height})")

    write_architecture()




# ─────────────────────────────────────────────────────────────────────────────
# Architecture diagram
#
# Deliberately not the linear step list -- the README already has that in ASCII.
# This draws the two things the linear view can't show: who owns the timeline,
# and where the decision about how each image gets made actually happens
# (generate_image_prompts.py, not generate_clips.py).
# ─────────────────────────────────────────────────────────────────────────────

W, H = 1360, 750

LIGHT = {
    "bg": "#ffffff",   "ink": "#1a1a1a", "muted": "#76767e",
    "panel": "#fbfbfa", "border": "#dededa", "fill": "#f4f4f1",
    "accent": "#c99700", "accent_fill": "#fdf6e0", "accent_ink": "#6b5100",
}
DARK = {
    "bg": "#0d1117",   "ink": "#e6edf3", "muted": "#8b949e",
    "panel": "#12161d", "border": "#2b313a", "fill": "#161b22",
    "accent": "#d9a520", "accent_fill": "#241d0c", "accent_ink": "#e8c86a",
}

SANS = ("ui-sans-serif,-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,"
        "'Helvetica Neue',Arial,sans-serif")
MONO = ("ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace")


def _esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Svg:
    """Minimal SVG builder: enough for boxes, labels and elbow connectors."""

    def __init__(self, pal: dict):
        self.pal = pal
        self.parts: list[str] = []

    def text(self, x, y, s, size=14, fill=None, weight="400", anchor="start", mono=False):
        family = MONO if mono else SANS
        self.parts.append(
            f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill or self.pal["ink"]}" '
            f'text-anchor="{anchor}">{_esc(s)}</text>'
        )

    def panel(self, x, y, w, h):
        self.parts.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" '
            f'fill="{self.pal["panel"]}" stroke="{self.pal["border"]}" stroke-width="1.5"/>'
        )

    def box(self, x, y, w, h, label, sub=None, mono=True, accent=False):
        pal  = self.pal
        fill = pal["accent_fill"] if accent else pal["fill"]
        edge = pal["accent"] if accent else pal["border"]
        self.parts.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" '
            f'stroke="{edge}" stroke-width="{2 if accent else 1.5}"/>'
        )
        cx = x + w / 2
        if sub:
            self.text(cx, y + h / 2 - 3, label, 14.5, pal["ink"], "600", "middle", mono)
            self.text(cx, y + h / 2 + 17, sub, 12.5, pal["muted"], "400", "middle", False)
        else:
            self.text(cx, y + h / 2 + 5, label, 14.5,
                      pal["accent_ink"] if accent else pal["ink"], "600", "middle", mono)
        return (x, y, w, h)

    def arrow(self, x1, y1, x2, y2, accent=False, label=None):
        """Straight or single-elbow connector, ending in a filled head."""
        pal   = self.pal
        color = pal["accent"] if accent else pal["muted"]
        if y1 == y2:
            path = f"M {x1} {y1} L {x2 - 9} {y2}"
        else:
            mid = x1 + (x2 - x1) / 2
            path = (f"M {x1} {y1} L {mid} {y1} Q {mid + 6} {y1} {mid + 6} "
                    f"{y1 + (6 if y2 > y1 else -6)} L {mid + 6} {y2} L {x2 - 9} {y2}")
        self.parts.append(
            f'<path d="{path}" fill="none" stroke="{color}" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round"/>'
        )
        self.parts.append(
            f'<path d="M {x2} {y2} L {x2 - 10} {y2 - 6} L {x2 - 10} {y2 + 6} Z" fill="{color}"/>'
        )
        if label:
            self.text((x1 + x2) / 2, y2 - 10, label, 12, color, "500", "middle")

    def render(self) -> str:
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
            f'width="{W}" height="{H}" role="img" '
            f'aria-label="Arquitectura de Garabato: el reloj unico y la bifurcacion de la imagen">'
            f'<rect width="{W}" height="{H}" fill="{self.pal["bg"]}"/>'
            + "".join(self.parts) + "</svg>"
        )


def render_architecture(pal: dict) -> str:
    s = Svg(pal)
    ink, muted = pal["ink"], pal["muted"]

    s.text(44, 50, "Lo que el flujo lineal no enseña", 25, ink, "700")
    s.text(44, 76, "Dos decisiones de arquitectura que no se ven en la lista de pasos.",
           14.5, muted)

    # ── Panel 1: the single timeline ─────────────────────────────────────────
    s.panel(44, 96, 1272, 228)
    s.text(72, 132, "1 · Una sola línea de tiempo", 16.5, ink, "700")
    s.text(72, 154, "generate_voice.py fija el reloj. Las imágenes y los subtítulos leen "
                    "el mismo, por eso no se separan del audio.", 13, muted)

    s.box(72,  186, 228, 52, "generate_voice.py")
    s.box(352, 176, 214, 60, "beat_timings.json", "start/end de cada beat", accent=True)
    s.box(352, 254, 214, 48, "narration.mp3")
    s.box(636, 166, 268, 56, "generate_image_prompts.py", "coloca cada imagen")
    s.box(636, 240, 268, 56, "generate_subtitles.py", "alinea cada palabra")

    s.arrow(300, 212, 352, 206)
    s.arrow(300, 212, 352, 278)
    s.arrow(566, 206, 636, 194, accent=True)
    s.arrow(566, 206, 636, 268, accent=True)

    # Annotation: the payoff, measured.
    s.parts.append(
        f'<rect x="964" y="196" width="284" height="76" rx="8" fill="none" '
        f'stroke="{pal["border"]}" stroke-width="1.5" stroke-dasharray="5 4"/>'
    )
    s.text(1106, 224, "MEDIDO", 11.5, muted, "700", "middle")
    s.text(1106, 250, "0,05 s de deriva en 83 beats", 14.5, ink, "600", "middle")

    # ── Panel 2: where the image decision happens ────────────────────────────
    s.panel(44, 350, 1272, 356)
    s.text(72, 386, "2 · Dónde se decide de dónde sale cada imagen", 16.5, ink, "700")
    s.text(72, 408, "La bifurcación ocurre al construir los prompts, no al generar los "
                    "clips. La elige CLIP_SOURCE.", 13, muted)

    s.box(72,  498, 232, 56, "generate_image_prompts.py", "línea 750")
    s.box(336, 502, 140, 48, "CLIP_SOURCE")
    s.arrow(304, 526, 336, 526)

    # Hosted branch: the model illustrates every beat type.
    s.box(520, 440, 176, 46, "gemini · manual")
    s.box(728, 440, 232, 46, "build_gemini_prompt()")
    s.box(992, 430, 256, 66, "prompt en lenguaje natural", "rótulos y diagramas incluidos")
    s.arrow(476, 526, 520, 463)
    s.arrow(696, 463, 728, 463)
    s.arrow(960, 463, 992, 463)

    # Local branch: the closed catalog and the PIL renderers.
    s.box(520, 568, 176, 46, "comfyui")
    s.box(728, 524, 232, 46, "beat_type: scene")
    s.box(992, 514, 256, 66, "prompt de catálogo", "_catalog.py: campo → fragmento")
    s.box(728, 622, 232, 46, "text-frame · diagram")
    s.box(992, 612, 256, 66, "prompt vacío", "lo dibuja PIL, sin modelo")
    s.arrow(476, 526, 520, 591)
    s.arrow(696, 591, 728, 547)
    s.arrow(696, 591, 728, 645)
    s.arrow(960, 547, 992, 547)
    s.arrow(960, 645, 992, 645)

    return s.render()


def write_architecture() -> None:
    for name, pal in (("light", LIGHT), ("dark", DARK)):
        path = os.path.join(OUT_DIR, f"architecture-{name}.svg")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(render_architecture(pal))
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
