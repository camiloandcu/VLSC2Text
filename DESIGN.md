---
name: Seña a seña
description: Practice app for five Colombian Sign Language signs, read from two metres away, with a metro line as its progress.
colors:
  ground: "#f6f7f4"
  card: "#ffffff"
  ink: "#0f2a44"
  ink-soft: "#4a5b6d"
  line: "#d9ddd6"
  line-soft: "#eceee9"
  stage: "#1a232d"
  go: "#1d7f74"
  go-hover: "#186c63"
  go-soft: "#dff1ed"
  warn: "#c98708"
  warn-soft: "#fff4da"
  warn-ink: "#573900"
  doubt: "#5b6b82"
  doubt-soft: "#eceff4"
  rec: "#e5484d"
  guide-hand: "#8fd0c4"
  guide-caption: "#d6e6f5"
typography:
  display:
    fontFamily: "Figtree, system-ui, Segoe UI, Roboto, Arial, sans-serif"
    fontSize: "clamp(32px, 8vw, 44px)"
    fontWeight: 800
    lineHeight: 1.05
    letterSpacing: "-0.025em"
  score:
    fontFamily: "Figtree, system-ui, sans-serif"
    fontSize: "72px"
    fontWeight: 800
    lineHeight: 1
    letterSpacing: "-0.03em"
    fontFeature: "tnum"
  headline:
    fontFamily: "Figtree, system-ui, sans-serif"
    fontSize: "clamp(30px, 9vw, 40px)"
    fontWeight: 800
    lineHeight: 1.05
    letterSpacing: "-0.02em"
  message-title:
    fontFamily: "Figtree, system-ui, sans-serif"
    fontSize: "30px"
    fontWeight: 800
    lineHeight: 1.1
  message-body:
    fontFamily: "Figtree, system-ui, sans-serif"
    fontSize: "22px"
    fontWeight: 700
    lineHeight: 1.2
  title:
    fontFamily: "Figtree, system-ui, sans-serif"
    fontSize: "18px"
    fontWeight: 600
    lineHeight: 1.4
  body:
    fontFamily: "Figtree, system-ui, Segoe UI, Roboto, Arial, sans-serif"
    fontSize: "16px"
    fontWeight: 500
    lineHeight: 1.4
  label:
    fontFamily: "Figtree, system-ui, sans-serif"
    fontSize: "14px"
    fontWeight: 800
    lineHeight: 1.2
rounded:
  station-terminal: "8px"
  sm: "12px"
  md: "16px"
  lg: "18px"
  xl: "22px"
  full: "999px"
spacing:
  xs: "8px"
  sm: "12px"
  md: "16px"
  lg: "22px"
  xl: "28px"
components:
  button-primary:
    backgroundColor: "{colors.go}"
    textColor: "{colors.card}"
    typography: "{typography.body}"
    rounded: "{rounded.md}"
    padding: "0 18px"
    height: "52px"
  button-primary-hover:
    backgroundColor: "{colors.go-hover}"
  button-ghost:
    backgroundColor: "{colors.card}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: "0 18px"
    height: "52px"
  button-ghost-off:
    backgroundColor: "{colors.line-soft}"
    textColor: "{colors.ink-soft}"
  icon-button:
    backgroundColor: "{colors.line-soft}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    size: "40px"
  message-idle:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.card}"
    typography: "{typography.message-title}"
    rounded: "{rounded.lg}"
    padding: "14px 16px"
  message-ok:
    backgroundColor: "{colors.go}"
    textColor: "{colors.card}"
  message-try:
    backgroundColor: "{colors.warn-soft}"
    textColor: "{colors.warn-ink}"
  message-doubt:
    backgroundColor: "{colors.doubt-soft}"
    textColor: "{colors.ink}"
  station:
    backgroundColor: "{colors.card}"
    textColor: "{colors.ink}"
    rounded: "{rounded.full}"
    size: "24px"
  station-current:
    backgroundColor: "{colors.card}"
    size: "34px"
  station-done:
    backgroundColor: "{colors.go}"
    textColor: "{colors.card}"
  station-terminal:
    backgroundColor: "{colors.card}"
    rounded: "{rounded.station-terminal}"
    size: "28px"
  camera-stage:
    backgroundColor: "{colors.stage}"
    rounded: "{rounded.xl}"
  guide-inset:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.guide-caption}"
    rounded: "{rounded.md}"
    width: "44%"
  chip-status:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.card}"
    rounded: "{rounded.full}"
    padding: "7px 12px"
  chip-rec:
    backgroundColor: "{colors.rec}"
    textColor: "{colors.card}"
  score-list:
    backgroundColor: "{colors.card}"
    textColor: "{colors.ink}"
    rounded: "{rounded.lg}"
    padding: "14px 16px"
---

# Design System: Seña a seña

## Overview

**Creative North Star: "The Day Line"**

A learning app laid over a metro line. Progress is a line of five round stations on a midnight-ink track with one square transfer terminal for the review; every screen keeps the conventional learning-app skeleton (progress at the top, the sign name, the camera, one large message, the action at the foot). The world is a light daytime ground with midnight-ink type, controls and track, and colour reserved for state: teal means progress and success, amber means almost or fix your framing, blue slate means not sure, red means recording. Each state paints the same three places at once (the camera ring, the current station and the message band), so the person sees what happened from two metres away without reading.

Density is low and type is large because the phone sits on a shelf while both hands are busy. The camera takes every pixel left over; the sign guide is a skeleton animation in a dark ink inset, never a person's video. The brand name appears only at the two ends of the journey (intro and result); the practice screen carries no header. Copy is warm, everyday neutral Colombian Spanish, and the technical side shrinks to one privacy line.

The build rejects a generic progress bar and per-sign colour coding (replaced by state colours at the user's request).

**Key Characteristics:**
- Light day ground, midnight-ink type, track and controls; colour reserved for state.
- One state, three surfaces: camera ring, current station, message band.
- Metro line progress: round white stations with heavy ink strokes, teal fill with a check when done, square transfer terminal for the review.
- Message band floating over the camera in 30 px or larger type.
- Figtree, self-hosted, weights 500 to 800; single-stroke SVG icons.
- Brand header only on the intro and result screens.

## Colors

A quiet daylight palette of paper and midnight ink, with four state hues that only ever speak about the attempt in progress.

### Primary
- **Station Teal** (go): progress and success. Primary buttons, completed stations and travelled track, the success camera ring and message band, the focus outline, the score numeral and hit dots. Hover deepens to **Deep Station Teal** (go-hover).
- **Pale Teal Mist** (go-soft): the intro framing diagram's backdrop and text selection.

### Secondary
- **Signal Amber** (warn): "Casi" and every framing warning. Paints the camera ring, the current station's stroke and halo, the message icon disc and missed-sign dots on the result list.
- **Amber Wash** (warn-soft) with **Amber Earth** (warn-ink): the amber message band's surface and text, and the missed-sign note colour.

### Tertiary
- **Blue Slate** (doubt) with **Slate Wash** (doubt-soft): "No estoy seguro". Slate ring, slate station stroke, slate message band with ink text.
- **Recording Red** (rec): recording only. Camera ring and the "Grabando" chip with its pulsing dot; it never appears as a message band.

### Neutral
- **Day Ground** (ground): page background and the browser theme colour.
- **Paper White** (card): ghost buttons, score list, side notes, hint sheet, station interiors.
- **Midnight Ink** (ink): all headings and body text, the track, unvisited station strokes, the idle message band, the guide inset, step numerals.
- **Slate Ink** (ink-soft): secondary copy, the key cue under the sign name, labels of non-current stations, privacy line.
- **Rule Grey** (line) and **Faint Rule** (line-soft): the inset stroke of ghost buttons, list dividers, icon-button and pressed-off toggle fills.
- **Camera Dark** (stage): the camera well behind the video.
- **Guide Mint** (guide-hand) with white: the two skeleton hands, one white and one mint; the pose is drawn in near-white, face contours at 45% white. **Guide Caption Blue** (guide-caption) labels the guide inset.

### Named Rules
**The Three Places Rule.** A state colour is set once (on the stage and body `data-state`) and paints the camera ring, the current station and the message band together. A state that only paints one place is a bug.

**The Amber Owns Framing Rule.** Framing problems (too close, too far, off centre, hands out of view) speak in the amber message band, the same voice as "Casi". The neutral ink chip is for passive status only.

**The Ink Until Earned Rule.** Track and stations are ink until the sign is achieved; teal is earned, never decorative.

## Typography

**Display Font:** Figtree (with system-ui, Segoe UI, Roboto, Arial, sans-serif), self-hosted variable woff2 (weights 300 to 900, latin and latin-ext) from `demo/static/fonts`.

**Character:** One friendly geometric sans across every role, carried by weight rather than by a second family. Headlines sit at 800 with tight negative tracking; reading copy at 500 to 600.

### Hierarchy
- **Display** (800, clamp 32 to 44 px, 1.05): the intro title, balanced wrap. The result title uses a smaller clamp (26 to 34 px).
- **Score** (800, 72 px, 1, tabular numerals): the single result number in teal, followed by "de 5" at 24 px 700 in slate ink.
- **Headline** (800, clamp 30 to 40 px on phones, 46 px on desktop, 1.05): the sign name at the top of the practice screen, set plain (no quotes) because it stands alone.
- **Message title** (800, 30 px phone, 34 px desktop, 1.1) and **Message body** (700, 22 px phone, 24 px desktop, 1.2): the band over the camera. A 16 px 600 small line may follow with the secondary note.
- **Title** (600, 18 px phone, 20 px desktop): the key cue under the sign name, in slate ink.
- **Body** (500, 16 px, 1.4): default text. Intro copy at 17 px in slate ink, max 40ch. Hints and score rows at 17 px.
- **Label** (800, 14 px): the current station's name. Other station labels (desktop only) 13.5 px 700 slate ink. Chips 13.5 px 700; captions 12.5 px 700.

### Named Rules
**The Two Metre Rule.** Anything the person must read during an attempt (message title and line, sign name, current station) stays at or above the sizes above. Never shrink the message band to fit more words; cut words.

**The Quoted Sign Rule.** Sign names inside running copy are wrapped in Spanish angle quotes («Café», «Ver guía»).

## Layout

Phone first, portrait. The practice screen is a single-column grid of four rows (top line, lesson, stage, foot) filling `100dvh`, with the stage taking the remaining height (`minmax(0, 1fr)`) and safe-area insets honoured top and bottom. The line spans the full width with 16 px side padding; the lesson block sits 20 px in; the stage and foot sit 12 px from the edges. On phones only the current station shows its name, centred under it.

At 980 px and wider the grid becomes two columns: the stage on the left (fluid) and a 400 px side column holding the lesson, the guide, hints and the foot actions, with 28 px gutters. The top row shows a "Seña N de 5" counter left of the line and every station's label. The corner guide inset disappears and the guide moves into the side column.

Intro and result are a centred single column (460 px max, 520 px on desktop) with an 18 px gap and actions pinned to the bottom with `margin-top: auto`.

Spacing rhythm: 8, 12, 16, 22 and 28 px, with 10, 14 and 18 px as in-component steps. Touch targets are at least 52 px tall for buttons and 36 px for stations.

## Elevation & Depth

Flat at rest on the page. Depth exists only over the camera: elements that float on the live video (guide inset, message band, hint sheet) carry soft dark ambient shadows so they separate from a busy image. Halos around the current station are flat rings in the state colour at about 20% opacity, not shadows.

### Shadow Vocabulary
- **Floating inset** (`box-shadow: 0 8px 18px rgba(0,0,0,.25)`): the guide inset over the camera.
- **Floating band** (`box-shadow: 0 10px 24px rgba(0,0,0,.22)`): the message band.
- **Floating sheet** (`box-shadow: 0 14px 30px rgba(0,0,0,.3)`): the hint sheet over the camera.
- **State ring** (`box-shadow: inset 0 0 0 5px <state colour>`, 6 px on desktop): the camera border, drawn inside the stage.
- **Station halo** (`box-shadow: 0 0 0 6px <state colour at ~.2>`): the current station.

### Named Rules
**The Shadows Only Over Video Rule.** Nothing on the day ground casts a shadow; only layers floating over the camera do.

## Shapes

Soft, friendly rounding sized to the element: 22 px for the camera stage and intro diagram, 18 px for the message band, score list and hint sheet, 16 px for buttons and the guide inset, 12 px for icon buttons and desktop hint rows. Stations, step numerals, score dots and chips are full circles or pills. The one deliberate square is the review terminal (8 px corners, double inset stroke), the transfer station that ends the line. Ghost buttons draw their edge as a 2 px inset stroke rather than a border.

## Components

### Buttons
Tactile and plain: tall, rounded, heavy labels with a single-stroke icon.
- **Shape:** gently rounded (16 px), 52 px minimum height, 18 px side padding, 8 px icon gap, 800 weight at 16 px.
- **Primary:** Station Teal with white text; one per screen, the forward action ("Empezar", "Siguiente seña", "Practicar"). Hover deepens to Deep Station Teal.
- **Ghost:** Paper White with ink text and a 2 px Rule Grey inset stroke, darkening on hover. Toggles show off state with Faint Rule fill and slate text (`aria-pressed="false"`), and their label states the setting ("Esqueleto sobre tu imagen: sí").
- **Compact:** the ghost button sized to content for secondary foot tools ("Grabar en 3 s", "Esqueleto").
- **Press / Focus:** press scales to 0.97 over 150 ms; focus is a 3 px teal outline offset 3 px. Disabled drops to 50% opacity.
- **Icon button:** 40 px square, 12 px radius, Faint Rule fill, used to close the hint sheet; always carries an `aria-label`.

### Chips
- **Status chip:** ink pill at 88% opacity in the camera's top right corner, white 13.5 px text with an icon, for passive status.
- **Recording chip:** red pill with a white dot pulsing once a second, shown only while the attempt is actually being captured.

### Cards / Containers
- **Score list:** Paper White, 18 px radius, rows 14 by 16 px with 1 px Faint Rule dividers; each row has a 28 px dot with a white single-stroke icon (teal with a check for a hit, amber with a retry arrow for a miss) and a right-aligned note ("a la primera", "practícala").
- **Side note and hint rows (desktop):** Paper White, 12 to 16 px radius, no border, no shadow.

### Navigation
The metro line is the only navigation: each station is a button that opens its lesson; the terminal opens the review. Labels are hidden on phones except for the current station.

### Metro Line (signature)
Six stations joined by a 6 px track. Unvisited track and stations are ink: white 24 px discs with a 5 px ink stroke. A completed station fills teal with a white check, and the track leading into a completed or current station turns teal. The current station grows to 34 px with a white interior, a stroke in the current state colour (teal by default, amber for "casi", slate for doubt) and a 6 px halo. The review terminal is a 28 px rounded square with a double inset stroke; when all five are done its strokes swap to teal and white. Colour changes ease over 300 to 500 ms.

### Camera Stage and Message Band (signature)
The stage is a Camera Dark well (22 px radius) with the mirrored video and skeleton overlay. Its inset ring takes the state colour. The message band floats 12 px from the bottom on phones (centred, max 560 px wide, 20 px from the bottom on desktop): a 44 px icon disc and a title, line and optional small note. Variants: ink (idle and preparing), teal (logro), amber wash with amber earth text and an amber icon disc (casi and framing), slate wash with ink text and a slate icon disc (no estoy seguro). It hides by fading and sliding 12 px down while recording.

### Sign Guide
A skeleton animation on a midnight-ink panel labelled "Así se hace": a 44% wide inset (max 172 px) in the stage's top left corner on phones, a panel in the side column on desktop. One hand is drawn white and the other Guide Mint, with the pose in near-white and faint face contours. It hides during the review unless the person asks for it.

### Intro Framing Diagram
A flat SVG on Pale Teal Mist: an ink phone, a dashed mint frame, a white stick figure with mint elbow dots, and ink callouts naming «cintura» and «codos». It teaches framing before the camera opens.

## Do's and Don'ts

### Do:
- **Do** paint every state in its three places at once: camera ring, current station, message band.
- **Do** route framing warnings through the amber message band, the same as "Casi".
- **Do** keep the message title at 30 px or more on phones (34 px desktop) and its line at 22 px or more.
- **Do** use one teal primary button per screen at the foot; everything else is ghost.
- **Do** draw icons as single-stroke inline SVG (2.4 stroke, round caps and joins, `currentColor`).
- **Do** write copy in natural, neutral Colombian Spanish and quote sign names with « ».
- **Do** keep the brand header to the intro and result screens.
- **Do** honour `prefers-reduced-motion` for everything except the guide animation itself.

### Don't:
- **Don't** use a generic progress bar; progress is the metro line with the review as its terminal.
- **Don't** assign colours per sign; colour belongs to state.
- **Don't** use red for anything but recording.
- **Don't** add kicker or eyebrow labels above titles.
- **Don't** put em dashes, en dashes or middle dots in copy.
- **Don't** show signers' faces or video in the guide; the guide is a skeleton.
- **Don't** cast shadows on the day ground; depth is for layers over the camera.
- **Don't** use emoji or icon fonts for icons.
