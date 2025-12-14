import React, { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { DNA_COLORS } from '../../types/dna';

interface DNAParticlesProps {
  sourcePositions: [number, number, number][];
  testPositions: [number, number, number][];
  pulseIntensity: number;
}

export const DNAParticles: React.FC<DNAParticlesProps> = ({
  sourcePositions,
  testPositions,
  pulseIntensity
}) => {
  // Reuse geometry for all particles
  const particleGeometry = useMemo(() => new THREE.SphereGeometry(0.06, 8, 8), []);

  // Refs for materials to update them without re-rendering
  const sourceMaterialRefs = useRef<(THREE.MeshStandardMaterial | null)[]>([]);
  const testMaterialRefs = useRef<(THREE.MeshStandardMaterial | null)[]>([]);

  // Animation loop
  useFrame((state) => {
    const time = state.clock.elapsedTime;

    // Update source particles
    sourceMaterialRefs.current.forEach((material, i) => {
      if (material) {
        material.emissiveIntensity = Math.sin(time * 2 + i) * 0.8 + 0.7;
      }
    });

    // Update test particles
    testMaterialRefs.current.forEach((material, i) => {
      if (material) {
        material.emissiveIntensity = Math.sin(time * 2.5 + i) * 0.8 + 0.7;
      }
    });
  });

  if (pulseIntensity <= 0.5) return null;

  return (
    <group>
      {sourcePositions.map((pos, i) => (
        <mesh key={`particle-${i}`} position={pos} geometry={particleGeometry}>
          <meshStandardMaterial
            ref={(el) => (sourceMaterialRefs.current[i] = el)}
            color={DNA_COLORS.SOURCE_STRAND}
            emissive={DNA_COLORS.SOURCE_STRAND}
            // Initial intensity, updated in useFrame
            emissiveIntensity={0.7}
            transparent
            opacity={0.6}
            metalness={0.9}
            roughness={0.1}
          />
        </mesh>
      ))}
      {testPositions.map((pos, i) => (
        <mesh key={`particle-test-${i}`} position={pos} geometry={particleGeometry}>
          <meshStandardMaterial
            ref={(el) => (testMaterialRefs.current[i] = el)}
            color={DNA_COLORS.TEST_STRAND}
            emissive={DNA_COLORS.TEST_STRAND}
            // Initial intensity, updated in useFrame
            emissiveIntensity={0.7}
            transparent
            opacity={0.6}
            metalness={0.9}
            roughness={0.1}
          />
        </mesh>
      ))}
    </group>
  );
};
