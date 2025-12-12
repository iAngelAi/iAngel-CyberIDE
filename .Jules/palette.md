## 2024-05-23 - Accessibility in Debug Console
**Learning:** Icon-only buttons are common in developer tools but often lack ARIA labels, making them inaccessible to screen readers despite their utility.
**Action:** Always check icon-only buttons for `aria-label` or `title` (which isn't enough) and add explicit accessible names.

## 2024-05-23 - Interactive Elements Accessibility
**Learning:** Clickable `div` elements are inaccessible to keyboard users as they lack semantic meaning and standard keyboard event handling (Enter/Space).
**Action:** Always use `<button>` for interactive elements. If a custom look is needed, style the button to look like a div (e.g., `text-left w-full`) but keep the semantic benefits and keyboard accessibility.
