#!/usr/bin/env python3
"""
SoD2 Diary v2 — annotated mockup generator.

Emits 21 SVG mockups under design/mockups/ for the seven canonical
screens at three breakpoints (mobile / tablet / desktop), per
PHA-348. Every callout cites a component § from
design/components.md and one or more tokens from design/tokens.css.

Re-run after touching the catalogues (tokens or components) and
commit the regenerated SVGs alongside the source change so the
mockups never drift from spec.

    cd design/mockups && python3 _render.py
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from textwrap import dedent
from typing import Callable, List

# ----------------------------------------------------------------
# Tokens (mirrored from design/tokens.css; SVG can't read CSS vars)
# ----------------------------------------------------------------
PAPER          = "#F1E4C8"
PAPER_STAINED  = "#C9B388"
LEATHER        = "#3B2A1A"
LEATHER_SHADOW = "#1B120A"
INK_BLUE       = "#1F2A4A"
INK_BROWN      = "#2A1F12"
INK_RED        = "#7E1E1E"
AMBER          = "#D4A24C"

FONT_TYPE = "'Special Elite', 'Courier New', Courier, monospace"
FONT_MONO = "'IBM Plex Mono', ui-monospace, Menlo, Consolas, monospace"
FONT_HAND = "'Caveat', 'Patrick Hand', 'Bradley Hand', cursive"

# Breakpoint device widths (per Plan §5 responsive strategy)
MOBILE_W,  MOBILE_H  = 360,  760
TABLET_W,  TABLET_H  = 768,  1024
DESKTOP_W, DESKTOP_H = 1440, 900

# Annotation rail to the right of the device, holding numbered callouts
RAIL_MOBILE  = 280
RAIL_TABLET  = 320
RAIL_DESKTOP = 360


@dataclass
class Annotation:
    """One numbered callout pointing into the device with a leader line."""
    n: int
    target: tuple[float, float]   # (x, y) inside the device frame
    title: str                    # e.g. "§1 Input slot · DATE"
    tokens: str                   # e.g. "--ink-brown · --font-typewriter"
    fallback: str                 # one-line clarity-win note


@dataclass
class Mockup:
    screen: str
    breakpoint: str               # "mobile" | "tablet" | "desktop"
    title: str
    body: Callable[["Canvas"], str]
    notes: List[Annotation] = field(default_factory=list)


# ----------------------------------------------------------------
# Canvas helpers
# ----------------------------------------------------------------
@dataclass
class Canvas:
    w: int            # full SVG width incl. annotation rail
    h: int
    device_w: int     # device frame width (inside the leather)
    device_h: int
    rail_x: int       # x-coord where the annotation rail starts
    inset: int = 14   # leather frame thickness around the page

    @property
    def page_x(self) -> int:
        return self.inset

    @property
    def page_y(self) -> int:
        return self.inset

    @property
    def page_w(self) -> int:
        return self.device_w - 2 * self.inset

    @property
    def page_h(self) -> int:
        return self.device_h - 2 * self.inset


def canvas_for(breakpoint: str) -> Canvas:
    if breakpoint == "mobile":
        return Canvas(MOBILE_W + RAIL_MOBILE, MOBILE_H, MOBILE_W, MOBILE_H, MOBILE_W, inset=10)
    if breakpoint == "tablet":
        return Canvas(TABLET_W + RAIL_TABLET, TABLET_H, TABLET_W, TABLET_H, TABLET_W, inset=14)
    return Canvas(DESKTOP_W + RAIL_DESKTOP, DESKTOP_H, DESKTOP_W, DESKTOP_H, DESKTOP_W, inset=18)


# ----------------------------------------------------------------
# Reusable SVG fragments
# ----------------------------------------------------------------
def defs() -> str:
    return dedent(f"""\
    <defs>
      <pattern id="paperGrain" x="0" y="0" width="60" height="60" patternUnits="userSpaceOnUse">
        <rect width="60" height="60" fill="{PAPER}"/>
        <circle cx="11" cy="14" r="0.6" fill="{PAPER_STAINED}" opacity="0.5"/>
        <circle cx="42" cy="22" r="0.5" fill="{PAPER_STAINED}" opacity="0.4"/>
        <circle cx="29" cy="48" r="0.7" fill="{PAPER_STAINED}" opacity="0.45"/>
        <circle cx="55" cy="51" r="0.4" fill="{PAPER_STAINED}" opacity="0.3"/>
      </pattern>
      <pattern id="leatherGrain" x="0" y="0" width="80" height="80" patternUnits="userSpaceOnUse">
        <rect width="80" height="80" fill="{LEATHER}"/>
        <path d="M0 13 q40 -3 80 0 M0 41 q40 4 80 0 M0 67 q40 -4 80 0" stroke="{LEATHER_SHADOW}"
              stroke-width="0.6" fill="none" opacity="0.5"/>
      </pattern>
      <radialGradient id="lamp" cx="18%" cy="12%" r="65%">
        <stop offset="0%" stop-color="{AMBER}" stop-opacity="0.18"/>
        <stop offset="55%" stop-color="{AMBER}" stop-opacity="0.06"/>
        <stop offset="100%" stop-color="{AMBER}" stop-opacity="0"/>
      </radialGradient>
      <filter id="hand" x="-2%" y="-50%" width="104%" height="200%">
        <feTurbulence type="fractalNoise" baseFrequency="0.7" numOctaves="2" seed="3"/>
        <feDisplacementMap in="SourceGraphic" scale="0.6"/>
      </filter>
      <symbol id="paperclip" viewBox="0 0 40 60">
        <path d="M20 4 q-9 0 -9 9 v36 q0 9 9 9 t9 -9 v-30 q0 -5 -5 -5 t-5 5 v22"
              fill="none" stroke="{AMBER}" stroke-width="2.2" stroke-linecap="round"/>
      </symbol>
      <symbol id="touchHint" viewBox="0 0 44 44">
        <rect x="0" y="0" width="44" height="44" fill="none" stroke="{AMBER}"
              stroke-width="1" stroke-dasharray="3 3" opacity="0.6"/>
      </symbol>
    </defs>
    """)


def book_chrome(c: Canvas) -> str:
    """Leather frame + paper page + amber lamp wash."""
    return dedent(f"""\
    <!-- leather book chrome -->
    <rect x="0" y="0" width="{c.device_w}" height="{c.device_h}" fill="url(#leatherGrain)"/>
    <rect x="0" y="0" width="{c.device_w}" height="{c.device_h}" fill="{LEATHER}" opacity="0.15"/>
    <!-- spine inset shadow -->
    <rect x="0" y="0" width="{c.device_w}" height="3" fill="{LEATHER_SHADOW}"/>
    <rect x="0" y="{c.device_h - 3}" width="{c.device_w}" height="3" fill="{LEATHER_SHADOW}"/>
    <rect x="0" y="0" width="3" height="{c.device_h}" fill="{LEATHER_SHADOW}"/>
    <rect x="{c.device_w - 3}" y="0" width="3" height="{c.device_h}" fill="{LEATHER_SHADOW}"/>
    <!-- paper page -->
    <rect x="{c.page_x}" y="{c.page_y}" width="{c.page_w}" height="{c.page_h}"
          fill="url(#paperGrain)" stroke="{PAPER_STAINED}" stroke-width="0.5"/>
    <!-- amber lamp wash from top-left -->
    <rect x="{c.page_x}" y="{c.page_y}" width="{c.page_w}" height="{c.page_h}" fill="url(#lamp)"/>
    """)


def annotation_rail(c: Canvas, notes: List[Annotation]) -> str:
    """Right-side rail with numbered callouts and leader lines into the device."""
    out = [
        f'<rect x="{c.rail_x}" y="0" width="{c.w - c.rail_x}" height="{c.h}" fill="#FAF6EC"/>',
        f'<line x1="{c.rail_x}" y1="0" x2="{c.rail_x}" y2="{c.h}" stroke="{PAPER_STAINED}" stroke-width="1"/>',
        f'<text x="{c.rail_x + 16}" y="28" font-family="{FONT_TYPE}" font-size="11" '
        f'fill="{INK_BROWN}" letter-spacing="2">ANNOTATIONS</text>',
        f'<line x1="{c.rail_x + 16}" y1="36" x2="{c.w - 16}" y2="36" stroke="{INK_BROWN}" '
        f'stroke-width="0.6" opacity="0.5"/>',
    ]
    rail_top = 56
    rail_left = c.rail_x + 16
    rail_right = c.w - 16
    block_h = max(72, (c.h - rail_top - 24) // max(1, len(notes)))
    for idx, ann in enumerate(notes):
        by = rail_top + idx * block_h
        # numbered marker on the device pointing at the target
        tx, ty = ann.target
        out.append(
            f'<line x1="{tx}" y1="{ty}" x2="{c.rail_x}" y2="{by + 12}" '
            f'stroke="{INK_RED}" stroke-width="0.6" stroke-dasharray="2 2" opacity="0.7"/>'
        )
        out.append(
            f'<circle cx="{tx}" cy="{ty}" r="9" fill="{PAPER}" stroke="{INK_RED}" stroke-width="1"/>'
        )
        out.append(
            f'<text x="{tx}" y="{ty + 4}" text-anchor="middle" font-family="{FONT_TYPE}" '
            f'font-size="10" fill="{INK_RED}">{ann.n}</text>'
        )
        # callout in the rail
        out.append(
            f'<circle cx="{rail_left + 8}" cy="{by + 12}" r="9" fill="{PAPER}" '
            f'stroke="{INK_RED}" stroke-width="1"/>'
        )
        out.append(
            f'<text x="{rail_left + 8}" y="{by + 16}" text-anchor="middle" '
            f'font-family="{FONT_TYPE}" font-size="10" fill="{INK_RED}">{ann.n}</text>'
        )
        out.append(
            f'<text x="{rail_left + 24}" y="{by + 16}" font-family="{FONT_TYPE}" '
            f'font-size="11" fill="{INK_BROWN}" letter-spacing="1">{xml_escape(ann.title)}</text>'
        )
        # tokens line
        out.append(
            f'<text x="{rail_left + 24}" y="{by + 32}" font-family="{FONT_MONO}" '
            f'font-size="9.5" fill="{INK_BLUE}">{xml_escape(ann.tokens)}</text>'
        )
        # fallback line(s) — wrap roughly to rail width
        wrapped = wrap_text(ann.fallback, max_chars=int((rail_right - rail_left - 24) / 5.6))
        for li, line in enumerate(wrapped[:3]):
            out.append(
                f'<text x="{rail_left + 24}" y="{by + 46 + li * 12}" font-family="{FONT_MONO}" '
                f'font-size="9" fill="{INK_BROWN}" opacity="0.85">{xml_escape(line)}</text>'
            )
    return "\n".join(out)


def wrap_text(s: str, max_chars: int) -> List[str]:
    words = s.split()
    lines, cur = [], ""
    for w in words:
        candidate = (cur + " " + w).strip()
        if len(candidate) > max_chars and cur:
            lines.append(cur)
            cur = w
        else:
            cur = candidate
    if cur:
        lines.append(cur)
    return lines


def xml_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header_meta(c: Canvas, title: str, subtitle: str) -> str:
    return dedent(f"""\
    <!-- mockup metadata header (rendered at top of annotation rail in PNGs) -->
    <text x="{c.rail_x + 16}" y="{c.h - 28}" font-family="{FONT_TYPE}" font-size="11"
          fill="{INK_BROWN}" letter-spacing="2">{xml_escape(title)}</text>
    <text x="{c.rail_x + 16}" y="{c.h - 14}" font-family="{FONT_MONO}" font-size="9"
          fill="{INK_BROWN}" opacity="0.7">{xml_escape(subtitle)}</text>
    """)


# ----------------------------------------------------------------
# Common page artifacts (parts that repeat between screens)
# ----------------------------------------------------------------
def page_title(c: Canvas, x: int, y: int, day: str, date: str, community: str,
               size_lg: int = 22, size_sm: int = 11) -> str:
    return dedent(f"""\
    <text x="{x}" y="{y}" font-family="{FONT_TYPE}" font-size="{size_sm}"
          fill="{INK_BROWN}" letter-spacing="2">DAY · {xml_escape(date)}</text>
    <text x="{x}" y="{y + 28}" font-family="{FONT_HAND}" font-size="{size_lg}"
          fill="{INK_BLUE}">{xml_escape(day)}</text>
    <text x="{x}" y="{y + 50}" font-family="{FONT_MONO}" font-size="{size_sm}"
          fill="{INK_BROWN}" opacity="0.8">community: {xml_escape(community)}</text>
    """)


def input_slot(x: int, y: int, w: int, h: int, label: str, value: str = "",
               width_label: int = 110) -> str:
    return dedent(f"""\
    <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none"
          stroke="{INK_BROWN}" stroke-width="1.4" rx="3"/>
    <text x="{x + 12}" y="{y + h/2 + 4}" font-family="{FONT_MONO}" font-size="11"
          fill="{INK_BROWN}" letter-spacing="1">{xml_escape(label)}</text>
    <text x="{x + width_label + 12}" y="{y + h/2 + 5}" font-family="{FONT_HAND}"
          font-size="{int(h*0.45)}" fill="{INK_BLUE}">{xml_escape(value)}</text>
    """)


def stamp_button(x: int, y: int, w: int, h: int, label: str,
                 fill: str = INK_BROWN, text_color: str = PAPER, rotate: float = -1.2) -> str:
    cx, cy = x + w / 2, y + h / 2
    return dedent(f"""\
    <g transform="rotate({rotate} {cx} {cy})">
      <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" rx="2"
            opacity="0.95"/>
      <text x="{cx}" y="{cy + 5}" text-anchor="middle" font-family="{FONT_TYPE}"
            font-size="14" fill="{text_color}" letter-spacing="2">{xml_escape(label)}</text>
    </g>
    """)


def index_card(x: int, y: int, w: int, h: int, name: str, age: str,
               traits: str, skills: str, morale: str, joined: str,
               rotate: float = -0.6, stamp: str | None = None) -> str:
    cx, cy = x + w / 2, y + h / 2
    parts = [f'<g transform="rotate({rotate} {cx} {cy})">']
    parts.append(
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{PAPER}" '
        f'stroke="{PAPER_STAINED}" stroke-width="0.6" rx="4"/>'
    )
    parts.append(
        f'<line x1="{x + 14}" y1="{y + 30}" x2="{x + w - 14}" y2="{y + 30}" '
        f'stroke="{PAPER_STAINED}" stroke-width="0.6"/>'
    )
    parts.append(
        f'<text x="{x + 14}" y="{y + 24}" font-family="{FONT_HAND}" font-size="20" '
        f'fill="{INK_BLUE}">{xml_escape(name)}, {xml_escape(age)}</text>'
    )
    parts.append(
        f'<text x="{x + w - 14}" y="{y + 24}" text-anchor="end" font-family="{FONT_MONO}" '
        f'font-size="10" fill="{INK_BROWN}">{xml_escape(joined)}</text>'
    )
    parts.append(
        f'<text x="{x + 14}" y="{y + 50}" font-family="{FONT_MONO}" font-size="11" '
        f'fill="{INK_BROWN}">TRAITS  {xml_escape(traits)}</text>'
    )
    parts.append(
        f'<text x="{x + 14}" y="{y + 68}" font-family="{FONT_MONO}" font-size="11" '
        f'fill="{INK_BROWN}">SKILLS  {xml_escape(skills)}</text>'
    )
    parts.append(
        f'<text x="{x + 14}" y="{y + 86}" font-family="{FONT_MONO}" font-size="11" '
        f'fill="{INK_BROWN}">MORALE  {xml_escape(morale)}</text>'
    )
    if stamp:
        # KIA / EXILED / LEGACY stamp overlay
        sx, sy = x + w - 80, y + h - 28
        if stamp == "KIA":
            parts.append(
                f'<g transform="rotate(-8 {sx + 35} {sy})">'
                f'<rect x="{sx}" y="{sy - 18}" width="70" height="36" fill="none" '
                f'stroke="{INK_RED}" stroke-width="2"/>'
                f'<text x="{sx + 35}" y="{sy + 6}" text-anchor="middle" '
                f'font-family="{FONT_TYPE}" font-size="18" fill="{INK_RED}" '
                f'letter-spacing="3">KIA</text></g>'
            )
        elif stamp == "EXILED":
            parts.append(
                f'<g transform="rotate(4 {sx + 35} {sy})" opacity="0.78">'
                f'<rect x="{sx - 6}" y="{sy - 16}" width="84" height="32" fill="none" '
                f'stroke="{INK_BROWN}" stroke-width="2"/>'
                f'<text x="{sx + 36}" y="{sy + 4}" text-anchor="middle" '
                f'font-family="{FONT_TYPE}" font-size="14" fill="{INK_BROWN}" '
                f'letter-spacing="2">EXILED</text></g>'
            )
        elif stamp == "LEGACY":
            parts.append(
                f'<g transform="rotate(-2 {sx + 35} {sy})">'
                f'<circle cx="{sx + 35}" cy="{sy}" r="22" fill="{AMBER}" '
                f'stroke="{INK_BROWN}" stroke-width="1.5"/>'
                f'<text x="{sx + 35}" y="{sy + 4}" text-anchor="middle" '
                f'font-family="{FONT_TYPE}" font-size="10" fill="{INK_BROWN}" '
                f'letter-spacing="2">LEGACY</text></g>'
            )
    parts.append("</g>")
    # paperclip clipping the card
    parts.append(
        f'<use href="#paperclip" x="{x + w/2 - 14}" y="{y - 14}" width="28" height="44"/>'
    )
    return "\n".join(parts)


def tab_strip_right(c: Canvas, active: str, x: int, y_start: int, count: int = 5) -> str:
    """Right-edge tabs: PEOPLE / PLACES / RESOURCES / EVENTS / DISPATCH (per moodboard)."""
    labels = ["PEOPLE", "PLACES", "RES", "EVENTS", "DISP"]
    if count == 4:
        labels = ["PEOPLE", "RES", "EVENTS", "DISP"]
    parts = []
    tab_h = 64
    for i, lbl in enumerate(labels[:count]):
        ty = y_start + i * (tab_h + 8)
        is_active = lbl.lower().startswith(active.lower())
        fill = PAPER if is_active else PAPER_STAINED
        offset = -4 if is_active else 0
        parts.append(
            f'<path d="M{x + offset} {ty} h{52} q12 0 12 12 v{tab_h - 24} '
            f'q0 12 -12 12 h-{52} z" fill="{fill}" stroke="{LEATHER}" stroke-width="0.6"/>'
        )
        parts.append(
            f'<text x="{x + offset + 8}" y="{ty + tab_h/2 + 4}" font-family="{FONT_TYPE}" '
            f'font-size="10" fill="{INK_BROWN}" letter-spacing="1.5">{lbl}</text>'
        )
        if is_active:
            parts.append(
                f'<line x1="{x + offset}" y1="{ty + tab_h - 1}" x2="{x + offset + 60}" '
                f'y2="{ty + tab_h - 1}" stroke="{AMBER}" stroke-width="2"/>'
            )
    return "\n".join(parts)


def ribbon_nav(c: Canvas, active: str) -> str:
    """Bottom-edge mobile ribbon (§7)."""
    h = 52
    y = c.device_h - h - c.inset
    items = ["PEOPLE", "RES", "EVENTS", "DISP", "⚙"]
    parts = [
        f'<rect x="{c.page_x}" y="{y}" width="{c.page_w}" height="{h}" fill="{LEATHER}"/>',
        f'<rect x="{c.page_x}" y="{y}" width="{c.page_w}" height="2" fill="{AMBER}" opacity="0.6"/>',
    ]
    item_w = c.page_w / len(items)
    for i, lbl in enumerate(items):
        ix = c.page_x + i * item_w + item_w / 2
        is_active = lbl.lower().startswith(active.lower())
        parts.append(
            f'<text x="{ix}" y="{y + 32}" text-anchor="middle" font-family="{FONT_TYPE}" '
            f'font-size="11" fill="{PAPER}" letter-spacing="1.5">{lbl}</text>'
        )
        if is_active:
            parts.append(
                f'<rect x="{ix - 28}" y="{y + h - 4}" width="56" height="4" fill="{AMBER}"/>'
            )
    return "\n".join(parts)


def section_clip(c: Canvas, x: int, y: int, label: str, sub: str = "") -> str:
    """Paperclip-grouped section header (§6)."""
    return dedent(f"""\
    <use href="#paperclip" x="{x}" y="{y - 8}" width="22" height="36"/>
    <text x="{x + 32}" y="{y + 14}" font-family="{FONT_TYPE}" font-size="13"
          fill="{INK_BROWN}" letter-spacing="1.5">{xml_escape(label)}</text>
    <text x="{x + 32}" y="{y + 28}" font-family="{FONT_MONO}" font-size="10"
          fill="{INK_BROWN}" opacity="0.7">{xml_escape(sub)}</text>
    """)


def touch_proof(c: Canvas, points: List[tuple[int, int]]) -> str:
    """Optional 44×44 dotted hit-box overlays for mobile/tablet proof."""
    out = []
    for (px, py) in points:
        out.append(f'<use href="#touchHint" x="{px - 22}" y="{py - 22}" width="44" height="44"/>')
    return "\n".join(out)


# ----------------------------------------------------------------
# Per-screen body builders
# ----------------------------------------------------------------
def todays_page(c: Canvas) -> str:
    px, py = c.page_x + 18, c.page_y + 24
    parts = [page_title(c, px, py, "Tuesday — clear", "14", "Trumbull Pt.")]
    # form area depends on breakpoint
    if c.device_w == MOBILE_W:
        slots = [
            ("DATE", "Tue · D14"),
            ("WEATHER", "clear"),
            ("MORALE", "high"),
            ("FOOD", "5"),
            ("MEDS", "2"),
            ("AMMO", "11"),
            ("FUEL", "3"),
            ("MATERIALS", "8"),
            ("PLAGUE HEARTS", "2"),
        ]
        slot_y = py + 70
        slot_h = 44
        for label, val in slots:
            parts.append(input_slot(px, slot_y, c.page_w - 36, slot_h, label, val, width_label=120))
            slot_y += slot_h + 8
        # events note (multiline)
        parts.append(input_slot(px, slot_y, c.page_w - 36, 72, "EVENTS", ""))
        parts.append(
            f'<text x="{px + 12}" y="{slot_y + 36}" font-family="{FONT_HAND}" font-size="16" '
            f'fill="{INK_BLUE}">Maya killed a feral. Ed</text>'
        )
        parts.append(
            f'<text x="{px + 12}" y="{slot_y + 56}" font-family="{FONT_HAND}" font-size="16" '
            f'fill="{INK_BLUE}">scavenged the gas station.</text>'
        )
        slot_y += 80
        # ribbon nav
        parts.append(ribbon_nav(c, "PEOPLE"))  # Today is shown via Today screen, ribbon shows section
        # transmit wax-seal
        parts.append(wax_seal(c.device_w - 200, c.device_h - 180, label="TRANSMIT"))
    elif c.device_w == TABLET_W:
        # Two-column form: vitals on left, resources on right
        col_w = (c.page_w - 60) // 2
        left_x = px
        right_x = px + col_w + 30
        parts.append(section_clip(c, left_x, py + 76, "VITALS", "morale · weather"))
        slots_left = [("DATE", "Tue · D14"), ("WEATHER", "clear"), ("MORALE", "high")]
        sy = py + 116
        for label, val in slots_left:
            parts.append(input_slot(left_x, sy, col_w, 44, label, val))
            sy += 52
        parts.append(section_clip(c, right_x, py + 76, "RESOURCES", "food · meds · ammo · fuel · mats"))
        slots_right = [("FOOD", "5"), ("MEDS", "2"), ("AMMO", "11"), ("FUEL", "3"), ("MATERIALS", "8")]
        sy = py + 116
        for label, val in slots_right:
            parts.append(input_slot(right_x, sy, col_w, 44, label, val))
            sy += 52
        # plague hearts (full width, ink-red label)
        ph_y = py + 116 + 5 * 52 + 8
        parts.append(
            f'<rect x="{px}" y="{ph_y}" width="{c.page_w - 36}" height="44" fill="none" '
            f'stroke="{INK_RED}" stroke-width="1.4" rx="3"/>'
        )
        parts.append(
            f'<text x="{px + 12}" y="{ph_y + 28}" font-family="{FONT_MONO}" font-size="12" '
            f'fill="{INK_RED}" letter-spacing="1">PLAGUE HEARTS</text>'
        )
        parts.append(
            f'<text x="{px + 130}" y="{ph_y + 30}" font-family="{FONT_HAND}" font-size="22" '
            f'fill="{INK_RED}">2 — west sector</text>'
        )
        # events note multi-line
        ev_y = ph_y + 60
        parts.append(input_slot(px, ev_y, c.page_w - 36, 96, "EVENTS", ""))
        parts.append(
            f'<text x="{px + 12}" y="{ev_y + 38}" font-family="{FONT_HAND}" font-size="18" '
            f'fill="{INK_BLUE}">Maya killed a feral on the highway.</text>'
        )
        parts.append(
            f'<text x="{px + 12}" y="{ev_y + 60}" font-family="{FONT_HAND}" font-size="18" '
            f'fill="{INK_BLUE}">Ed scavenged the gas station — found</text>'
        )
        parts.append(
            f'<text x="{px + 12}" y="{ev_y + 80}" font-family="{FONT_HAND}" font-size="18" '
            f'fill="{INK_BLUE}">2 medkits, gave one to Marcus.</text>'
        )
        parts.append(tab_strip_right(c, "PEOPLE", c.device_w - c.inset - 60, py + 70))
        parts.append(wax_seal(c.device_w - 240, c.device_h - 160, label="TRANSMIT"))
    else:  # desktop — two-page spread
        spine_x = c.page_x + c.page_w // 2
        # spine fold
        parts.append(
            f'<rect x="{spine_x - 4}" y="{c.page_y}" width="8" height="{c.page_h}" '
            f'fill="{LEATHER_SHADOW}" opacity="0.6"/>'
        )
        # left page: vitals + plague hearts
        left_inner = px
        parts.append(section_clip(c, left_inner, py + 80, "VITALS", "weather · morale"))
        sy = py + 116
        for label, val in [("DATE", "Tue · D14"), ("WEATHER", "clear · 62°F"), ("MORALE", "high")]:
            parts.append(input_slot(left_inner, sy, spine_x - left_inner - 32, 44, label, val))
            sy += 56
        parts.append(section_clip(c, left_inner, sy + 12, "PLAGUE HEARTS", "alert color: --ink-red"))
        sy += 50
        parts.append(
            f'<rect x="{left_inner}" y="{sy}" width="{spine_x - left_inner - 32}" '
            f'height="56" fill="none" stroke="{INK_RED}" stroke-width="1.6" rx="3"/>'
        )
        parts.append(
            f'<text x="{left_inner + 14}" y="{sy + 32}" font-family="{FONT_MONO}" font-size="12" '
            f'fill="{INK_RED}" letter-spacing="1">HEARTS</text>'
        )
        parts.append(
            f'<text x="{left_inner + 100}" y="{sy + 36}" font-family="{FONT_HAND}" font-size="26" '
            f'fill="{INK_RED}">2 — west sector, near the mall</text>'
        )
        # right page: resources + events
        right_inner = spine_x + 20
        right_w = c.device_w - c.inset - right_inner
        parts.append(section_clip(c, right_inner, py + 80, "RESOURCES", "food · meds · ammo · fuel · materials"))
        sy = py + 116
        col_w = (right_w - 24) // 2
        cols = [
            ("FOOD", "5"),    ("MEDS", "2"),
            ("AMMO", "11"),   ("FUEL", "3"),
            ("MATERIALS", "8"), ("PARTS", "1"),
        ]
        for i, (label, val) in enumerate(cols):
            cx_ = right_inner + (i % 2) * (col_w + 24)
            cy_ = sy + (i // 2) * 56
            parts.append(input_slot(cx_, cy_, col_w, 44, label, val))
        sy = sy + (len(cols) // 2) * 56 + 12
        parts.append(section_clip(c, right_inner, sy, "EVENTS", "freeform notes"))
        sy += 36
        parts.append(input_slot(right_inner, sy, right_w - 28, 200, "", ""))
        for i, line in enumerate([
            "Maya killed a feral on the highway near the rest-stop.",
            "Ed scavenged the gas station — 2 medkits, gave one to Marcus.",
            "Heard a radio whisper: someone east of the dam, day 11 dispatch.",
            "Tomorrow: clear the south plague heart before it metastasizes.",
        ]):
            parts.append(
                f'<text x="{right_inner + 18}" y="{sy + 36 + i * 30}" font-family="{FONT_HAND}" '
                f'font-size="20" fill="{INK_BLUE}">{xml_escape(line)}</text>'
            )
        parts.append(tab_strip_right(c, "PEOPLE", c.device_w - c.inset - 60, py + 80))
        parts.append(wax_seal(c.device_w - 280, c.device_h - 200, label="TRANSMIT"))
    return "\n".join(parts)


def wax_seal(x: int, y: int, label: str = "TRANSMIT", size: int = 130) -> str:
    cx = x + size // 2
    cy = y + size // 2
    r = size // 2 - 12
    return dedent(f"""\
    <g>
      <path d="M{x + 12} {cy + r - 6} q{r} -10 {2*r - 12} 0 v18 q-{r} 10 -{2*r - 12} 0 z"
            fill="{INK_RED}" opacity="0.85"/>
      <circle cx="{cx}" cy="{cy}" r="{r}" fill="{INK_RED}"/>
      <circle cx="{cx - 6}" cy="{cy - 8}" r="{r}" fill="{PAPER}" opacity="0.18"/>
      <circle cx="{cx}" cy="{cy}" r="{int(r * 0.55)}" fill="none" stroke="{PAPER}" stroke-width="1.5"/>
      <line x1="{cx}" y1="{cy - int(r * 0.55)}" x2="{cx}" y2="{cy + int(r * 0.55)}"
            stroke="{PAPER}" stroke-width="1.5"/>
      <line x1="{cx - int(r * 0.55)}" y1="{cy}" x2="{cx + int(r * 0.55)}" y2="{cy}"
            stroke="{PAPER}" stroke-width="1.5"/>
      <text x="{cx}" y="{cy + r + 14}" text-anchor="middle" font-family="{FONT_TYPE}"
            font-size="11" fill="{PAPER}" letter-spacing="2.5">{xml_escape(label)}</text>
    </g>
    """)


def people_front(c: Canvas) -> str:
    px, py = c.page_x + 18, c.page_y + 24
    parts = [
        f'<text x="{px}" y="{py + 14}" font-family="{FONT_TYPE}" font-size="11" '
        f'fill="{INK_BROWN}" letter-spacing="2">PEOPLE · FRONT</text>',
    ]
    # filter chips: alive / fallen / legacy
    chip_labels = ["ALIVE", "FALLEN", "LEGACY"]
    chip_y = py + 30
    chip_x = px
    chip_w = 72
    for i, lbl in enumerate(chip_labels):
        is_active = i == 0
        fill = INK_BROWN if is_active else "none"
        text_color = PAPER if is_active else INK_BROWN
        cx = chip_x + i * (chip_w + 8)
        parts.append(
            f'<rect x="{cx}" y="{chip_y}" width="{chip_w}" height="28" fill="{fill}" '
            f'stroke="{INK_BROWN}" stroke-width="1.2" rx="3"/>'
        )
        parts.append(
            f'<text x="{cx + chip_w/2}" y="{chip_y + 18}" text-anchor="middle" '
            f'font-family="{FONT_TYPE}" font-size="10" fill="{text_color}" '
            f'letter-spacing="1.5">{lbl}</text>'
        )

    survivors = [
        ("Maya", "28", "Tough · Leader", "Shoot · Med", "high", "JOINED D1", None),
        ("Ed", "31", "Loyal · Cooking", "Scout · Stealth", "ok", "D1", None),
        ("Marcus", "44", "Vet · Mechanic", "Repair · Drive", "low", "D5", None),
        ("Lena", "22", "Quick · Runner", "Cardio · Med", "high", "D7", None),
        ("Sam", "39", "Stoic · Plowing", "Garden · Repair", "ok", "D9", None),
        ("Reyes", "26", "Sharp", "Shoot · Stealth", "—", "D11", "KIA"),
    ]
    if c.device_w == MOBILE_W:
        # 1 column, ~2 visible
        card_w = c.page_w - 36
        card_h = 130
        cy_ = py + 80
        for s in survivors[:3]:
            parts.append(index_card(px, cy_, card_w, card_h, *s))
            cy_ += card_h + 18
        parts.append(ribbon_nav(c, "PEOPLE"))
    elif c.device_w == TABLET_W:
        # 2 columns, ~6 visible
        card_w = (c.page_w - 80) // 2
        card_h = 150
        gap = 24
        cols = 2
        cy_ = py + 80
        for i, s in enumerate(survivors[:6]):
            cx_ = px + (i % cols) * (card_w + gap)
            ry = cy_ + (i // cols) * (card_h + 24)
            parts.append(index_card(cx_, ry, card_w, card_h, *s))
        parts.append(tab_strip_right(c, "PEOPLE", c.device_w - c.inset - 60, py + 70))
    else:
        # desktop — 3 columns, full grid
        spine_x = c.page_x + c.page_w // 2
        parts.append(
            f'<rect x="{spine_x - 4}" y="{c.page_y}" width="8" height="{c.page_h}" '
            f'fill="{LEATHER_SHADOW}" opacity="0.4"/>'
        )
        card_w = 280
        card_h = 170
        gap = 24
        cols = 3
        cy_ = py + 80
        for i, s in enumerate(survivors):
            cx_ = px + (i % cols) * (card_w + gap)
            ry = cy_ + (i // cols) * (card_h + 28)
            parts.append(index_card(cx_, ry, card_w, card_h, *s))
        parts.append(tab_strip_right(c, "PEOPLE", c.device_w - c.inset - 60, py + 80))
    return "\n".join(parts)


def people_back(c: Canvas) -> str:
    """TIES panel — card flipped to back face showing relationship rows."""
    px, py = c.page_x + 18, c.page_y + 24
    parts = [
        f'<text x="{px}" y="{py + 14}" font-family="{FONT_TYPE}" font-size="11" '
        f'fill="{INK_BROWN}" letter-spacing="2">PEOPLE · CARD-BACK · TIES</text>',
    ]
    # title + flip-back affordance
    if c.device_w == MOBILE_W:
        card_x = px
        card_y = py + 36
        card_w = c.page_w - 36
        card_h = c.page_h - 80 - 70  # room for ribbon
    elif c.device_w == TABLET_W:
        card_x = px + 40
        card_y = py + 80
        card_w = c.page_w - 80 - 60  # leave tab gutter
        card_h = c.page_h - 160
    else:
        card_x = px + 80
        card_y = py + 80
        card_w = c.page_w - 200 - 60
        card_h = c.page_h - 160

    parts.append(
        f'<rect x="{card_x}" y="{card_y}" width="{card_w}" height="{card_h}" '
        f'fill="{PAPER}" stroke="{PAPER_STAINED}" stroke-width="0.6" rx="4"/>'
    )
    parts.append(
        f'<use href="#paperclip" x="{card_x + card_w/2 - 14}" y="{card_y - 14}" '
        f'width="28" height="44"/>'
    )
    # header: name, "BACK OF CARD", flip arrow
    parts.append(
        f'<text x="{card_x + 18}" y="{card_y + 28}" font-family="{FONT_HAND}" '
        f'font-size="22" fill="{INK_BLUE}">Maya, 28</text>'
    )
    parts.append(
        f'<text x="{card_x + 18}" y="{card_y + 48}" font-family="{FONT_TYPE}" '
        f'font-size="10" fill="{INK_BROWN}" letter-spacing="2">— TIES —</text>'
    )
    parts.append(
        f'<text x="{card_x + card_w - 18}" y="{card_y + 28}" text-anchor="end" '
        f'font-family="{FONT_MONO}" font-size="10" fill="{INK_BROWN}" '
        f'opacity="0.7">↺ flip to front</text>'
    )

    ties = [
        ("PARTNER",  "Ed — husband, met in Trumbull", None),
        ("MENTOR",   "Marcus — taught me to shoot", None),
        ("FRIEND",   "Lena — runs route with me", None),
        ("FRIEND",   "Reyes — quiet, loved birds", "MOURNED"),
        ("RIVAL",    "Sam — fought over the radio", "STRAINED"),
    ]
    row_y = card_y + 70
    row_h = 56 if c.device_w != MOBILE_W else 64
    inner_pad = 16
    for kind, label, status in ties:
        parts.append(
            f'<line x1="{card_x + inner_pad}" y1="{row_y}" '
            f'x2="{card_x + card_w - inner_pad}" y2="{row_y}" '
            f'stroke="{PAPER_STAINED}" stroke-width="0.6"/>'
        )
        # kind glyph: linked rings
        gx = card_x + inner_pad + 12
        gy = row_y + row_h / 2
        parts.append(
            f'<circle cx="{gx}" cy="{gy}" r="6" fill="none" stroke="{INK_BROWN}" stroke-width="1.4"/>'
            f'<circle cx="{gx + 10}" cy="{gy}" r="6" fill="none" stroke="{INK_BROWN}" stroke-width="1.4"/>'
        )
        parts.append(
            f'<text x="{card_x + inner_pad + 36}" y="{row_y + 20}" font-family="{FONT_MONO}" '
            f'font-size="10" fill="{INK_BROWN}" letter-spacing="1">{kind}'
            + (f" · {status}" if status else "") + "</text>"
        )
        parts.append(
            f'<text x="{card_x + inner_pad + 36}" y="{row_y + 42}" font-family="{FONT_HAND}" '
            f'font-size="18" fill="{INK_BLUE}">{xml_escape(label)}</text>'
        )
        if status == "MOURNED":
            parts.append(
                f'<rect x="{card_x + inner_pad}" y="{row_y + 4}" width="3" height="{row_h - 8}" '
                f'fill="{INK_BROWN}"/>'
            )
        if status == "STRAINED":
            parts.append(
                f'<path d="M{card_x + inner_pad + 36} {row_y + 48} q4 -3 8 0 t8 0 t8 0 t8 0 t8 0" '
                f'stroke="{INK_RED}" stroke-width="1" fill="none"/>'
            )
        # EDIT chip
        ex = card_x + card_w - inner_pad - 50
        ey = row_y + (row_h - 30) / 2
        parts.append(
            f'<rect x="{ex}" y="{ey}" width="44" height="30" fill="none" '
            f'stroke="{INK_BROWN}" stroke-width="1" rx="2" opacity="0.7"/>'
        )
        parts.append(
            f'<text x="{ex + 22}" y="{ey + 19}" text-anchor="middle" font-family="{FONT_TYPE}" '
            f'font-size="10" fill="{INK_BROWN}" letter-spacing="1.5">EDIT</text>'
        )
        row_y += row_h
    # add-tie row
    parts.append(
        f'<line x1="{card_x + inner_pad}" y1="{row_y}" '
        f'x2="{card_x + card_w - inner_pad}" y2="{row_y}" '
        f'stroke="{PAPER_STAINED}" stroke-width="0.6"/>'
    )
    parts.append(
        f'<rect x="{card_x + inner_pad}" y="{row_y + 8}" '
        f'width="{card_w - 2 * inner_pad}" height="40" fill="none" stroke="{INK_BROWN}" '
        f'stroke-dasharray="4 4" stroke-width="1" rx="3"/>'
    )
    parts.append(
        f'<text x="{card_x + card_w / 2}" y="{row_y + 33}" text-anchor="middle" '
        f'font-family="{FONT_TYPE}" font-size="11" fill="{INK_BROWN}" letter-spacing="2">+ ADD TIE</text>'
    )

    if c.device_w == MOBILE_W:
        parts.append(ribbon_nav(c, "PEOPLE"))
    else:
        parts.append(tab_strip_right(c, "PEOPLE", c.device_w - c.inset - 60,
                                     c.page_y + 80))
    return "\n".join(parts)


def people_pencil_overlay(c: Canvas) -> str:
    """Desktop only — pencil-line web of strongest ties between cards."""
    px, py = c.page_x + 18, c.page_y + 24
    parts = [
        f'<text x="{px}" y="{py + 14}" font-family="{FONT_TYPE}" font-size="11" '
        f'fill="{INK_BROWN}" letter-spacing="2">PEOPLE · PENCIL OVERLAY · DESKTOP ONLY</text>',
    ]
    if c.device_w != DESKTOP_W:
        # Mobile / tablet fallback: show the back-of-card panel as the surrogate.
        parts.append(
            f'<text x="{px}" y="{py + 36}" font-family="{FONT_MONO}" font-size="12" '
            f'fill="{INK_BROWN}" opacity="0.9">FALLBACK · this view is desktop-only.</text>'
        )
        parts.append(
            f'<text x="{px}" y="{py + 56}" font-family="{FONT_MONO}" font-size="11" '
            f'fill="{INK_BROWN}" opacity="0.8">On {c.device_w}px viewports the visual web</text>'
        )
        parts.append(
            f'<text x="{px}" y="{py + 72}" font-family="{FONT_MONO}" font-size="11" '
            f'fill="{INK_BROWN}" opacity="0.8">collapses to the per-card TIES panel (§4)</text>'
        )
        parts.append(
            f'<text x="{px}" y="{py + 88}" font-family="{FONT_MONO}" font-size="11" '
            f'fill="{INK_BROWN}" opacity="0.8">with the same rows. No data lost.</text>'
        )
        # show one back-of-card as the fallback artifact
        cx_ = px + 30
        cy_ = py + 130
        cw_ = min(c.page_w - 60, 460)
        ch_ = 320
        parts.append(
            f'<rect x="{cx_}" y="{cy_}" width="{cw_}" height="{ch_}" fill="{PAPER}" '
            f'stroke="{PAPER_STAINED}" stroke-width="0.6" rx="4"/>'
        )
        parts.append(
            f'<use href="#paperclip" x="{cx_ + cw_/2 - 14}" y="{cy_ - 14}" '
            f'width="28" height="44"/>'
        )
        parts.append(
            f'<text x="{cx_ + 18}" y="{cy_ + 28}" font-family="{FONT_HAND}" '
            f'font-size="22" fill="{INK_BLUE}">Maya, 28</text>'
        )
        parts.append(
            f'<text x="{cx_ + 18}" y="{cy_ + 48}" font-family="{FONT_TYPE}" '
            f'font-size="10" fill="{INK_BROWN}" letter-spacing="2">— TIES (collapsed view) —</text>'
        )
        ties = [
            ("PARTNER", "Ed — husband"),
            ("MENTOR",  "Marcus — taught me to shoot"),
            ("FRIEND",  "Lena — runs route with me"),
            ("FRIEND",  "Reyes — quiet, loved birds (mourned)"),
        ]
        for i, (k, v) in enumerate(ties):
            parts.append(
                f'<text x="{cx_ + 18}" y="{cy_ + 80 + i * 32}" font-family="{FONT_MONO}" '
                f'font-size="10" fill="{INK_BROWN}" letter-spacing="1">{k}</text>'
            )
            parts.append(
                f'<text x="{cx_ + 110}" y="{cy_ + 80 + i * 32}" font-family="{FONT_HAND}" '
                f'font-size="16" fill="{INK_BLUE}">{xml_escape(v)}</text>'
            )
        if c.device_w == MOBILE_W:
            parts.append(ribbon_nav(c, "PEOPLE"))
        else:
            parts.append(tab_strip_right(c, "PEOPLE", c.device_w - c.inset - 60, py + 70))
        return "\n".join(parts)

    # Desktop — full pencil web
    spine_x = c.page_x + c.page_w // 2
    parts.append(
        f'<rect x="{spine_x - 4}" y="{c.page_y}" width="8" height="{c.page_h}" '
        f'fill="{LEATHER_SHADOW}" opacity="0.4"/>'
    )
    survivors = [
        ("Maya", "28", "Tough · Leader", "Shoot · Med", "high", "D1", None),
        ("Ed", "31", "Loyal", "Scout", "ok", "D1", None),
        ("Marcus", "44", "Vet · Mechanic", "Repair", "low", "D5", None),
        ("Lena", "22", "Quick", "Cardio", "high", "D7", None),
        ("Sam", "39", "Stoic", "Garden", "ok", "D9", None),
        ("Reyes", "26", "Sharp", "Shoot", "—", "D11", "KIA"),
    ]
    card_w, card_h, gap = 280, 170, 24
    cy_ = py + 80
    centers = []
    for i, s in enumerate(survivors):
        cx_ = px + (i % 3) * (card_w + gap)
        ry = cy_ + (i // 3) * (card_h + 28)
        parts.append(index_card(cx_, ry, card_w, card_h, *s))
        centers.append((s[0], cx_ + card_w / 2, ry + card_h / 2))
    # pencil-line ties (strongest only)
    web = [
        ("Maya", "Ed",     "PARTNER"),
        ("Maya", "Marcus", "MENTOR"),
        ("Maya", "Lena",   "FRIEND"),
        ("Ed",   "Marcus", "ALLY"),
        ("Lena", "Sam",    "ALLY"),
        ("Maya", "Reyes",  "MOURNED"),
    ]
    by_name = {n: (x, y) for (n, x, y) in centers}
    for a, b, kind in web:
        ax, ay = by_name[a]
        bx, by_ = by_name[b]
        # slight curve via control point above midpoint
        mx = (ax + bx) / 2
        my = (ay + by_) / 2 - 28
        stroke = INK_BROWN if kind != "MOURNED" else INK_RED
        opacity = "0.55" if kind != "MOURNED" else "0.7"
        dash = "" if kind != "MOURNED" else 'stroke-dasharray="4 4"'
        parts.append(
            f'<path d="M{ax} {ay} Q{mx} {my} {bx} {by_}" stroke="{stroke}" '
            f'stroke-width="1.2" fill="none" opacity="{opacity}" {dash}/>'
        )
        # label at midpoint
        parts.append(
            f'<rect x="{mx - 28}" y="{my - 10}" width="56" height="14" fill="{PAPER}" '
            f'opacity="0.85"/>'
        )
        parts.append(
            f'<text x="{mx}" y="{my + 1}" text-anchor="middle" font-family="{FONT_TYPE}" '
            f'font-size="9" fill="{stroke}" letter-spacing="1">{kind}</text>'
        )
    parts.append(tab_strip_right(c, "PEOPLE", c.device_w - c.inset - 60, py + 80))
    # legend
    legend_x = c.device_w - c.inset - 220
    legend_y = c.page_y + c.page_h - 130
    parts.append(
        f'<rect x="{legend_x}" y="{legend_y}" width="200" height="100" '
        f'fill="{PAPER}" stroke="{PAPER_STAINED}" stroke-width="0.5"/>'
    )
    parts.append(
        f'<text x="{legend_x + 12}" y="{legend_y + 20}" font-family="{FONT_TYPE}" '
        f'font-size="10" fill="{INK_BROWN}" letter-spacing="2">LEGEND</text>'
    )
    parts.append(
        f'<line x1="{legend_x + 12}" y1="{legend_y + 36}" x2="{legend_x + 60}" y2="{legend_y + 36}" '
        f'stroke="{INK_BROWN}" stroke-width="1.2" opacity="0.55"/>'
    )
    parts.append(
        f'<text x="{legend_x + 70}" y="{legend_y + 40}" font-family="{FONT_MONO}" '
        f'font-size="10" fill="{INK_BROWN}">strongest tie</text>'
    )
    parts.append(
        f'<line x1="{legend_x + 12}" y1="{legend_y + 56}" x2="{legend_x + 60}" y2="{legend_y + 56}" '
        f'stroke="{INK_RED}" stroke-width="1.2" stroke-dasharray="4 4" opacity="0.7"/>'
    )
    parts.append(
        f'<text x="{legend_x + 70}" y="{legend_y + 60}" font-family="{FONT_MONO}" '
        f'font-size="10" fill="{INK_BROWN}">mourned tie</text>'
    )
    parts.append(
        f'<text x="{legend_x + 12}" y="{legend_y + 82}" font-family="{FONT_MONO}" '
        f'font-size="9" fill="{INK_BROWN}" opacity="0.7">canonical: card-back rows.</text>'
    )
    return "\n".join(parts)


def history(c: Canvas) -> str:
    px, py = c.page_x + 18, c.page_y + 24
    parts = [
        f'<text x="{px}" y="{py + 14}" font-family="{FONT_TYPE}" font-size="11" '
        f'fill="{INK_BROWN}" letter-spacing="2">HISTORY · PAST PAGES</text>',
    ]
    days = [
        ("D14", "Tue · clear",  "Maya killed a feral.",        "high"),
        ("D13", "Mon · rain",   "Lost 2 food to mold.",         "ok"),
        ("D12", "Sun · clear",  "Found 4 medkits at the pharm.","high"),
        ("D11", "Sat · fog",    "Reyes — KIA. North highway.",  "low"),
        ("D10", "Fri · clear",  "Sam joined the community.",    "high"),
        ("D09", "Thu · clear",  "Cleared the south plague heart","ok"),
        ("D08", "Wed · rain",   "Quiet day. Repaired the gate.","ok"),
    ]

    if c.device_w == MOBILE_W:
        # vertical stack of past-day strips
        sy = py + 36
        for d, weather, note, mood in days[:5]:
            parts.append(
                f'<rect x="{px}" y="{sy}" width="{c.page_w - 36}" height="76" '
                f'fill="{PAPER}" stroke="{PAPER_STAINED}" stroke-width="0.5" rx="3"/>'
            )
            parts.append(
                f'<text x="{px + 12}" y="{sy + 22}" font-family="{FONT_TYPE}" font-size="11" '
                f'fill="{INK_BROWN}" letter-spacing="2">{d} · {weather}</text>'
            )
            parts.append(
                f'<text x="{px + 12}" y="{sy + 50}" font-family="{FONT_HAND}" font-size="18" '
                f'fill="{INK_BLUE}">{xml_escape(note)}</text>'
            )
            mood_color = INK_BLUE if mood == "high" else INK_BROWN if mood == "ok" else INK_RED
            parts.append(
                f'<text x="{px + c.page_w - 60}" y="{sy + 24}" font-family="{FONT_MONO}" '
                f'font-size="10" fill="{mood_color}">{mood.upper()}</text>'
            )
            sy += 84
        parts.append(ribbon_nav(c, "EVENTS"))
    elif c.device_w == TABLET_W:
        # stacked slightly-rotated cards (the "stack" metaphor)
        sx = px + 30
        sy = py + 60
        cw_ = c.page_w - 140
        ch_ = 110
        for i, (d, weather, note, mood) in enumerate(days[:6]):
            rotate = -1.0 + (i % 3) * 0.6
            cx = sx
            cy_ = sy + i * (ch_ - 18)
            mid_x = cx + cw_ / 2
            mid_y = cy_ + ch_ / 2
            parts.append(f'<g transform="rotate({rotate} {mid_x} {mid_y})">')
            parts.append(
                f'<rect x="{cx}" y="{cy_}" width="{cw_}" height="{ch_}" fill="{PAPER}" '
                f'stroke="{PAPER_STAINED}" stroke-width="0.6" rx="4"/>'
            )
            parts.append(
                f'<text x="{cx + 16}" y="{cy_ + 28}" font-family="{FONT_TYPE}" font-size="12" '
                f'fill="{INK_BROWN}" letter-spacing="2">{d} · {weather}</text>'
            )
            parts.append(
                f'<text x="{cx + 16}" y="{cy_ + 60}" font-family="{FONT_HAND}" font-size="20" '
                f'fill="{INK_BLUE}">{xml_escape(note)}</text>'
            )
            mood_color = INK_BLUE if mood == "high" else INK_BROWN if mood == "ok" else INK_RED
            parts.append(
                f'<text x="{cx + cw_ - 80}" y="{cy_ + 28}" font-family="{FONT_MONO}" '
                f'font-size="11" fill="{mood_color}">MORALE · {mood}</text>'
            )
            parts.append(
                f'<use href="#paperclip" x="{cx + cw_/2 - 12}" y="{cy_ - 12}" '
                f'width="24" height="36"/>'
            )
            parts.append("</g>")
        parts.append(tab_strip_right(c, "EVENTS", c.device_w - c.inset - 60, py + 70))
    else:
        # desktop — calendar-strip + open detail of one day
        spine_x = c.page_x + c.page_w // 2
        parts.append(
            f'<rect x="{spine_x - 4}" y="{c.page_y}" width="8" height="{c.page_h}" '
            f'fill="{LEATHER_SHADOW}" opacity="0.4"/>'
        )
        # left: stack of past days
        sx = px + 30
        sy = py + 80
        cw_ = spine_x - sx - 60
        ch_ = 90
        for i, (d, weather, note, mood) in enumerate(days):
            rotate = -1.2 + (i % 3) * 0.6
            mid_x = sx + cw_ / 2
            mid_y = sy + ch_ / 2
            parts.append(f'<g transform="rotate({rotate} {mid_x} {mid_y})">')
            parts.append(
                f'<rect x="{sx}" y="{sy}" width="{cw_}" height="{ch_}" fill="{PAPER}" '
                f'stroke="{PAPER_STAINED}" stroke-width="0.6" rx="4"/>'
            )
            parts.append(
                f'<text x="{sx + 16}" y="{sy + 28}" font-family="{FONT_TYPE}" font-size="12" '
                f'fill="{INK_BROWN}" letter-spacing="2">{d} · {weather}</text>'
            )
            parts.append(
                f'<text x="{sx + 16}" y="{sy + 56}" font-family="{FONT_HAND}" font-size="20" '
                f'fill="{INK_BLUE}">{xml_escape(note)}</text>'
            )
            mood_color = INK_BLUE if mood == "high" else INK_BROWN if mood == "ok" else INK_RED
            parts.append(
                f'<text x="{sx + cw_ - 90}" y="{sy + 28}" font-family="{FONT_MONO}" '
                f'font-size="11" fill="{mood_color}">{mood.upper()}</text>'
            )
            parts.append(
                f'<use href="#paperclip" x="{sx + cw_/2 - 12}" y="{sy - 12}" '
                f'width="24" height="36"/>'
            )
            parts.append("</g>")
            sy += ch_ - 8

        # right: open detail of D12 ("found 4 medkits")
        rx = spine_x + 30
        ry = py + 80
        rw = c.device_w - c.inset - rx - 80  # leave tab gutter
        rh = c.page_h - 160
        parts.append(
            f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" fill="{PAPER}" '
            f'stroke="{PAPER_STAINED}" stroke-width="0.6" rx="4"/>'
        )
        parts.append(
            f'<use href="#paperclip" x="{rx + rw/2 - 14}" y="{ry - 14}" '
            f'width="28" height="44"/>'
        )
        parts.append(
            f'<text x="{rx + 20}" y="{ry + 30}" font-family="{FONT_TYPE}" font-size="13" '
            f'fill="{INK_BROWN}" letter-spacing="2">D12 · SUN · CLEAR</text>'
        )
        parts.append(
            f'<text x="{rx + 20}" y="{ry + 60}" font-family="{FONT_HAND}" font-size="24" '
            f'fill="{INK_BLUE}">A long, quiet day.</text>'
        )
        for i, line in enumerate([
            "Marcus drove the truck to the pharmacy on 9th.",
            "Found 4 medkits, 2 cans of food, an unopened",
            "bottle of antibiotics. Lena watched the door.",
            "No infestations along the route. We slept well.",
        ]):
            parts.append(
                f'<text x="{rx + 20}" y="{ry + 100 + i * 28}" font-family="{FONT_HAND}" '
                f'font-size="20" fill="{INK_BLUE}">{xml_escape(line)}</text>'
            )
        parts.append(
            f'<text x="{rx + 20}" y="{ry + rh - 60}" font-family="{FONT_TYPE}" font-size="10" '
            f'fill="{INK_BROWN}" letter-spacing="2">RESOURCES Δ</text>'
        )
        parts.append(
            f'<text x="{rx + 20}" y="{ry + rh - 38}" font-family="{FONT_MONO}" font-size="11" '
            f'fill="{INK_BROWN}">food +2 · meds +4 · ammo 0 · fuel −1</text>'
        )
        parts.append(tab_strip_right(c, "EVENTS", c.device_w - c.inset - 60, py + 80))
    return "\n".join(parts)


def report_panel(c: Canvas) -> str:
    """Generated Report panel — TRANSMIT TO NETWORK output, plain-mono."""
    px, py = c.page_x + 18, c.page_y + 24
    parts = [
        f'<text x="{px}" y="{py + 14}" font-family="{FONT_TYPE}" font-size="11" '
        f'fill="{INK_BROWN}" letter-spacing="2">GENERATED REPORT · TRANSMIT TO NETWORK</text>',
    ]
    report_lines = [
        "════════════════════════════════════",
        "  NETWORK DISPATCH · DAY 14",
        "  Trumbull Pt. · Maya, broadcasting",
        "════════════════════════════════════",
        "",
        "WEATHER ··· clear, 62°F",
        "MORALE  ··· high",
        "",
        "RESOURCES",
        "  food          5",
        "  meds          2",
        "  ammo         11",
        "  fuel          3",
        "  materials     8",
        "",
        "PLAGUE HEARTS  2 · west sector",
        "",
        "EVENTS",
        "  - Maya killed a feral on the highway.",
        "  - Ed scavenged the gas station, +2 medkits.",
        "  - Reyes laid to rest. Day 11 dispatch.",
        "",
        "TIES UPDATED",
        "  - Maya → Marcus    MENTOR",
        "  - Lena → Sam       ALLY",
        "",
        "SHARED TODAY, STRONGER TOMORROW.",
    ]
    if c.device_w == MOBILE_W:
        # full-width mono block + COPY AS MARKDOWN stamp + share/transmit
        bx = px
        by = py + 36
        bw = c.page_w - 36
        bh = c.page_h - 130 - 64
        parts.append(
            f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="{PAPER}" '
            f'stroke="{PAPER_STAINED}" stroke-width="0.5" rx="3"/>'
        )
        line_y = by + 26
        for line in report_lines[:24]:
            parts.append(
                f'<text x="{bx + 14}" y="{line_y}" font-family="{FONT_MONO}" font-size="10" '
                f'fill="{INK_BROWN}">{xml_escape(line)}</text>'
            )
            line_y += 16
        parts.append(stamp_button(bx, by + bh + 14, 160, 44, "COPY AS MD"))
        parts.append(stamp_button(bx + 170, by + bh + 14, 130, 44, "TRANSMIT", fill=INK_RED))
        parts.append(ribbon_nav(c, "DISP"))
    elif c.device_w == TABLET_W:
        # block + footer with stamp buttons side by side
        bx = px
        by = py + 60
        bw = c.page_w - 80
        bh = c.page_h - 240
        parts.append(
            f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="{PAPER}" '
            f'stroke="{PAPER_STAINED}" stroke-width="0.5" rx="3"/>'
        )
        line_y = by + 28
        for line in report_lines:
            parts.append(
                f'<text x="{bx + 18}" y="{line_y}" font-family="{FONT_MONO}" font-size="11" '
                f'fill="{INK_BROWN}">{xml_escape(line)}</text>'
            )
            line_y += 18
        parts.append(stamp_button(bx, by + bh + 24, 200, 52, "COPY AS MARKDOWN"))
        parts.append(stamp_button(bx + 220, by + bh + 24, 180, 52, "REGENERATE"))
        parts.append(wax_seal(bx + bw - 160, by + bh - 4, "TRANSMIT"))
        parts.append(tab_strip_right(c, "DISP", c.device_w - c.inset - 60, py + 60))
    else:
        # desktop — split: left page is the report, right page is share preview (tweet/clipboard)
        spine_x = c.page_x + c.page_w // 2
        parts.append(
            f'<rect x="{spine_x - 4}" y="{c.page_y}" width="8" height="{c.page_h}" '
            f'fill="{LEATHER_SHADOW}" opacity="0.4"/>'
        )
        bx = px + 20
        by = py + 60
        bw = spine_x - bx - 30
        bh = c.page_h - 200
        parts.append(
            f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="{PAPER}" '
            f'stroke="{PAPER_STAINED}" stroke-width="0.5" rx="3"/>'
        )
        line_y = by + 28
        for line in report_lines:
            parts.append(
                f'<text x="{bx + 22}" y="{line_y}" font-family="{FONT_MONO}" font-size="12" '
                f'fill="{INK_BROWN}">{xml_escape(line)}</text>'
            )
            line_y += 20
        parts.append(stamp_button(bx, by + bh + 24, 220, 52, "COPY AS MARKDOWN"))
        parts.append(stamp_button(bx + 240, by + bh + 24, 180, 52, "REGENERATE"))

        # right: preview of what gets shared (clipboard pane + wax seal)
        rx = spine_x + 30
        ry = py + 60
        rw = c.device_w - c.inset - rx - 80
        rh = c.page_h - 200
        parts.append(
            f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" fill="{PAPER}" '
            f'stroke="{PAPER_STAINED}" stroke-width="0.5" rx="3"/>'
        )
        parts.append(
            f'<text x="{rx + 20}" y="{ry + 28}" font-family="{FONT_TYPE}" font-size="11" '
            f'fill="{INK_BROWN}" letter-spacing="2">SHARE PREVIEW</text>'
        )
        parts.append(
            f'<text x="{rx + 20}" y="{ry + 50}" font-family="{FONT_MONO}" font-size="10" '
            f'fill="{INK_BROWN}" opacity="0.7">clipboard format · plain text</text>'
        )
        for i, line in enumerate(report_lines[:18]):
            parts.append(
                f'<text x="{rx + 20}" y="{ry + 80 + i * 18}" font-family="{FONT_MONO}" '
                f'font-size="11" fill="{INK_BROWN}" opacity="0.85">{xml_escape(line)}</text>'
            )
        parts.append(wax_seal(rx + rw - 180, ry + rh - 200, "TRANSMIT", size=160))
        parts.append(tab_strip_right(c, "DISP", c.device_w - c.inset - 60, py + 60))
    return "\n".join(parts)


def sync_panel(c: Canvas) -> str:
    """Sync radio panel: closed / open / conflict — all three states stacked."""
    px, py = c.page_x + 18, c.page_y + 24
    parts = [
        f'<text x="{px}" y="{py + 14}" font-family="{FONT_TYPE}" font-size="11" '
        f'fill="{INK_BROWN}" letter-spacing="2">SYNC RADIO · CLOSED · OPEN · CONFLICT</text>',
    ]

    def dial(x: int, y: int, size: int, pointer_angle: float, halo: str = "") -> str:
        cx, cy = x + size // 2, y + size // 2
        r = size // 2 - 4
        # pointer end
        import math
        a = math.radians(pointer_angle - 90)
        ex = cx + math.cos(a) * (r - 8)
        ey = cy + math.sin(a) * (r - 8)
        out = []
        if halo:
            out.append(
                f'<circle cx="{cx}" cy="{cy}" r="{r + 8}" fill="none" stroke="{halo}" '
                f'stroke-width="6" opacity="0.4"/>'
            )
        out.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{LEATHER}" stroke="{AMBER}" stroke-width="2"/>'
        )
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r - 6}" fill="{LEATHER_SHADOW}"/>')
        out.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r - 12}" fill="none" stroke="{AMBER}" '
            f'stroke-width="0.6" opacity="0.5"/>'
        )
        # ticks
        for ta in (0, 90, 180, 270):
            ar = math.radians(ta - 90)
            sxp, syp = cx + math.cos(ar) * (r - 4), cy + math.sin(ar) * (r - 4)
            exp, eyp = cx + math.cos(ar) * (r - 10), cy + math.sin(ar) * (r - 10)
            out.append(
                f'<line x1="{sxp}" y1="{syp}" x2="{exp}" y2="{eyp}" stroke="{AMBER}" '
                f'stroke-width="1" opacity="0.6"/>'
            )
        out.append(
            f'<line x1="{cx}" y1="{cy}" x2="{ex}" y2="{ey}" stroke="{AMBER}" '
            f'stroke-width="3" stroke-linecap="round"/>'
        )
        out.append(f'<circle cx="{cx}" cy="{cy}" r="3" fill="{AMBER}"/>')
        return "\n".join(out)

    if c.device_w == MOBILE_W:
        # three sections stacked vertically: closed, open, conflict
        sx = px
        sy = py + 36
        # CLOSED
        parts.append(
            f'<rect x="{sx}" y="{sy}" width="{c.page_w - 36}" height="80" fill="{PAPER}" '
            f'stroke="{PAPER_STAINED}" stroke-width="0.5" rx="3"/>'
        )
        parts.append(dial(sx + 12, sy + 12, 56, 0))
        parts.append(
            f'<text x="{sx + 80}" y="{sy + 30}" font-family="{FONT_TYPE}" font-size="11" '
            f'fill="{INK_BROWN}" letter-spacing="2">SYNC · OFF</text>'
        )
        parts.append(
            f'<text x="{sx + 80}" y="{sy + 50}" font-family="{FONT_MONO}" font-size="10" '
            f'fill="{INK_BROWN}" opacity="0.7">tap dial to enable</text>'
        )
        sy += 96
        # OPEN — gist mode + QR telegram
        parts.append(
            f'<rect x="{sx}" y="{sy}" width="{c.page_w - 36}" height="280" fill="{PAPER}" '
            f'stroke="{PAPER_STAINED}" stroke-width="0.5" rx="3"/>'
        )
        parts.append(dial(sx + 12, sy + 14, 64, 180))
        parts.append(
            f'<text x="{sx + 90}" y="{sy + 30}" font-family="{FONT_TYPE}" font-size="11" '
            f'fill="{INK_BROWN}" letter-spacing="2">SYNC · GIST</text>'
        )
        parts.append(
            f'<text x="{sx + 90}" y="{sy + 50}" font-family="{FONT_MONO}" font-size="10" '
            f'fill="{INK_BROWN}" opacity="0.7">last synced 4m ago</text>'
        )
        # QR telegram
        qx = sx + 14
        qy = sy + 90
        parts.append(qr_telegram(qx, qy, c.page_w - 64, 170))
        sy += 296
        # CONFLICT
        parts.append(
            f'<rect x="{sx}" y="{sy}" width="{c.page_w - 36}" height="80" fill="{PAPER}" '
            f'stroke="{INK_RED}" stroke-width="1.4" rx="3"/>'
        )
        parts.append(dial(sx + 12, sy + 12, 56, 180, halo=INK_RED))
        parts.append(
            f'<text x="{sx + 80}" y="{sy + 28}" font-family="{FONT_TYPE}" font-size="11" '
            f'fill="{INK_RED}" letter-spacing="2">CONFLICT — REVIEW NEEDED</text>'
        )
        parts.append(
            f'<text x="{sx + 80}" y="{sy + 50}" font-family="{FONT_MONO}" font-size="10" '
            f'fill="{INK_BROWN}">food, morale differ between local + remote</text>'
        )
        parts.append(
            f'<text x="{sx + 80}" y="{sy + 66}" font-family="{FONT_MONO}" font-size="10" '
            f'fill="{INK_BROWN}" opacity="0.7">tap → opens conflict spread (§10)</text>'
        )
        parts.append(ribbon_nav(c, "DISP"))
    elif c.device_w == TABLET_W:
        # three columns side by side
        col_w = (c.page_w - 80 - 64) // 3
        col_y = py + 60
        col_h = c.page_h - 200
        for i, (state_label, mode_label, sub, halo) in enumerate([
            ("CLOSED", "SYNC · OFF", "tap dial to enable",        ""),
            ("OPEN",   "SYNC · GIST", "last synced 4m ago",       ""),
            ("CONFLICT", "CONFLICT", "review needed",            INK_RED),
        ]):
            cx_ = px + i * (col_w + 24)
            stroke = INK_RED if halo else PAPER_STAINED
            sw = "1.4" if halo else "0.5"
            parts.append(
                f'<rect x="{cx_}" y="{col_y}" width="{col_w}" height="{col_h}" fill="{PAPER}" '
                f'stroke="{stroke}" stroke-width="{sw}" rx="3"/>'
            )
            parts.append(
                f'<text x="{cx_ + 14}" y="{col_y + 24}" font-family="{FONT_TYPE}" font-size="11" '
                f'fill="{INK_BROWN}" letter-spacing="2">{state_label}</text>'
            )
            angle = 0 if i == 0 else 180
            parts.append(dial(cx_ + col_w/2 - 60, col_y + 50, 120, angle, halo=halo))
            color = INK_RED if halo else INK_BROWN
            parts.append(
                f'<text x="{cx_ + col_w/2}" y="{col_y + 200}" text-anchor="middle" '
                f'font-family="{FONT_TYPE}" font-size="12" fill="{color}" '
                f'letter-spacing="2">{mode_label}</text>'
            )
            parts.append(
                f'<text x="{cx_ + col_w/2}" y="{col_y + 222}" text-anchor="middle" '
                f'font-family="{FONT_MONO}" font-size="10" fill="{INK_BROWN}" '
                f'opacity="0.7">{sub}</text>'
            )
            if i == 1:  # OPEN — show QR telegram below
                parts.append(qr_telegram(cx_ + 14, col_y + 250, col_w - 28, 280))
            elif i == 2:  # CONFLICT — show diff preview
                parts.append(conflict_preview(cx_ + 14, col_y + 250, col_w - 28, 280))
        parts.append(tab_strip_right(c, "DISP", c.device_w - c.inset - 60, py + 60))
    else:
        # desktop — closed / open / conflict in three panels with deeper detail
        panel_w = (c.page_w - 100) // 3
        panel_y = py + 60
        panel_h = c.page_h - 220
        for i, (state_label, mode_label, sub, halo) in enumerate([
            ("CLOSED",   "SYNC · OFF",         "tap dial to enable",     ""),
            ("OPEN",     "SYNC · GIST",        "last synced 4m ago",     ""),
            ("CONFLICT", "CONFLICT — REVIEW", "food, morale, events",   INK_RED),
        ]):
            cx_ = px + i * (panel_w + 30)
            stroke = INK_RED if halo else PAPER_STAINED
            sw = "1.4" if halo else "0.5"
            parts.append(
                f'<rect x="{cx_}" y="{panel_y}" width="{panel_w}" height="{panel_h}" fill="{PAPER}" '
                f'stroke="{stroke}" stroke-width="{sw}" rx="3"/>'
            )
            parts.append(
                f'<text x="{cx_ + 16}" y="{panel_y + 28}" font-family="{FONT_TYPE}" font-size="12" '
                f'fill="{INK_BROWN}" letter-spacing="2">{state_label}</text>'
            )
            angle = 0 if i == 0 else 180
            parts.append(dial(cx_ + panel_w/2 - 70, panel_y + 60, 140, angle, halo=halo))
            color = INK_RED if halo else INK_BROWN
            parts.append(
                f'<text x="{cx_ + panel_w/2}" y="{panel_y + 230}" text-anchor="middle" '
                f'font-family="{FONT_TYPE}" font-size="13" fill="{color}" '
                f'letter-spacing="2">{mode_label}</text>'
            )
            parts.append(
                f'<text x="{cx_ + panel_w/2}" y="{panel_y + 252}" text-anchor="middle" '
                f'font-family="{FONT_MONO}" font-size="10" fill="{INK_BROWN}" '
                f'opacity="0.7">{sub}</text>'
            )
            if i == 1:
                parts.append(qr_telegram(cx_ + 18, panel_y + 280, panel_w - 36, panel_h - 320))
            elif i == 2:
                parts.append(conflict_preview(cx_ + 18, panel_y + 280, panel_w - 36, panel_h - 320))
        parts.append(tab_strip_right(c, "DISP", c.device_w - c.inset - 60, py + 60))
    return "\n".join(parts)


def qr_telegram(x: int, y: int, w: int, h: int) -> str:
    """QR code stamped onto a paper telegram. Approximate placeholder QR grid."""
    parts = [
        f'<g transform="rotate(-1 {x + w/2} {y + h/2})">',
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{PAPER}" '
        f'stroke="{PAPER_STAINED}" stroke-width="0.6"/>',
        f'<text x="{x + 14}" y="{y + 22}" font-family="{FONT_TYPE}" font-size="10" '
        f'fill="{INK_BROWN}" letter-spacing="2">— TELEGRAM —</text>',
        f'<line x1="{x + 14}" y1="{y + 30}" x2="{x + w - 14}" y2="{y + 30}" '
        f'stroke="{INK_BROWN}" stroke-width="0.5"/>',
    ]
    # approximate 9×9 QR
    qsize = min(w - 60, h - 90)
    qx = x + (w - qsize) / 2
    qy = y + 44
    parts.append(
        f'<rect x="{qx}" y="{qy}" width="{qsize}" height="{qsize}" fill="{PAPER}" '
        f'stroke="{INK_BROWN}" stroke-width="1"/>'
    )
    cell = qsize / 9
    pattern = [
        [1,1,1,1,0,1,1,1,1],
        [1,0,0,0,0,0,0,0,1],
        [1,0,1,1,0,1,1,0,1],
        [1,0,1,1,0,1,1,0,1],
        [0,1,0,1,1,0,1,1,0],
        [1,0,1,0,1,1,0,1,1],
        [1,0,1,1,0,1,1,0,1],
        [1,0,0,0,0,0,0,0,1],
        [1,1,1,1,0,1,1,1,1],
    ]
    for ry, row in enumerate(pattern):
        for cxn, v in enumerate(row):
            if v:
                parts.append(
                    f'<rect x="{qx + cxn * cell + 1}" y="{qy + ry * cell + 1}" '
                    f'width="{cell - 2}" height="{cell - 2}" fill="{INK_BROWN}"/>'
                )
    parts.append(
        f'<text x="{x + w/2}" y="{y + h - 24}" text-anchor="middle" font-family="{FONT_MONO}" '
        f'font-size="9" fill="{INK_BROWN}">SCAN ON OTHER DEVICE</text>'
    )
    parts.append(
        f'<text x="{x + w/2}" y="{y + h - 10}" text-anchor="middle" font-family="{FONT_MONO}" '
        f'font-size="8" fill="{INK_BROWN}" opacity="0.6">or copy link below</text>'
    )
    parts.append("</g>")
    return "\n".join(parts)


def conflict_preview(x: int, y: int, w: int, h: int) -> str:
    """Tiny preview of conflict spread embedded in the sync panel."""
    parts = []
    spine = x + w // 2
    parts.append(
        f'<rect x="{spine - 3}" y="{y}" width="6" height="{h}" fill="{LEATHER_SHADOW}"/>'
    )
    parts.append(
        f'<rect x="{x}" y="{y}" width="{w//2 - 3}" height="{h}" fill="{PAPER}" '
        f'stroke="{PAPER_STAINED}" stroke-width="0.5"/>'
    )
    parts.append(
        f'<rect x="{spine + 3}" y="{y}" width="{w//2 - 3}" height="{h}" fill="{PAPER}" '
        f'stroke="{PAPER_STAINED}" stroke-width="0.5"/>'
    )
    parts.append(
        f'<text x="{x + 8}" y="{y + 16}" font-family="{FONT_TYPE}" font-size="9" '
        f'fill="{INK_BROWN}" letter-spacing="2">LOCAL</text>'
    )
    parts.append(
        f'<text x="{spine + 11}" y="{y + 16}" font-family="{FONT_TYPE}" font-size="9" '
        f'fill="{INK_BROWN}" letter-spacing="2">REMOTE</text>'
    )
    rows = [
        ("food", "5", "3", True),
        ("morale", "high", "low", True),
        ("events", "2 entries", "2 entries", False),
        ("plague hearts", "2", "2", False),
    ]
    ry = y + 32
    for field_, lv, rv, conflict in rows:
        if conflict:
            parts.append(
                f'<rect x="{x + 4}" y="{ry - 2}" width="{w - 8}" height="14" '
                f'fill="{INK_RED}" opacity="0.18"/>'
            )
        parts.append(
            f'<text x="{x + 8}" y="{ry + 9}" font-family="{FONT_MONO}" font-size="9" '
            f'fill="{INK_BROWN}">{xml_escape(field_)}: {xml_escape(lv)}</text>'
        )
        parts.append(
            f'<text x="{spine + 11}" y="{ry + 9}" font-family="{FONT_MONO}" font-size="9" '
            f'fill="{INK_BROWN}">{xml_escape(field_)}: {xml_escape(rv)}</text>'
        )
        ry += 18
    # accept buttons row
    parts.append(
        f'<rect x="{x + 4}" y="{y + h - 26}" width="{w//2 - 12}" height="20" '
        f'fill="{INK_BROWN}" rx="2"/>'
    )
    parts.append(
        f'<text x="{x + w//4}" y="{y + h - 12}" text-anchor="middle" font-family="{FONT_TYPE}" '
        f'font-size="9" fill="{PAPER}" letter-spacing="1">KEEP LOCAL</text>'
    )
    parts.append(
        f'<rect x="{spine + 8}" y="{y + h - 26}" width="{w//2 - 12}" height="20" '
        f'fill="{INK_BROWN}" rx="2"/>'
    )
    parts.append(
        f'<text x="{spine + w//4 + 2}" y="{y + h - 12}" text-anchor="middle" '
        f'font-family="{FONT_TYPE}" font-size="9" fill="{PAPER}" '
        f'letter-spacing="1">TAKE REMOTE</text>'
    )
    return "\n".join(parts)


# ----------------------------------------------------------------
# Per-screen annotation tables
# ----------------------------------------------------------------
def annotations_for(screen: str, breakpoint: str, c: Canvas) -> List[Annotation]:
    """Return numbered annotations targeting xy points inside the device frame."""
    px, py = c.page_x + 18, c.page_y + 24
    if screen == "today":
        if breakpoint == "mobile":
            return [
                Annotation(1, (px + 100, py + 38), "§0 Page header",
                           "--font-typewriter · --font-hand · --ink-blue",
                           "Date stays in mono caps; handwritten day-name is decorative — typed day is canonical."),
                Annotation(2, (px + 80, py + 100), "§1 Input slot · DATE",
                           "--ink-brown 1.4px · --radius-sm",
                           "Falls back to flat <input> with solid border if SVG filter unsupported."),
                Annotation(3, (px + 80, py + 460), "§1 PLAGUE HEARTS",
                           "--ink-red border · --font-mono",
                           "Color is paired with the explicit text label; never rely on red alone."),
                Annotation(4, (px + 60, c.device_h - 80), "§7 Ribbon nav",
                           "--leather + --texture-leather · --amber 4px",
                           "Active section announced via aria-current=page; underline survives CSS strip."),
                Annotation(5, (c.device_w - 130, c.device_h - 130), "§13 Wax-seal TRANSMIT",
                           "--ink-red · --font-typewriter · --paper",
                           "Real <button> underneath; toast announced via aria-live polite."),
            ]
        if breakpoint == "tablet":
            return [
                Annotation(1, (px + 30, py + 90), "§6 Paperclip header · VITALS",
                           "--amber clip · --font-typewriter · --ink-brown",
                           "Decorative grouping; <section aria-labelledby> still asserts structure."),
                Annotation(2, (px + 200, py + 130), "§1 Input slot · MORALE",
                           "--font-mono label · --font-hand value",
                           "Caveat is decorative; numeric value (1–10) is canonical via <output>."),
                Annotation(3, (px + 360, py + 130), "§1 RESOURCES grid",
                           "--ink-brown 1.4px · --radius-sm",
                           "Two-column grid drops to single column under prefers-reduced-data."),
                Annotation(4, (px + 100, py + 460), "§1 PLAGUE HEARTS",
                           "--ink-red · --font-mono",
                           "Inline <small> error text accompanies the red border for AA-safe error signal."),
                Annotation(5, (c.device_w - 90, py + 200), "§5 Right-edge tabs",
                           "--paper-stained inactive · --paper active · --amber underline",
                           "Tabs degrade to a horizontal <nav> on small viewports; redundant cues for active."),
                Annotation(6, (c.device_w - 200, c.device_h - 80), "§13 Wax-seal TRANSMIT",
                           "--ink-red · --shadow-press",
                           "Single dominant CTA; never a second wax in v2."),
            ]
        return [  # desktop
            Annotation(1, (px + 80, py + 100), "§0 Two-page spread",
                       "--leather-shadow spine · 8px gutter",
                       "Lamp falls top-left; left page reads slightly brighter — drops under reduced-data."),
            Annotation(2, (px + 80, py + 250), "§1 Vitals slots",
                       "--ink-brown · --font-typewriter label",
                       "Label-as-affordance: <label for=> extends the hit-box without enlarging the art."),
            Annotation(3, (px + 80, py + 460), "§0 PLAGUE HEARTS",
                       "--ink-red border · --font-hand readout",
                       "Plain text 'PLAGUE HEARTS' carries meaning; red is redundant cue."),
            Annotation(4, (c.device_w/2 + 200, py + 200), "§6 RESOURCES paperclip",
                       "--amber clip · --font-typewriter",
                       "Clip groups visually; <section aria-labelledby> for screen readers."),
            Annotation(5, (c.device_w/2 + 200, py + 480), "§1 EVENTS textarea",
                       "--font-hand · --ink-blue",
                       "Multi-line input falls back to flat <textarea>; handwriting is visual decoration."),
            Annotation(6, (c.device_w - 90, py + 200), "§5 Right-edge tabs",
                       "--paper-stained · --paper · --amber 2px",
                       "Active state: aria-current + cutout-forward + amber underline (3 redundant cues)."),
            Annotation(7, (c.device_w - 220, c.device_h - 160), "§13 Wax-seal TRANSMIT",
                       "--ink-red · --font-typewriter --paper",
                       "Static toast 'TRANSMITTED · COPIED TO CLIPBOARD' over aria-live polite."),
        ]

    if screen == "people-front":
        if breakpoint == "mobile":
            return [
                Annotation(1, (px + 60, py + 44), "§3 Filter chips · ALIVE/FALLEN/LEGACY",
                           "--ink-brown border · --paper text on --ink-brown active",
                           "Chips are <button role=tab>; active state announced via aria-selected."),
                Annotation(2, (px + 160, py + 140), "§3 Index card",
                           "--paper · --shadow-card · --radius-md · 0.6° rotate",
                           "Whole card is the link; flat <a> fallback if rotation/shadow unsupported."),
                Annotation(3, (px + 160, py + 100), "§6 Paperclip",
                           "--amber 2.2px · ±2° rotation pinned",
                           "Decorative; <span aria-hidden=true> drops cleanly when chrome is stripped."),
                Annotation(4, (c.device_w/2, c.device_h - 80), "§7 Ribbon nav · PEOPLE active",
                           "--amber 4px marker · aria-current=page",
                           "Active item also announced; amber bar survives CSS strip."),
            ]
        if breakpoint == "tablet":
            return [
                Annotation(1, (px + 60, py + 44), "§3 Filter chips · ALIVE/FALLEN/LEGACY",
                           "--ink-brown border · 28px touch row",
                           "Chip row uses display:grid grid-auto-columns:minmax(--touch-min,1fr) for 44px floor."),
                Annotation(2, (px + 220, py + 140), "§3 Index card",
                           "--paper · --shadow-card · ±0.6°",
                           "Rotation pinned via survivorId hash so re-render doesn't jiggle."),
                Annotation(3, (px + 220, py + 320), "§3 Paperclip-clipped card",
                           "--amber clip · pointer-events: none",
                           "Clip never blocks card hit-box."),
                Annotation(4, (c.device_w - 90, py + 200), "§5 Right-edge tab · PEOPLE active",
                           "--paper fill · --amber 2px underline",
                           "Active state pairs aria-current + fill change + underline."),
            ]
        return [  # desktop
            Annotation(1, (px + 60, py + 44), "§3 Filter chips",
                       "--ink-brown border · 36px row",
                       "Chips use real <button role=tab>; aria-selected announces active filter."),
            Annotation(2, (px + 160, py + 160), "§3 Index card · alive",
                       "--paper · --shadow-card · ±0.6° pinned",
                       "Default state — name in --font-hand --ink-blue, metadata --font-mono --ink-brown."),
            Annotation(3, (c.device_w/2 - 200, py + 380), "§3 Index card · KIA",
                       "§11 KIA stamp overlay · --ink-red 8°",
                       "Stamp art is decorative; canonical status is <span>KIA · Day 11</span> in card row."),
            Annotation(4, (c.device_w - 90, py + 200), "§5 Right-edge tabs",
                       "--paper-stained inactive · --paper active",
                       "Three redundant active cues: aria-current, paper fill, amber underline."),
            Annotation(5, (px + 160, py + 80), "§6 Paperclip",
                       "--amber clip · pinned ±2° per card",
                       "Decorative; the survivor's name <h3> carries semantic group id."),
        ]

    if screen == "people-back":
        common = [
            Annotation(1, (px + 60, py + 80), "Card-back header",
                       "--font-hand --ink-blue name · --font-typewriter — TIES —",
                       "Flip is bidirectional: clicking ↺ returns to front; aria-pressed tracks face."),
            Annotation(2, (px + 220, py + 160), "§4 Tie row · PARTNER",
                       "--font-mono kind · --font-hand counterpart + label",
                       "Free-text label is the load-bearing field; kind is a coarse bucket."),
            Annotation(3, (px + 220, py + 280), "§4 Tie row · MOURNED",
                       "--ink-brown 3px left band + ' · MOURNED' text",
                       "Status text appended in plain text so screen-readers carry meaning."),
            Annotation(4, (px + 220, py + 340), "§4 Tie row · STRAINED",
                       "--ink-red zigzag underline · ' · STRAINED' text",
                       "Color is redundant; never the only signal."),
            Annotation(5, (px + 280, py + 420), "§4 + ADD TIE",
                       "--ink-brown dashed · --font-typewriter",
                       "Tap opens the inline editor (kind / label / since / status / note inputs)."),
        ]
        if breakpoint == "mobile":
            common.append(
                Annotation(6, (c.device_w/2, c.device_h - 80), "§7 Ribbon nav · PEOPLE",
                           "--amber 4px · aria-current",
                           "Card back is a stacked dialog; back-button returns to grid.")
            )
        else:
            common.append(
                Annotation(6, (c.device_w - 90, py + 200), "§5 Right-edge tabs",
                           "--paper active · --amber underline",
                           "Tabs persist across front/back faces; flip is in-place.")
            )
        return common

    if screen == "people-pencil-overlay":
        if breakpoint != "desktop":
            return [
                Annotation(1, (px + 80, py + 80), "Fallback · view collapses",
                           "--font-mono · --ink-brown",
                           "Visual web is desktop-only; ties surface via §4 card-back rows on smaller viewports."),
                Annotation(2, (px + 200, py + 200), "§4 Card-back rows · canonical",
                           "--font-mono kind · --font-hand label",
                           "Same data, different surface — no ties are hidden, only the spatial overlay."),
                Annotation(3, (px + 200, py + 320), "§3 Paperclip retained",
                           "--amber clip",
                           "Card metaphor still anchors the data; only the inter-card web is missing."),
            ]
        return [
            Annotation(1, (px + 280, py + 200), "Pencil tie · PARTNER",
                       "--ink-brown 1.2px · 0.55 opacity · curved",
                       "Tie label rendered over a --paper opacity:0.85 chip so it stays readable on any card."),
            Annotation(2, (px + 580, py + 280), "Pencil tie · MENTOR",
                       "--ink-brown · QBezier midpoint label",
                       "Curve sits above midpoint by 28px so labels don't collide."),
            Annotation(3, (px + 800, py + 380), "Pencil tie · MOURNED",
                       "--ink-red 1.2px dashed · 0.7 opacity",
                       "Mourned ties get red dashed pencil; same data also visible on KIA card-back."),
            Annotation(4, (c.device_w - 220, c.page_y + c.page_h - 70), "Legend",
                       "--paper sub-card · --font-mono",
                       "Reads even with chrome stripped; canonical tie data is on card-backs."),
            Annotation(5, (c.device_w - 90, py + 200), "§5 Right-edge tabs · PEOPLE",
                       "--paper active · --amber underline",
                       "Overlay shares the People surface; toggle hides the web cleanly."),
        ]

    if screen == "history":
        if breakpoint == "mobile":
            return [
                Annotation(1, (px + 80, py + 80), "Past day strip",
                           "--paper · --paper-stained 0.5px · --radius-sm",
                           "Tapping a strip opens that day's full page (route push, browser back returns to list)."),
                Annotation(2, (px + 280, py + 80), "§0 mood pill",
                           "--ink-blue high · --ink-brown ok · --ink-red low",
                           "Color is paired with explicit mood word — never alone."),
                Annotation(3, (px + 200, py + 280), "Stack item · KIA day",
                           "Note text plain; KIA stamp lives on People tab",
                           "History page does not re-stamp; the cross-reference stays in the survivor record."),
                Annotation(4, (c.device_w/2, c.device_h - 80), "§7 Ribbon · EVENTS",
                           "--amber 4px",
                           "EVENTS is the entry point to history on mobile."),
            ]
        if breakpoint == "tablet":
            return [
                Annotation(1, (px + 200, py + 100), "Stacked past day card",
                           "--paper · --shadow-card · ±0.6° rotate",
                           "Stack metaphor uses pinned-per-day rotation; tapping selects."),
                Annotation(2, (px + 200, py + 360), "§6 Paperclip",
                           "--amber · pointer-events:none",
                           "Decorative; the day card is the link target."),
                Annotation(3, (px + 600, py + 100), "Mood badge",
                           "--font-mono · color paired with text",
                           "Reduces to plain text on color-blind / monochrome rendering."),
                Annotation(4, (c.device_w - 90, py + 200), "§5 Right-edge tab · EVENTS",
                           "--paper active",
                           "EVENTS section persists across history detail."),
            ]
        return [
            Annotation(1, (px + 100, py + 200), "Stacked past day card",
                       "--paper · --shadow-card · pinned ±0.6°",
                       "Click expands to full detail on the right page; arrow keys cycle days."),
            Annotation(2, (c.device_w/2 - 60, py + 80), "Two-page spread · spine",
                       "--leather-shadow 8px",
                       "Lamp source is consistent with Today's page; one light source for the whole book."),
            Annotation(3, (c.device_w/2 + 60, py + 200), "Open-day detail",
                       "--paper · --font-hand --ink-blue narrative",
                       "Right page is read-only history; transmit/regenerate live in DISPATCH."),
            Annotation(4, (c.device_w/2 + 60, py + 540), "RESOURCES Δ summary",
                       "--font-mono · --ink-brown",
                       "Day-over-day deltas computed from data-model.md §2 daily snapshot."),
            Annotation(5, (c.device_w - 90, py + 200), "§5 Right-edge tabs · EVENTS active",
                       "--paper · --amber",
                       "Three redundant active cues per §0."),
        ]

    if screen == "report":
        if breakpoint == "mobile":
            return [
                Annotation(1, (px + 100, py + 80), "Mono report block",
                           "--font-mono · --ink-brown · --paper",
                           "Plain pre-formatted text; same string the clipboard receives."),
                Annotation(2, (px + 80, py + 540), "§2 COPY AS MD stamp",
                           "--ink-brown · --paper · --font-typewriter",
                           "Falls back to <button>; native browser submit on JS-off still copies via the underlying clipboard API."),
                Annotation(3, (px + 220, py + 540), "§2 TRANSMIT stamp · destructive accent",
                           "--ink-red label (not background) · --shadow-press",
                           "Per §2 destructive variants put red on label so the stamp metaphor stays."),
                Annotation(4, (c.device_w/2, c.device_h - 80), "§7 Ribbon · DISP",
                           "--amber 4px",
                           "DISP is the dispatch (report) entry point on mobile."),
            ]
        if breakpoint == "tablet":
            return [
                Annotation(1, (px + 200, py + 200), "Mono report block",
                           "--font-mono 11px · --ink-brown",
                           "Always plain pre-formatted — never decorate the report itself."),
                Annotation(2, (px + 100, py + 700), "§2 COPY AS MARKDOWN",
                           "--ink-brown · --paper · letter-spacing 2",
                           "Two-stamp footer: copy + regenerate. Real <button>s underneath."),
                Annotation(3, (px + 540, py + 700), "§13 Wax seal · TRANSMIT",
                           "--ink-red · --paper crosshair",
                           "Single dominant CTA on the page."),
                Annotation(4, (c.device_w - 90, py + 200), "§5 Tab · DISP active",
                           "--paper · --amber",
                           "DISPATCH section badge — three active cues."),
            ]
        return [
            Annotation(1, (px + 100, py + 200), "Report block · plain mono",
                       "--font-mono · --ink-brown · --paper",
                       "Output is byte-for-byte identical to the clipboard payload (auditable)."),
            Annotation(2, (px + 100, py + 720), "§2 COPY AS MARKDOWN · §2 REGENERATE",
                       "--ink-brown stamp · --font-typewriter",
                       "Regenerate re-derives the report from the day record; copy hits the clipboard API."),
            Annotation(3, (c.device_w/2 + 80, py + 80), "Share preview pane",
                       "--paper · --font-mono 0.85 opacity",
                       "Dimmed copy shows what the recipient sees — zero JS needed to read it."),
            Annotation(4, (c.device_w/2 + 80, py + 600), "§13 Wax seal · TRANSMIT",
                       "--ink-red · --shadow-press · letter-spacing 2.5",
                       "Single dominant CTA; opens the share sheet + writes to clipboard."),
            Annotation(5, (c.device_w - 90, py + 200), "§5 Tab · DISP",
                       "--paper · --amber",
                       "Active DISPATCH tab; three redundant cues."),
        ]

    if screen == "sync":
        if breakpoint == "mobile":
            return [
                Annotation(1, (px + 50, py + 60), "§8 Brass dial · CLOSED",
                           "--leather body · --amber pointer 50%",
                           "Plain readout 'Sync: off' lives beside the dial — pointer rotation is redundant cue."),
                Annotation(2, (px + 50, py + 180), "§8 Brass dial · OPEN · GIST",
                           "--amber pointer full · --leather-shadow inset",
                           "Pointer animates over --ink-bleed-duration; reduced-motion collapses to 1-frame swap."),
                Annotation(3, (px + 200, py + 280), "§9 QR telegram",
                           "--paper · --ink-brown QR · ±1° rotate",
                           "QR is decorative; <input readonly> with the share link is canonical."),
                Annotation(4, (px + 60, py + 470), "§8 Brass dial · CONFLICT halo",
                           "--ink-red 6px halo · --amber pointer",
                           "Conflict announced via role=alert text; red halo is one of two redundant cues."),
                Annotation(5, (c.device_w/2, c.device_h - 80), "§7 Ribbon · DISP",
                           "--amber 4px",
                           "Sync settings live under DISPATCH on mobile (cog item is redundant entry point)."),
            ]
        if breakpoint == "tablet":
            return [
                Annotation(1, (px + 100, py + 100), "§8 Dial · CLOSED",
                           "--leather · --amber 50%",
                           "Pointer at 12 o'clock = 'Sync: off'."),
                Annotation(2, (px + 360, py + 100), "§8 Dial · OPEN · GIST",
                           "--amber pointer · 6 o'clock",
                           "Status text 'last synced 4m ago' rendered redundantly."),
                Annotation(3, (px + 360, py + 320), "§9 QR telegram",
                           "--paper · --ink-brown · ±1°",
                           "QR + canonical <input readonly> for the share URL."),
                Annotation(4, (px + 620, py + 100), "§8 Dial · CONFLICT",
                           "--ink-red halo · --amber pointer",
                           "Conflict text in role=alert; red is paired, never alone."),
                Annotation(5, (px + 620, py + 360), "§10 Conflict spread preview",
                           "--paper · --leather-shadow spine · --ink-red 18% wash",
                           "Tap → opens full spread (modal <dialog> with KEEP LOCAL / TAKE REMOTE chips)."),
                Annotation(6, (c.device_w - 90, py + 200), "§5 Tab · DISP",
                           "--paper · --amber",
                           "Sync surface lives under DISPATCH."),
            ]
        return [
            Annotation(1, (px + 160, py + 100), "§8 Brass dial · CLOSED",
                       "--leather body · --amber pointer 50%",
                       "Always paired with a plain readout — pointer rotation is decorative."),
            Annotation(2, (px + 540, py + 100), "§8 Brass dial · OPEN · GIST",
                       "--amber pointer 100% · --leather-shadow inset",
                       "Mode change animates over --ink-bleed-duration; reduced-motion = 1-frame swap."),
            Annotation(3, (px + 540, py + 360), "§9 QR telegram",
                       "--paper · --ink-brown QR · ±1° rotate",
                       "QR encodes the same string the textarea contains, byte-for-byte."),
            Annotation(4, (px + 940, py + 100), "§8 Dial · CONFLICT halo",
                       "--ink-red 6px halo · pointer halts",
                       "Conflict announced via role=alert; halo is paired, never alone."),
            Annotation(5, (px + 940, py + 400), "§10 Conflict spread (preview)",
                       "--paper pages · --leather-shadow spine",
                       "Tap any field opens the modal spread — KEEP LOCAL / TAKE REMOTE chips at ≥44×96px."),
            Annotation(6, (c.device_w - 90, py + 200), "§5 Tab · DISP active",
                       "--paper · --amber underline",
                       "DISPATCH is the parent surface for sync settings on tablet/desktop."),
        ]

    return []


# ----------------------------------------------------------------
# Render driver
# ----------------------------------------------------------------
SCREENS = [
    ("today",                 "Today's page",                     todays_page),
    ("people-front",          "People · index-card front",        people_front),
    ("people-back",           "People · card-back · TIES",        people_back),
    ("people-pencil-overlay", "People · pencil-line overlay",     people_pencil_overlay),
    ("history",               "History · past pages",             history),
    ("report",                "Generated report · TRANSMIT",      report_panel),
    ("sync",                  "Sync radio · closed/open/conflict",sync_panel),
]
BREAKPOINTS = ["mobile", "tablet", "desktop"]


def render_one(screen: str, label: str, body_fn: Callable[[Canvas], str],
               breakpoint: str, out_dir: str) -> str:
    c = canvas_for(breakpoint)
    body = body_fn(c)
    notes = annotations_for(screen, breakpoint, c)

    bp_label = {"mobile": f"Mobile · ≤640px",
                "tablet": f"Tablet · 641–1024px",
                "desktop": f"Desktop · ≥1025px"}[breakpoint]
    title = f"PHA-348 · {label} · {bp_label}"
    subtitle = (f"viewBox {c.device_w}×{c.device_h} device + {c.w - c.rail_x}px rail · "
                f"tokens from design/tokens.css · components from design/components.md")

    svg = dedent(f"""\
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {c.w} {c.h}" width="{c.w}"
         height="{c.h}" role="img"
         aria-label="{xml_escape(title)} mockup">
      <title>{xml_escape(title)}</title>
      <desc>{xml_escape(subtitle)}</desc>
    {defs()}
      <!-- backdrop matches body chrome (leather over texture-leather) -->
      <rect x="0" y="0" width="{c.w}" height="{c.h}" fill="{LEATHER}"/>
      <rect x="0" y="0" width="{c.rail_x}" height="{c.h}" fill="url(#leatherGrain)"/>
    {book_chrome(c)}
    {body}
    {annotation_rail(c, notes)}
    {header_meta(c, title, subtitle)}
    </svg>
    """)
    path = os.path.join(out_dir, f"{screen}-{breakpoint}.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    return path


def main() -> None:
    out_dir = os.path.dirname(os.path.abspath(__file__))
    written: List[str] = []
    for screen_id, label, body_fn in SCREENS:
        for bp in BREAKPOINTS:
            written.append(render_one(screen_id, label, body_fn, bp, out_dir))
    print(f"wrote {len(written)} mockups → {out_dir}")
    for p in written:
        size = os.path.getsize(p)
        print(f"  {os.path.basename(p):40s}  {size:6d} B")


if __name__ == "__main__":
    main()
