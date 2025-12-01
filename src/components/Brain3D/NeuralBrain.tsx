import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { Sphere, MeshDistortMaterial } from '@react-three/drei';
import * as THREE from 'three';
import type { NeuralRegion } from '../../types';

interface NeuralBrainProps {
  regions: NeuralRegion[];
  autoRotate?: boolean;
  illuminationLevel?: number;
}

/**
 * NeuralBrain - 3D Brain Visualization Component
 *
 * Represents the core of CyberIDE with a neural network-inspired brain
 * that illuminates progressively based on project health metrics.
 */
export const NeuralBrain: React.FC<NeuralBrainProps> = ({
  regions,
  autoRotate = true,
  illuminationLevel = 0,
}) => {
  const groupRef = useRef<THREE.Group>(null);
  const coreRef = useRef<THREE.Mesh>(null);

  // Auto-rotation animation
  useFrame((state, delta) => {
    if (groupRef.current && autoRotate) {
      groupRef.current.rotation.y += delta * 0.1;
    }

    // Pulsing effect based on illumination
    if (coreRef.current) {
      const scale = 1 + Math.sin(state.clock.elapsedTime * 2) * 0.02 * illuminationLevel;
      coreRef.current.scale.setScalar(scale);
    }
  });

  // Neural pathways (connecting lines between regions)
  const pathways = useMemo(() => {
    const lines: React.ReactElement[] = [];

    regions.forEach((region, index) => {
      // Connect to next region (creating a network)
      const nextIndex = (index + 1) % regions.length;
      const nextRegion = regions[nextIndex];

      const points = [
        new THREE.Vector3(...region.position),
        new THREE.Vector3(...nextRegion.position),
      ];

      const geometry = new THREE.BufferGeometry().setFromPoints(points);

      // Illumination color based on status
      const color = getStatusColor(region.status);
      const opacity = region.illumination * 0.8;

      lines.push(
        <primitive
          key={`pathway-${region.id}-${nextRegion.id}`}
          object={new THREE.Line(
            geometry,
            new THREE.LineBasicMaterial({
              color,
              transparent: true,
              opacity,
              linewidth: 2,
            })
          )}
        />
      );
    });

    return lines;
  }, [regions]);

  return (
    <group ref={groupRef}>
      {/* Core Brain Sphere */}
      <Sphere ref={coreRef} args={[2, 64, 64]} position={[0, 0, 0]}>
        <MeshDistortMaterial
          color="#0a0e27"
          emissive="#00f0ff"
          emissiveIntensity={illuminationLevel * 0.5}
          metalness={0.8}
          roughness={0.2}
          distort={0.3}
          speed={2}
          transparent
          opacity={0.9}
        />
      </Sphere>

      {/* Neural Regions */}
      {regions.map((region) => (
        <NeuralNode
          key={region.id}
          region={region}
        />
      ))}

      {/* Neural Pathways */}
      {pathways}

      {/* Outer Glow Ring */}
      <mesh position={[0, 0, 0]} rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[3, 0.05, 16, 100]} />
        <meshStandardMaterial
          color="#00f0ff"
          emissive="#00f0ff"
          emissiveIntensity={illuminationLevel}
          transparent
          opacity={0.6}
        />
      </mesh>
    </group>
  );
};

/**
 * NeuralNode - Individual region/node in the brain
 */
interface NeuralNodeProps {
  region: NeuralRegion;
}

const NeuralNode: React.FC<NeuralNodeProps> = ({ region }) => {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (meshRef.current && region.illumination > 0) {
      // Pulsing effect for active nodes
      const pulse = Math.sin(state.clock.elapsedTime * 3) * 0.1 + 0.9;
      meshRef.current.scale.setScalar(0.3 * pulse);
    }
  });

  const color = getStatusColor(region.status);
  const emissiveIntensity = region.illumination * 2;

  return (
    <Sphere
      ref={meshRef}
      args={[0.3, 32, 32]}
      position={region.position}
    >
      <meshStandardMaterial
        color={color}
        emissive={color}
        emissiveIntensity={emissiveIntensity}
        metalness={0.9}
        roughness={0.1}
        transparent
        opacity={region.illumination > 0 ? 1 : 0.3}
      />
    </Sphere>
  );
};

/**
 * Get color based on health status
 */
function getStatusColor(status: string): string {
  switch (status) {
    case 'optimal':
      return '#00ff9f'; // Neon green
    case 'healthy':
      return '#00f0ff'; // Cyan
    case 'warning':
      return '#ffa500'; // Orange
    case 'critical':
      return '#ff0055'; // Red
    case 'offline':
    default:
      return '#1a1f3a'; // Dark
  }
}
