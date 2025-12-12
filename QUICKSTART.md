# CyberIDE - Quick Start Guide

## Prerequisites

- Node.js 18+
- Python 3.8+
- npm or pnpm

## Installation

```bash
# Clone the repository
git clone https://github.com/iAngelAi/iAngel-CyberIDE.git
cd iAngel-CyberIDE

# Install dependencies
npm install
pip install -r requirements.txt
```

## Launch the Application

### One-Command Launch (Recommended)

```bash
# Start everything (auto-installs dependencies)
python3 neural_core.py

# Or using npm:
npm start
```

This starts both the frontend (port 5173) and backend (port 8000) automatically.

### Separate Launch

If you prefer to run frontend and backend separately:

```bash
# Terminal 1 - Frontend
npm run dev

# Terminal 2 - Backend
python3 neural_core.py --backend
```

## Access the Application

Open your browser and navigate to:
```
http://localhost:5173/
```

## Try the Demo

Click the **"INITIALIZE NEURAL CORE"** button in the top-right corner.

Watch as:
- 6 neural regions activate sequentially
- The 3D brain illuminates progressively
- Status panel updates in real-time
- Illumination meter reaches 100%

## Interact with the Brain

- **Drag** with mouse to rotate the brain 360°
- **Scroll** to zoom in/out
- **Watch** the nodes pulse and glow
- **Observe** neural pathways connecting regions

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

## Customization Tips

### Change Brain Colors

Edit `tailwind.config.js`:

```javascript
colors: {
  cyber: {
    primary: '#00f0ff',    // Your color here
  }
}
```

### Add More Regions

Edit `src/App.tsx`:

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

Edit `src/components/Brain3D/NeuralBrain.tsx`:

```typescript
groupRef.current.rotation.y += delta * 0.1;  // Change 0.1 to adjust speed
```

## Troubleshooting

### Server Not Running?

```bash
cd iAngel-CyberIDE
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

## Next Steps

### Learn More
- Read the [full documentation](docs/README.md)
- Explore the [architecture decisions](docs/adr/)
- Review the [security policy](SECURITY.md)

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

## Key Commands

```bash
npm run dev      # Start development server
npm run build    # Build for production
npm run preview  # Preview production build
```

## Support

For more help:
- Check the [documentation index](docs/README.md)
- Review [troubleshooting guides](docs/README.md)
- Open an issue on GitHub

---

Enjoy exploring CyberIDE!
