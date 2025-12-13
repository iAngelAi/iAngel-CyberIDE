import React, { useRef, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface ParticleStrandProps {
  positions: [number, number, number][];
  color: string;
  pulseIntensity: number;
  pulseSpeed?: number;
  pulseOffset?: number;
}

export const ParticleStrand: React.FC<ParticleStrandProps> = ({
  positions,
  color,
  pulseIntensity,
  pulseSpeed = 2,
  pulseOffset = 0,
}) => {
  // Store refs to materials to update them directly without re-rendering
  const materialRefs = useRef<(THREE.MeshStandardMaterial | null)[]>([]);

  // Update refs array size when positions change
  useEffect(() => {
    materialRefs.current = materialRefs.current.slice(0, positions.length);
    while (materialRefs.current.length < positions.length) {
      materialRefs.current.push(null);
    }
  }, [positions.length]);

  useFrame((state) => {
    // Only animate if there is some pulse intensity
    if (pulseIntensity <= 0) return;

    const time = state.clock.elapsedTime;

    materialRefs.current.forEach((material, i) => {
      if (material) {
        // Calculate intensity based on time and index for wave effect
        // Math.sin(time * speed + index) * amplitude + base
        const intensity = Math.sin(time * pulseSpeed + i + pulseOffset) * 0.8 + 0.7;
        material.emissiveIntensity = intensity;
      }
    });
  });

  return (
    <group>
      {positions.map((pos, i) => (
        <mesh key={`particle-${i}`} position={pos}>
          <sphereGeometry args={[0.06, 8, 8]} />
          <meshStandardMaterial
            ref={(el) => { materialRefs.current[i] = el; }}
            color={color}
            emissive={color}
            // Initial intensity
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
