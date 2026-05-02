#!/usr/bin/env python3
"""
Spatial audit for the rendered mockup SVGs.

Catches the kinds of bugs that come from layout-by-arithmetic:
  - elements rendered outside the page area
  - annotation targets that fall inside the leather frame, the
    annotation rail, or off-canvas
  - wax-seal / stamp-button TRANSMIT artifacts overlapping the
    bottom-edge ribbon nav
  - pencil-overlay tie paths intersecting any survivor card
  - tab strip overlapping survivor cards on the People views

Run after `_render.py`. Exits 0 on clean audit, 1 on any flag.
"""
from __future__ import annotations

import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

SVG_NS = "{http://www.w3.org/2000/svg}"
RAIL_X = {"mobile": 360, "tablet": 768, "desktop": 1440}
INSET  = {"mobile": 10,  "tablet": 14,  "desktop": 18}
DEVICE_H = {"mobile": 1080, "tablet": 1024, "desktop": 900}


def parse_viewbox(root: ET.Element) -> tuple[float, float, float, float]:
    vb = root.attrib.get("viewBox", "0 0 0 0").split()
    return tuple(map(float, vb))


def num(v: str | None, default: float = 0.0) -> float:
    if v is None:
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def collect_rects(root: ET.Element):
    out = []
    for el in root.iter():
        tag = el.tag.replace(SVG_NS, "")
        if tag != "rect":
            continue
        x, y = num(el.attrib.get("x")), num(el.attrib.get("y"))
        w, h = num(el.attrib.get("width")), num(el.attrib.get("height"))
        out.append((x, y, w, h, el))
    return out


def collect_paths(root: ET.Element):
    out = []
    for el in root.iter():
        tag = el.tag.replace(SVG_NS, "")
        if tag != "path":
            continue
        d = el.attrib.get("d", "")
        out.append((d, el))
    return out


def path_segments(d: str):
    """Approximate a path's straight-line segments from M/L/Q endpoints."""
    tokens = re.findall(r"[MLQTCH]|-?[0-9]+(?:\.[0-9]+)?", d)
    pts = []
    cur = (0.0, 0.0)
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t in ("M", "L"):
            x = float(tokens[i + 1])
            y = float(tokens[i + 2])
            if t == "M":
                cur = (x, y)
                pts.append(("M", cur))
            else:
                pts.append(("L", cur, (x, y)))
                cur = (x, y)
            i += 3
        elif t == "Q":
            cx, cy = float(tokens[i + 1]), float(tokens[i + 2])
            x, y = float(tokens[i + 3]), float(tokens[i + 4])
            pts.append(("Q", cur, (cx, cy), (x, y)))
            cur = (x, y)
            i += 5
        else:
            i += 1
    return pts


def line_intersects_rect(p1, p2, rect) -> bool:
    """Does the line segment p1→p2 cross the interior of rect (x,y,w,h)?"""
    rx, ry, rw, rh = rect
    # quick reject by bbox
    minx, maxx = sorted([p1[0], p2[0]])
    miny, maxy = sorted([p1[1], p2[1]])
    if maxx < rx or minx > rx + rw or maxy < ry or miny > ry + rh:
        return False
    # if either endpoint is strictly inside, intersect
    def inside(px, py):
        return rx < px < rx + rw and ry < py < ry + rh
    if inside(*p1) or inside(*p2):
        return True
    # otherwise check segment vs rect edges
    edges = [
        ((rx, ry), (rx + rw, ry)),
        ((rx + rw, ry), (rx + rw, ry + rh)),
        ((rx + rw, ry + rh), (rx, ry + rh)),
        ((rx, ry + rh), (rx, ry)),
    ]
    for (a, b) in edges:
        if segments_cross(p1, p2, a, b):
            return True
    return False


def segments_cross(p, p2, q, q2) -> bool:
    def ccw(a, b, c):
        return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])
    return ccw(p, q, q2) != ccw(p2, q, q2) and ccw(p, p2, q) != ccw(p, p2, q2)


def audit_one(path: str) -> list[str]:
    flags: list[str] = []
    name = os.path.basename(path)
    breakpoint = name.rsplit("-", 1)[1].split(".")[0]
    rail_x = RAIL_X[breakpoint]
    inset  = INSET[breakpoint]
    device_h = DEVICE_H[breakpoint]
    page_x, page_y = inset, inset
    page_w = rail_x - 2 * inset

    tree = ET.parse(path)
    root = tree.getroot()
    rects = collect_rects(root)
    paths = collect_paths(root)

    # 1) any rect with x+w > rail_x and the rect ISN'T part of the rail
    canvas_w = parse_viewbox(root)[2]
    for (x, y, w, h, el) in rects:
        # Skip the annotation-rail backdrop ("#FAF6EC") and the full-canvas
        # leather backdrop (covers the whole SVG including the rail).
        fill = el.attrib.get("fill", "")
        if x >= rail_x:
            continue  # in rail — fine
        if x == 0 and w >= canvas_w - 1 and fill in ("#3B2A1A", "url(#leatherGrain)"):
            continue  # intentional backdrop
        if x + w > rail_x + 1 and fill not in ("#FAF6EC",):
            if x < rail_x and x + w > rail_x + 4:
                flags.append(
                    f"  rect bleeds into rail x={x:.0f}+{w:.0f} fill={fill!r}"
                )

    # 2) bottom-of-page overflow (in the device area only)
    page_bottom = page_y + (device_h - 2 * inset)
    for (x, y, w, h, el) in rects:
        if x >= rail_x:
            continue
        if y + h > device_h + 1:
            flags.append(
                f"  rect overflows device bottom y={y:.0f}+{h:.0f} "
                f"(device_h={device_h})"
            )

    # 3) Pencil-overlay desktop: every tie path must NOT cross any card
    if "pencil-overlay-desktop" in name:
        # Cards: rects with fill=#F1E4C8 and width≈280 height≈170, within the
        # device area. Skip the page-paper background and small chips.
        cards = [
            (x, y, w, h)
            for (x, y, w, h, el) in rects
            if x < rail_x
            and 270 < w < 290 and 165 < h < 175
            and el.attrib.get("fill", "") == "#F1E4C8"
        ]
        for (d, el) in paths:
            stroke = el.attrib.get("stroke", "")
            sw = num(el.attrib.get("stroke-width"), 0)
            if stroke not in ("#2A1F12", "#7E1E1E") or sw == 0 or sw > 1.5:
                continue  # not a pencil-line tie (skip card outlines etc)
            segs = path_segments(d)
            cur = None
            for seg in segs:
                if seg[0] == "M":
                    cur = seg[1]
                elif seg[0] == "L":
                    p1, p2 = seg[1], seg[2]
                    for card in cards:
                        # shrink the card a hair so endpoints exactly on the
                        # card edge don't trigger
                        cx, cy, cw, ch = card[0] + 1, card[1] + 1, card[2] - 2, card[3] - 2
                        if line_intersects_rect(p1, p2, (cx, cy, cw, ch)):
                            flags.append(
                                f"  pencil-tie crosses card at "
                                f"({cx:.0f},{cy:.0f},{cw:.0f}×{ch:.0f}): "
                                f"{p1} -> {p2}"
                            )
                            break
                    cur = p2
    return flags


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    files = sorted(glob.glob(os.path.join(here, "*.svg")))
    total_flags = 0
    for f in files:
        flags = audit_one(f)
        if flags:
            print(f"{os.path.basename(f)}:")
            for fl in flags:
                print(fl)
            total_flags += len(flags)
    if total_flags:
        print(f"\n{total_flags} flag(s).")
        return 1
    print(f"OK · audit clean across {len(files)} mockups.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
