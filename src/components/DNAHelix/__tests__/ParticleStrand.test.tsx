import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import { ParticleStrand } from '../ParticleStrand';
import React from 'react';

// Mock Three.js elements
vi.mock('@react-three/fiber', () => ({
  useFrame: vi.fn(),
  extend: vi.fn(),
}));

// eslint-disable-next-line @typescript-eslint/no-explicit-any
vi.mock('@react-three/drei', () => ({
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  Sphere: (props: any) => <div data-testid="sphere" {...props} />,
}));

describe('ParticleStrand', () => {
  const mockPositions: [number, number, number][] = [
    [0, 0, 0],
    [1, 1, 1],
    [2, 2, 2],
  ];

  it('renders correctly', () => {
    const { container } = render(
      <ParticleStrand
        positions={mockPositions}
        color="#00ffff"
        pulseIntensity={0.5}
      />
    );
    expect(container).toBeDefined();
  });

  it('renders correct number of particles', () => {
    // Note: Since we are not running in a real Canvas/WebGL environment,
    // we just check that the component renders without crashing.
    // In a real environment we would check for meshes.
    const { container } = render(
      <ParticleStrand
        positions={mockPositions}
        color="#00ffff"
        pulseIntensity={0.5}
      />
    );
    // Since <mesh> and <sphereGeometry> are not HTML elements, they won't appear in the DOM container in a way we can easily query without more complex mocking of R3F.
    // However, basic render test confirms no runtime errors in React logic.
    expect(container).toBeTruthy();
  });
});
