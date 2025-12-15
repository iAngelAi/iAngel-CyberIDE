# Bolt's Journal - Critical Learnings

This journal records critical performance learnings, anti-patterns, and architectural bottlenecks specific to this codebase.

## 2025-12-15 - InstancedMesh Shader Injection & Linter Conflicts
**Learning:** Standard `InstancedMesh` only supports geometric transformations (P/R/S). To animate properties like emissive intensity per-instance without draw call overhead, we must inject custom shader logic via `onBeforeCompile` using `gl_InstanceID`.
**Action:** When optimizing animated particle systems, use `onBeforeCompile` to move animation logic to the GPU. Note that ESLint `react-hooks/immutability` flags material mutations; use `useLayoutEffect` to isolate setup or explicitly suppress the rule for specific mutation lines.
