## 2024-05-23 - Accessibility in Debug Console
**Learning:** Icon-only buttons are common in developer tools but often lack ARIA labels, making them inaccessible to screen readers despite their utility.
**Action:** Always check icon-only buttons for `aria-label` or `title` (which isn't enough) and add explicit accessible names.
