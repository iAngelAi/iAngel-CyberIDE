# CyberIDE - Quick Start Guide

## Get Started in 30 Seconds

### 1. The App is Already Running!

Open your browser and go to:
```
http://localhost:5173/
```

### 2. Try the Demo

Click the **"INITIALIZE NEURAL CORE"** button in the top-right corner.

Watch as:
- 6 neural regions activate sequentially
- The 3D brain illuminates progressively
- Status panel updates in real-time
- Illumination meter reaches 100%

### 3. Interact with the Brain

- **Drag** with mouse to rotate the brain 360°
- **Scroll** to zoom in/out
- **Watch** the nodes pulse and glow
- **Observe** neural pathways connecting regions

---

## What You're Seeing

### The 3D Brain

The rotating brain represents your project's health:
- **Dark nodes** = Offline (not started)
- **Cyan nodes** = Healthy (working)
- **Green nodes** = Optimal (perfect)
- **Orange nodes** = Warning (needs attention)
- **Red nodes** = Critical (broken)

### Neural Regions (Default 6)

1. **Core Logic** - Business logic modules
2. **API Integration** - External connections
3. **UI Components** - Frontend components
4. **Data Layer** - Database/storage
5. **Tests** - Test coverage
6. **Documentation** - Docs status

### Status Panel (Right Side)

Shows each region's:
- Name
- Status (OFFLINE/HEALTHY/OPTIMAL)
- Progress bar (0-100%)

### Illumination Meter (Bottom Left)

Overall system health visualization:
- **0%** = Nothing working
- **50%** = Half complete
- **100%** = All systems optimal

---

## File Structure at a Glance

```
src/
├── components/
│   ├── Brain3D/          # 3D visualization
│   ├── Diagnostics/      # Error alerts
│   └── Settings/         # Configuration (coming soon)
├── hooks/                # Custom React hooks
├── utils/                # Helper functions
├── types/                # TypeScript definitions
└── App.tsx               # Main application
```

---

## Customization Tips

### Change Brain Colors

Edit `/Users/felixlefebvre/CyberIDE/tailwind.config.js`:

```javascript
colors: {
  cyber: {
    primary: '#00f0ff',    // Your color here
  }
}
```

### Add More Regions

Edit `/Users/felixlefebvre/CyberIDE/src/App.tsx`:

```typescript
const initialRegions: NeuralRegion[] = [
  // Add your region here
  {
    id: 'security',
    name: 'Security',
    position: [3, 0, 0],  // 3D coordinates
    status: 'offline',
    progress: 0,
    illumination: 0,
  },
  // ...existing regions
];
```

### Modify Animation Speed

Edit `/Users/felixlefebvre/CyberIDE/src/components/Brain3D/NeuralBrain.tsx`:

```typescript
groupRef.current.rotation.y += delta * 0.1;  // Change 0.1 to adjust speed
```

---

## Troubleshooting

### Server Not Running?

```bash
cd /Users/felixlefebvre/CyberIDE
npm run dev
```

### Port 5173 Already in Use?

Vite will automatically use the next available port (5174, 5175, etc.)

### Brain Not Rendering?

1. Check WebGL support: https://get.webgl.org/
2. Update your graphics drivers
3. Try a different browser (Chrome recommended)

### TypeScript Errors?

```bash
npx tsc --noEmit
```

Should show no errors. If it does, check the file paths.

---

## Next Steps

### Learn More
- Read `SETUP.md` for detailed documentation
- Read `IMPLEMENTATION_SUMMARY.md` for technical details
- Read `CLAUDE.md` for the Neural Architect philosophy

### Extend the App
1. Connect to real test results (Phase 1)
2. Build the Settings UI (Phase 2)
3. Add advanced diagnostics (Phase 3)
4. Implement historical tracking (Phase 4)

### Explore the Code
- **3D Brain**: `src/components/Brain3D/NeuralBrain.tsx`
- **Main App**: `src/App.tsx`
- **Types**: `src/types/index.ts`
- **Utilities**: `src/utils/brainHelpers.ts`

---

## Key Commands

```bash
npm run dev      # Start development server
npm run build    # Build for production
npm run preview  # Preview production build
```

---

## Support

Questions? Check these files:
- **Setup Issues**: `SETUP.md`
- **Technical Details**: `IMPLEMENTATION_SUMMARY.md`
- **Philosophy**: `CLAUDE.md`
- **Roadmap**: `ROADMAP.md`

---

**Status:** ⚡ System Optimal. Neural Core Active.

Enjoy exploring CyberIDE!
