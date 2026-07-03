from __future__ import annotations

import base64
from io import BytesIO
from typing import Any, Dict, List, Optional, Sequence, Tuple


try:
    from PIL import Image, ImageDraw, ImageFont
except Exception:  # pragma: no cover - allows app to run without Pillow installed
    Image = None  # type: ignore[assignment]
    ImageDraw = None  # type: ignore[assignment]
    ImageFont = None  # type: ignore[assignment]


RGB = Tuple[int, int, int]


def _load_font(*, size: int, bold: bool) -> Any:
    """
    Best-effort font loading:
    - On Windows, try Arial/Arial Bold.
    - Otherwise, fall back to DejaVuSans.
    - If nothing works, use Pillow's default bitmap font.
    """

    if ImageFont is None:  # pragma: no cover
        return None

    candidates: List[str] = []
    if bold:
        candidates.extend(
            [
                r"C:\Windows\Fonts\arialbd.ttf",
                r"C:\Windows\Fonts\ARIALBD.TTF",
            ]
        )
    candidates.extend(
        [
            r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\ARIAL.TTF",
            r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\SEGOEUI.TTF",
            r"/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            r"/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    )

    for p in candidates:
        try:
            return ImageFont.truetype(p, size=size)
        except Exception:
            continue

    return ImageFont.load_default()


def _text_size(draw: Any, text: str, font: Any) -> Tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def _wrap_text(
    text: str,
    *,
    draw: Any,
    font: Any,
    max_width: int,
) -> List[str]:
    """
    Wrap a string into lines that fit max_width.
    Preserves explicit newlines by inserting blank lines.
    """

    if not text:
        return []

    lines: List[str] = []
    for paragraph in text.splitlines():
        if paragraph.strip() == "":
            lines.append("")
            continue

        words = paragraph.split()
        current = ""
        for w in words:
            test = w if not current else f"{current} {w}"
            test_w, _ = _text_size(draw, test, font)
            if test_w <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = w
        if current:
            lines.append(current)
    return lines


def _font_line_height(font: Any) -> int:
    bbox = font.getbbox("Ag")
    return (bbox[3] - bbox[1]) + 6


def _legacy_roadmap_to_png_base64(
    roadmap: Dict[str, Any],
    *,
    width: int = 1100,
    background: RGB = (5, 5, 9),
    padding: int = 40,
) -> Optional[str]:
    """
    Convert roadmap text into a single PNG image and return it as base64.

    Expected `roadmap` shape:
      { "overview": str, "entries": [ { "skill": str, "project": str, "timeline": str } ] }
    """

    if Image is None or ImageDraw is None or ImageFont is None:  # pragma: no cover
        return None

    if not roadmap:
        return None

    entries_raw = roadmap.get("entries", []) or []
    if not isinstance(entries_raw, list):
        entries_raw = []
    entries: Sequence[Dict[str, Any]] = entries_raw  # type: ignore[assignment]

    # If roadmap has no steps, still render an empty (but branded) roadmap.
    n = 0
    for e in entries:
        if isinstance(e, dict):
            n += 1
    n = max(1, min(n, 10))

    # Fonts/colors (creative look; do NOT render the literal roadmap text).
    font_heading = _load_font(size=42, bold=True)
    font_subheading = _load_font(size=20, bold=False)
    font_step = _load_font(size=20, bold=True)
    font_label = _load_font(size=14, bold=False)

    bg_top: RGB = (5, 5, 9)
    bg_bottom: RGB = (10, 10, 20)
    accent_a: RGB = (99, 102, 241)  # indigo
    accent_b: RGB = (236, 72, 153)  # pink
    accent_c: RGB = (34, 211, 238)  # cyan
    text_primary: RGB = (245, 245, 255)
    text_secondary: RGB = (210, 210, 230)

    # Compute layout.
    header_h = 140
    card_h = 94
    v_gap = 28
    step_spacing = card_h + v_gap
    total_h = header_h + (n * step_spacing) + padding

    img = Image.new("RGB", (width, total_h), bg_top)
    draw = ImageDraw.Draw(img)

    # Background subtle gradient.
    for i in range(total_h):
        t = i / max(1, total_h - 1)
        r = int(bg_top[0] * (1 - t) + bg_bottom[0] * t)
        g = int(bg_top[1] * (1 - t) + bg_bottom[1] * t)
        b = int(bg_top[2] * (1 - t) + bg_bottom[2] * t)
        draw.line([(0, i), (width, i)], fill=(r, g, b))

    # Decorative blobs.
    def blob(cx: int, cy: int, rr: int, color: RGB) -> None:
        draw.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=color)

    blob(int(width * 0.12), 55, 70, (accent_a[0], accent_a[1], accent_a[2]))
    blob(int(width * 0.82), 75, 85, (accent_b[0], accent_b[1], accent_b[2]))
    # A softer overlay.
    draw.ellipse([int(width * 0.6) - 110, 10, int(width * 0.6) + 110, 230], outline=accent_c, width=6)

    # Heading.
    center_x = width // 2
    heading_y = 54
    # Put the heading centered; PIL doesn't auto-center text.
    heading = "Innovative Roadmap"
    heading_w, _ = draw.textbbox((0, 0), heading, font=font_heading)[2:]
    draw.text((center_x - heading_w // 2, heading_y), heading, fill=text_primary, font=font_heading)

    sub = f"{n} milestone steps"
    sub_w, _ = draw.textbbox((0, 0), sub, font=font_subheading)[2:]
    draw.text((center_x - sub_w // 2, heading_y + 52), sub, fill=text_secondary, font=font_subheading)

    # Timeline line.
    line_x = center_x
    line_top = header_h - 20
    line_bottom = total_h - padding - 10
    draw.line([(line_x, line_top), (line_x, line_bottom)], fill=(80, 80, 120), width=6)

    # Step cards positions.
    left_x0 = padding
    left_x1 = center_x - 24
    right_x0 = center_x + 24
    right_x1 = width - padding
    card_w_left = left_x1 - left_x0
    card_w_right = right_x1 - right_x0

    def rounded_rect(box: Tuple[int, int, int, int], fill: RGB, outline: RGB, r: int = 20) -> None:
        x0, y0, x1, y1 = box
        if hasattr(draw, "rounded_rectangle"):
            draw.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=fill, outline=outline, width=3)
        else:  # pragma: no cover
            draw.rectangle([x0, y0, x1, y1], fill=fill, outline=outline)

    def arrowhead(at_x: int, at_y: int, direction: str, color: RGB) -> None:
        # Small triangle arrow head anchored on the center line.
        size = 18
        if direction == "down":
            pts = [(at_x - size // 2, at_y - 6), (at_x + size // 2, at_y - 6), (at_x, at_y + size)]
        else:  # up
            pts = [(at_x - size // 2, at_y + 6), (at_x + size // 2, at_y + 6), (at_x, at_y - size)]
        draw.polygon(pts, fill=color)

    # Draw steps with alternating left/right cards.
    start_y = line_top + 14
    for i in range(n):
        step_y = start_y + i * step_spacing
        side_left = i % 2 == 0

        # Card styling alternates accents.
        if i % 3 == 0:
            card_fill = (22, 22, 40)
            card_outline = accent_a
            dot_color = accent_a
        elif i % 3 == 1:
            card_fill = (18, 24, 44)
            card_outline = accent_c
            dot_color = accent_c
        else:
            card_fill = (35, 18, 45)
            card_outline = accent_b
            dot_color = accent_b

        if side_left:
            card_box = (left_x0, step_y, left_x1, step_y + card_h)
            dot_center = (line_x, step_y + card_h // 2)
            # Decorative arrow from card to line.
            arrow_pts = [
                (left_x1 - 20, step_y + card_h // 2 - 14),
                (left_x1 - 20, step_y + card_h // 2 + 14),
                (left_x1 - 8, step_y + card_h // 2),
            ]
        else:
            card_box = (right_x0, step_y, right_x1, step_y + card_h)
            dot_center = (line_x, step_y + card_h // 2)
            arrow_pts = [
                (right_x0 + 20, step_y + card_h // 2 - 14),
                (right_x0 + 20, step_y + card_h // 2 + 14),
                (right_x0 + 8, step_y + card_h // 2),
            ]

        rounded_rect(
            card_box,
            fill=card_fill,
            outline=card_outline,
            r=22,
        )

        # Dot on the center line.
        dcx, dcy = dot_center
        rdot = 16
        draw.ellipse([dcx - rdot, dcy - rdot, dcx + rdot, dcy + rdot], fill=dot_color, outline=(255, 255, 255), width=2)
        # Step number inside dot.
        step_num = str(i + 1)
        num_w, num_h = draw.textbbox((0, 0), step_num, font=font_label)[2:]
        draw.text((dcx - num_w // 2, dcy - num_h // 2), step_num, fill=(0, 0, 0), font=font_label)

        # Card content (generic; not derived from resume text).
        label = "Milestone"
        action = "Build momentum"
        y_text = step_y + 18

        if side_left:
            tx = left_x0 + 22
        else:
            # right-aligned feel
            tx = right_x1 - 22

        if side_left:
            draw.text((tx, y_text), label, fill=text_secondary, font=font_label)
            draw.text((tx, y_text + 26), action, fill=text_primary, font=font_step)
        else:
            lw, _ = draw.textbbox((0, 0), label, font=font_label)[2:]
            draw.text((tx - lw, y_text), label, fill=text_secondary, font=font_label)
            aw, _ = draw.textbbox((0, 0), action, font=font_step)[2:]
            draw.text((tx - aw, y_text + 26), action, fill=text_primary, font=font_step)

        # Arrow connector.
        draw.polygon(arrow_pts, fill=card_outline)

        # Subtle arrowhead on the vertical line between steps.
        if i < n - 1:
            arrowhead(at_x=line_x, at_y=step_y + card_h + v_gap // 2, direction="down", color=card_outline)

    buf = BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def roadmap_to_png_base64(
    roadmap: Dict[str, Any],
    *,
    width: int = 867,
    height: int = 612,
    background: RGB = (255, 255, 255),
) -> Optional[str]:
    """
    Convert roadmap `overview` + `entries` into an infographic-style PNG.

    Output is intentionally driven by the roadmap *entries* (what to learn / do),
    not by generic phrases (e.g., "build momentum"), and uses a white background
    with dark text to match the reference style.
    """

    if Image is None or ImageDraw is None or ImageFont is None:  # pragma: no cover
        return None
    if not roadmap:
        return None

    entries_raw = roadmap.get("entries", []) or []
    if not isinstance(entries_raw, list):
        entries_raw = []

    cleaned_entries: List[Dict[str, str]] = []
    for e in entries_raw:
        if not isinstance(e, dict):
            continue
        skill = str(e.get("skill", "") or "").strip()
        project = str(e.get("project", "") or "").strip()
        timeline = str(e.get("timeline", "") or "").strip()
        if skill or project or timeline:
            cleaned_entries.append({"skill": skill, "project": project, "timeline": timeline})

    overview = str(roadmap.get("overview", "") or "").strip()

    # Basic fallback if the roadmap is empty
    if not cleaned_entries:
        cleaned_entries = [{"skill": "Learning", "project": overview, "timeline": ""}]

    # Fonts
    font_title_small = _load_font(size=26, bold=True)
    font_title_big = _load_font(size=58, bold=True)
    font_card_skill = _load_font(size=20, bold=True)
    font_card_delivery = _load_font(size=16, bold=True)
    font_card_meta = _load_font(size=12, bold=False)

    # Colors (dark on white)
    color_text = (12, 12, 18)
    color_muted = (72, 72, 86)
    color_border = (15, 15, 20)

    palette: List[RGB] = [
        (239, 68, 68),  # red
        (99, 102, 241),  # indigo
        (34, 211, 238),  # cyan
        (245, 158, 11),  # amber
        (236, 72, 153),  # pink
        (74, 222, 128),  # green
    ]

    img = Image.new("RGB", (width, height), background)
    draw = ImageDraw.Draw(img)

    def polyline_lengths(pts: List[Tuple[int, int]]) -> List[float]:
        segs: List[float] = [0.0]
        total = 0.0
        for i in range(1, len(pts)):
            x0, y0 = pts[i - 1]
            x1, y1 = pts[i]
            d = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
            total += d
            segs.append(total)
        return segs

    def point_at_ratio(pts: List[Tuple[int, int]], segs: List[float], ratio: float) -> Tuple[int, int]:
        if not pts or len(pts) < 2:
            return (0, 0)
        total = segs[-1]
        if total <= 0:
            return pts[0]
        t = max(0.0, min(1.0, ratio))
        target = t * total
        for i in range(1, len(segs)):
            if segs[i] >= target:
                x0, y0 = pts[i - 1]
                x1, y1 = pts[i]
                prev = segs[i - 1]
                seg_len = segs[i] - prev
                if seg_len <= 0:
                    return (x1, y1)
                local = (target - prev) / seg_len
                return (int(x0 + (x1 - x0) * local), int(y0 + (y1 - y0) * local))
        return pts[-1]

    def draw_dashed_polyline(pts: List[Tuple[int, int]], *, dash: int, gap: int, fill: RGB, width_px: int) -> None:
        segs = polyline_lengths(pts)
        total = segs[-1]
        if total <= 0:
            return
        dist = 0.0
        step = dash + gap
        while dist < total:
            p0 = point_at_ratio(pts, segs, dist / total)
            dist_end = min(total, dist + dash)
            p1 = point_at_ratio(pts, segs, dist_end / total)
            draw.line([p0, p1], fill=fill, width=width_px)
            dist += step

    def wrap_text(text: str, font: Any, max_w: int) -> List[str]:
        return _wrap_text(text, draw=draw, font=font, max_width=max_w)

    def truncate_text(text: str, font: Any, max_w: int) -> str:
        text = text or ""
        if not text:
            return ""
        # Fast path
        w, _ = _text_size(draw, text, font)
        if w <= max_w:
            return text

        # Binary-ish search by trimming
        lo, hi = 0, len(text)
        while lo < hi:
            mid = (lo + hi) // 2
            candidate = text[:mid].rstrip()
            candidate = candidate + "…" if mid < len(text) else candidate
            cw, _ = _text_size(draw, candidate, font)
            if cw <= max_w:
                lo = mid + 1
            else:
                hi = mid
        mid = max(0, lo - 1)
        candidate = text[:mid].rstrip()
        return candidate + ("…" if mid < len(text) else "")

    def draw_pin(px: int, py: int, color: RGB) -> None:
        # Teardrop-ish pin (smaller so it doesn't cover card headings).
        r = 14
        outer_cx, outer_cy = px, py - 8
        draw.ellipse(
            [outer_cx - r, outer_cy - r, outer_cx + r, outer_cy + r],
            fill=color,
            outline=(10, 10, 16),
            width=4,
        )
        draw.ellipse(
            [outer_cx - 7, outer_cy - 7, outer_cx + 7, outer_cy + 7],
            fill=background,
            outline=(10, 10, 16),
            width=3,
        )
        # stem
        draw.polygon(
            [(px - 7, py + 3), (px + 7, py + 3), (px, py + 22)],
            fill=color,
            outline=(10, 10, 16),
        )
        draw.line([(px, py + 18), (px, py + 24)], fill=color, width=6)

    def draw_card(x0: int, y0: int, w: int, entry: Dict[str, str], accent: RGB) -> None:
        """
        Render only headings (no descriptions):
        - Skill (heading)
        - Optional timeline label
        """
        card_r = 14
        bar_h = 8
        if hasattr(draw, "rounded_rectangle"):
            draw.rounded_rectangle([x0, y0, x0 + w, y0 + 110], radius=card_r, fill=(255, 255, 255), outline=color_border, width=2)
            draw.rounded_rectangle([x0, y0, x0 + w, y0 + bar_h], radius=card_r, fill=accent)
        else:  # pragma: no cover
            draw.rectangle([x0, y0, x0 + w, y0 + 110], fill=(255, 255, 255), outline=color_border)
            draw.rectangle([x0, y0, x0 + w, y0 + bar_h], fill=accent)

        pad = 14
        max_text_w = w - pad * 2
        ty = y0 + bar_h + 14
        tx = x0 + pad

        skill = str(entry.get("skill", "") or "").strip()
        timeline = str(entry.get("timeline", "") or "").strip()

        if skill:
            skill_lines = wrap_text(skill, font_card_skill, max_text_w)[:2]
            for ln in skill_lines:
                draw.text((tx, ty), ln, fill=color_text, font=font_card_skill)
                ty += 26

        if timeline:
            # Timeline is a short label; render as a single line.
            tline = truncate_text(timeline, font_card_meta, max_text_w)
            if tline:
                ty += 2
                draw.text((tx, ty), tline, fill=(90, 90, 105), font=font_card_meta)

    # Header
    first_skill = str(cleaned_entries[0].get("skill", "") or "").strip() or "Learning"
    subtitle = first_skill.upper()
    # Wrap into at most 2 lines without overly long strings.
    subtitle_words = subtitle.split()
    line1: str = " ".join(subtitle_words[:2]) if subtitle_words else subtitle
    line2: str = " ".join(subtitle_words[2:4]) if len(subtitle_words) > 2 else ""
    subtitle_lines = [line1] + ([line2] if line2 else [])
    if not subtitle_lines or subtitle_lines == [""]:
        subtitle_lines = ["LEARNING"]

    draw.text((70, 62), "ROADMAP", fill=color_text, font=font_title_small)
    base_y = 118
    for i, line in enumerate(subtitle_lines[:2]):
        draw.text((70, base_y + i * 56), line, fill=color_text, font=font_title_big)

    # Keep the image focused on concrete steps (skills/projects/timelines).
    # We intentionally do not render the `overview` text inside the infographic
    # because it may contain generic phrasing.

    # Path
    path_pts: List[Tuple[int, int]] = [
        (110, 470),
        (200, 535),
        (280, 475),
        (320, 390),
        (420, 320),
        (520, 290),
        (600, 330),
        (655, 410),
        (760, 420),
        (820, 340),
    ]
    draw.line(path_pts, fill=(0, 0, 0), width=20)
    draw_dashed_polyline(path_pts, dash=12, gap=10, fill=(240, 240, 240), width_px=5)

    # Steps
    step_count = min(4, len(cleaned_entries))
    segs = polyline_lengths(path_pts)
    ratios = [(i + 1) / (step_count + 1) for i in range(step_count)]

    half = width // 2
    left_x0, left_w = 42, half - 64
    right_x0, right_w = half + 22, width - (half + 44)

    card_h = 112  # compact and aligned
    top_safe = 220
    bottom_safe = height - 14 - card_h

    # Compute pin anchors first, then sort top-to-bottom for stable layout.
    pins: List[Dict[str, Any]] = []
    for i in range(step_count):
        pin_x, pin_y = point_at_ratio(path_pts, segs, ratios[i])
        pins.append({"pin_x": pin_x, "pin_y": pin_y, "entry_index": i})
    pins.sort(key=lambda p: p["pin_y"])

    prev_y_left: int | None = None
    prev_y_right: int | None = None

    for k, p in enumerate(pins):
        entry = cleaned_entries[p["entry_index"]]
        accent = palette[p["entry_index"] % len(palette)]
        pin_x, pin_y = int(p["pin_x"]), int(p["pin_y"])

        side_left = (k % 2 == 0)
        x0 = left_x0 if side_left else right_x0
        w = left_w if side_left else right_w

        # Cards go BELOW the pin so the pin is always visible.
        desired_y0 = pin_y + 10
        y0 = max(top_safe, min(bottom_safe, desired_y0))

        # Avoid overlap on the same side (two cards per side max).
        if side_left and prev_y_left is not None:
            y0 = max(y0, prev_y_left + card_h + 14)
            y0 = min(y0, bottom_safe)
        if (not side_left) and prev_y_right is not None:
            y0 = max(y0, prev_y_right + card_h + 14)
            y0 = min(y0, bottom_safe)

        if side_left:
            prev_y_left = y0
        else:
            prev_y_right = y0

        # Connector: short line from pin to card bar.
        bar_center_x = x0 + w // 2
        draw.line([(pin_x, pin_y + 4), (bar_center_x, y0 + 6)], fill=(0, 0, 0), width=3)

        # Draw card then pin so the pin stays visible.
        draw_card(x0, y0, w, entry, accent)
        draw_pin(pin_x, pin_y, accent)

    # If there are more steps, we intentionally don't render extra text
    # to keep the infographic clean.

    buf = BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode("ascii")


__all__ = ["roadmap_to_png_base64"]

