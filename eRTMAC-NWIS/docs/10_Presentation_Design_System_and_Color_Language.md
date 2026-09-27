# 10. Presentation Design System & Color Language Specification
## Official Design System for eRTMAC-NWIS Pitch Deck
### Theme: "Assam Crude & Industrial Amber" (Confirmed Selection)

---

## 1. Selected Palette & Tokens

This color language directly mirrors **Oil India Limited's (OIL)** corporate gravitas, the lush geography of the Upper Assam Valley, and the physical reality of upstream crude oil exploration. It retains the exact visual contrast and hierarchical structure of the benchmark winning deck (`sih26188.pptx` / Team Lumora archetype).

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              OFFICIAL COLOR PALETTE TOKENS                             │
├───────────────────────┬───────────┬───────────────┬────────────────────────────────────┤
│ Token Name            │ Hex Code  │ RGB Values    │ UI / Slide Role                    │
├───────────────────────┼───────────┼───────────────┼────────────────────────────────────┤
│ **Pine Green (Brand)**│ `#184E3A` │ (24, 78, 58)  │ Primary slide titles, section      │
│                       │           │               │ headers, checkmarks, trust badges. │
├───────────────────────┼───────────┼───────────────┼────────────────────────────────────┤
│ **Petroleum Amber**   │ `#E58A13` │ (229, 138, 19)│ Numbered badges (1, 2, 3, 4),      │
│                       │           │               │ metric highlights, alert cards.    │
├───────────────────────┼───────────┼───────────────┼────────────────────────────────────┤
│ **Charcoal Slate**    │ `#1E242B` │ (30, 36, 43)  │ Container card borders, technical  │
│                       │           │               │ diagram frames, dark accents.      │
├───────────────────────┼───────────┼───────────────┼────────────────────────────────────┤
│ **Canvas Surface**    │ `#FFFFFF` │ (255, 255, 255│ Slide background base.             │
├───────────────────────┼───────────┼───────────────┼────────────────────────────────────┤
│ **Card Container Fill**│ `#F8F9FA`│ (248, 249, 250│ Rounded card backgrounds.          │
├───────────────────────┼───────────┼───────────────┼────────────────────────────────────┤
│ **Text Title**        │ `#0D1117` │ (13, 17, 23)  │ High-contrast card headlines.      │
├───────────────────────┼───────────┼───────────────┼────────────────────────────────────┤
│ **Text Body**         │ `#4A5568` │ (74, 85, 104) │ Subtitles, descriptions, captions. │
├───────────────────────┼───────────┼───────────────┼────────────────────────────────────┤
│ **Critical Red Alert**│ `#D9381E` │ (217, 56, 30) │ Stuck pipe / blowout hazard tags.  │
└───────────────────────┴───────────┴───────────────┴────────────────────────────────────┘
```

---

## 2. Slide-by-Slide Component Styling Rules

### Slide 1: Title & Team Credentials
*   **Header Banner:** Text in `#184E3A` (Pine Green).
*   **Team & PS Metadata Card:** Left rounded container with `#1E242B` border, text in `#0D1117`, labels in `#4A5568`.
*   **SIH Lightbulb Logo:** Green (`#184E3A`) and Saffron/Amber (`#E58A13`) dual-filament motif.

### Slide 2: Problem & Solution Breakdown
*   **Left Problem Card:** Thick border in `#184E3A` with `#F8F9FA` fill; Warning icons in `#E58A13` and `#D9381E`.
*   **Center 4 Solution Cards:** Thin `#E58A13` and `#184E3A` borders, clean vector icons, bold headers in `#0D1117`.
*   **Right "Different? One of a Kind" Badges:** 4 large filled circles in `#E58A13` with white numbers (`1`, `2`, `3`, `4`), accompanied by bold title and description.

### Slide 3: Technical Architecture & Implementation
*   **Data Pipeline Boxes:** Rounded cards with `#1E242B` stroke and `#F8F9FA` fill.
*   **Connective Arrows:** Stroke in `#184E3A` with directional arrowheads.
*   **Right Side "Sovereign Tech Stack" Card:** Dark slate container (`#1E242B`) with amber highlights (`#E58A13`).

### Slide 4: Overcoming Hurdles & Feasibility Analysis
*   **Stakeholder Table:** Alternating rows with `#F8F9FA` and `#FFFFFF`; stakeholder role badges in `#E58A13`; solution checkmarks in `#184E3A`.
*   **Right Feasibility Pillars (3 Containers):** Framed in `#184E3A` with circular icon badges in `#E58A13`.

### Slide 5: How We Make a Change & Big Metrics
*   **3 Big Metric Highlight Bubbles:** Filled circles in `#E58A13` (Amber) with bold white metric text:
    *   **Bubble 1:** `₹25L/hr` *(NPT Cost Saved)*
    *   **Bubble 2:** `<15ms` *(Spatial Query Latency)*
    *   **Bubble 3:** `100%` *(Air-Gapped / Offline-Ready)*
*   **4 Core Innovation Cards:** Rounded rectangles with `#184E3A` headers and `#E58A13` accent tabs.
*   **Bottom Social vs Economic Matrix:** Dual-card container comparing community protection vs PSU savings.

### Slide 6: Research & References
*   **6 Citation Blocks:** Light `#F8F9FA` cards with `#184E3A` circular numbering icons and bold publication titles.

---

## 3. Typography & Spacing Standard
*   **Slide Dimension:** Standard 16:9 widescreen ($13.333'' \times 7.5''$ / $1920 \times 1080$ px).
*   **Primary Font:** `Arial` or `Segoe UI` (Universally installed across all Windows/Mac systems; prevents PPT layout shift during live evaluation).
*   **Card Corner Radius:** $12\text{ pt}$ ($152,400\text{ EMU}$) for modern, polished rounded corners.
*   **Card Border Stroke:** $1.5\text{ pt}$ ($19,050\text{ EMU}$) solid line.
