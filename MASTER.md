# MASTER.md - Constabox: Forensic & Network Analysis Platform

This document serves as the master specification for the design, architecture, and implementation of the **Constabox** web interface. It defines the "pro max skill" level UI/UX standards, focusing on a high-fidelity, tactical, and data-centric aesthetic suitable for forensic and network security applications.

## 1. Project Overview

*   **Name**: Constabox
*   **Purpose**: Advanced digital forensics, network analysis, and cyber threat intelligence platform.
*   **Target Audience**: Security analysts, penetration testers, forensic investigators.
*   **Vibe**: "Hacker Chic", "Tactical Dashboard", "Sci-Fi Interface", "Clean & Professional".
*   **Tech Stack**: HTML5, Vanilla CSS3 (Custom Properties), Vanilla JavaScript (ES6+). No frameworks to ensure raw performance and control.

## 2. Design System (UI/UX Pro Max Skill)

### 2.1. Color Palette

The interface uses a dark, high-contrast theme optimized for low-light environments and long operational sessions.

*   **Backgrounds**:
    *   `--bg-primary`: `#0a0b10` (Deep Void Black - Main background)
    *   `--bg-secondary`: `#13151a` (Dark Gunmetal - Panels/Cards)
    *   `--bg-tertiary`: `#1c1f26` (Lighter Gunmetal - Inputs/Hover states)
    *   `--bg-overlay`: `rgba(10, 11, 16, 0.85)` (Backdrop blur)

*   **Accents (The "Cyber" Touch)**:
    *   `--accent-primary`: `#00ff9d` (Cyber Green - Success, Active, Safe)
    *   `--accent-secondary`: `#00d2ff` (Electric Cyan - Info, Links, Selection)
    *   `--accent-alert`: `#ff003c` (Crimson Red - Errors, Threats, Critical)
    *   `--accent-warning`: `#ffbd00` (Amber - Warnings, Caution)
    *   `--accent-purple`: `#bd00ff` (Void Purple - Special/Encrypted data)

*   **Text**:
    *   `--text-primary`: `#ffffff` (Pure White)
    *   `--text-secondary`: `#a0a0a0` (Light Grey)
    *   `--text-muted`: `#505050` (Dark Grey - Placeholders/Disabled)

*   **Borders & Glows**:
    *   `--border-color`: `#2d313a`
    *   `--glow-primary`: `0 0 10px rgba(0, 255, 157, 0.5)`
    *   `--glow-alert`: `0 0 10px rgba(255, 0, 60, 0.5)`

### 2.2. Typography

*   **Primary Font (UI)**: 'Inter', sans-serif (Clean, modern, readable).
*   **Monospace Font (Data/Code/Logs)**: 'JetBrains Mono', 'Fira Code', or 'Consolas' (Essential for technical data).
*   **Scale**:
    *   `h1`: 24px (Bold, Uppercase, Tracking 1px)
    *   `h2`: 18px (Semi-Bold)
    *   `body`: 14px (Regular)
    *   `mono`: 12px (Regular)
    *   `small`: 10px (Uppercase, Muted)

### 2.3. Layout & Structure

*   **Grid System**: 12-column fluid grid.
*   **Spacing**: 4px baseline grid (4px, 8px, 16px, 24px, 32px).
*   **Containers**: Card-based layout with thin, glowing borders.
*   **Sidebar**: Collapsible, icon-only mode for maximum screen real estate.
*   **Status Bar**: Sticky footer for global system status, network ping, and active tasks.

### 2.4. Visual Effects (The "Wow" Factor)

*   **Glassmorphism**: Subtle backdrop-filter blur on overlays and modals (`backdrop-filter: blur(12px)`).
*   **Scanlines**: Optional CRT scanline overlay (opacity 0.03) for retro-tech feel.
*   **Glow**: Accent elements emit a soft glow.
*   **Animations**:
    *   Smooth transitions (0.2s ease-out) for hover states.
    *   "Typing" effect for terminal outputs.
    *   Pulse effect for live status indicators.
    *   Slide-in panels for details.

## 3. UI Components

### 3.1. Navigation (The "Command Center")
*   **Top Bar**: App logo (SVG), Global Search (Command Palette style `Ctrl+K`), User Profile, Notifications.
*   **Sidebar**: Icons + Labels. Highlighting active route with a left border using `--accent-primary`.

### 3.2. Dashboard Widgets
*   **Network Map**: Interactive node-link diagram (D3.js or Canvas). Nodes pulse on activity.
*   **Live Feed**: Scrolling log of system events/network traffic (Matrix style).
*   **Resource Monitor**: Circular progress bars or sparklines for CPU/RAM/Bandwidth.
*   **Threat Intel**: Map with ping animations showing origin of attacks.

### 3.3. Data Tables
*   **Header**: Sticky, uppercase, muted text.
*   **Rows**: Zebra striping (very subtle), hover highlight.
*   **Cells**: Monospace for IPs, Hashes, Timestamps.
*   **Actions**: Context menu on right-click or ellipsis icon.

### 3.4. Terminal / Console
*   **Input**: `>` prompt, blinking cursor.
*   **Output**: Colored syntax highlighting for commands.
*   **Behavior**: Auto-scroll to bottom.

## 4. Implementation Guidelines

### 4.1. File Structure
```
constabox/
├── index.html          # Main dashboard entry
├── login.html          # Authentication gate
├── assets/
│   ├── css/
│   │   ├── main.css    # Variables, reset, typography
│   │   ├── layout.css  # Grid, sidebar, containers
│   │   ├── components.css # Cards, buttons, inputs
│   │   └── effects.css # Animations, glows, scanlines
│   ├── js/
│   │   ├── app.js      # Main logic
│   │   ├── charts.js   # Chart rendering (using library or canvas)
│   │   └── terminal.js # Console simulation
│   └── icons/          # SVG icons (Feather or Lucide)
└── README.md
```

### 4.2. HTML Standards
*   Semantic HTML5 tags (`<main>`, `<nav>`, `<aside>`, `<section>`, `<article>`).
*   Accessible ARIA labels for icon-only buttons.
*   Clean class naming (BEM or utility-first naming convention).

### 4.3. CSS Best Practices
*   Use CSS Variables for **everything** (colors, spacing, fonts). This allows for easy theming (e.g., switching from "Green Hacker" to "Red Alert" mode).
*   Use Flexbox for 1D layouts (navbars, lists).
*   Use CSS Grid for 2D layouts (dashboard structure).
*   Avoid `@import` in production; bundle CSS if possible, but for vanilla, keep it organized.

### 4.4. JavaScript Logic
*   **Modular**: functions for specific tasks (e.g., `updateNetworkGraph()`, `logMessage()`).
*   **Event Delegation**: Attach listeners to containers for dynamic elements.
*   **No jQuery**: Use `document.querySelector`, `classList`, `fetch`.

## 5. Sample Code Snippets

### 5.1. CSS Variables (Theme)
```css
:root {
    --bg-primary: #0a0b10;
    --accent-primary: #00ff9d;
    --font-mono: 'Fira Code', monospace;
}

body {
    background-color: var(--bg-primary);
    color: var(--text-primary);
    font-family: 'Inter', sans-serif;
}

.panel {
    background: rgba(19, 21, 26, 0.6);
    border: 1px solid rgba(45, 49, 58, 0.5);
    backdrop-filter: blur(10px);
    border-radius: 4px; /* Sharp technical look */
}
```

### 5.2. Terminal Animation
```css
@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0; }
}
.cursor {
    display: inline-block;
    width: 8px;
    height: 16px;
    background: var(--accent-primary);
    animation: blink 1s step-end infinite;
}
```

## 6. UX Requirements
*   **Load Time**: Under 1s (critical for tactical tools).
*   **Feedback**: Every action must have immediate visual feedback (click, submit, error).
*   **Data Density**: High. Avoid whitespace for the sake of aesthetics; prioritize information visibility.
*   **Keyboard Shortcuts**: Implement shortcuts for power users (e.g., `/` to search, `Esc` to close pane).

---
**Status**: DRAFT 1.0
**Author**: Antigravity (AI)
**Target**: Web Interface (HTML/CSS/JS)
