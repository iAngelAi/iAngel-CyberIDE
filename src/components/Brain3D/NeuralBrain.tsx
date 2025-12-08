import { useRef, useMemo } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import { Sphere } from '@react-three/drei';
import * as THREE from 'three';
import type { NeuralRegion } from '../../types';
import { brainVertexShader, brainFragmentShader } from '../../shaders/brainShaders';

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
  const shaderMaterialRef = useRef<THREE.ShaderMaterial>(null);
  const { camera } = useThree();

  // Enhanced shader material with custom effects
  const customShaderMaterial = useMemo(() => {
    return new THREE.ShaderMaterial({
      uniforms: {
        time: { value: 0 },
        illuminationLevel: { value: illuminationLevel },
        pulseIntensity: { value: illuminationLevel },
        primaryColor: { value: new THREE.Color('#00f0ff') },
        accentColor: { value: new THREE.Color('#ff00ff') },
        cameraPosition: { value: camera.position }
      },
      vertexShader: brainVertexShader,
      fragmentShader: brainFragmentShader,
      transparent: true,
      side: THREE.DoubleSide,
    });
  }, [camera.position]);

  // Auto-rotation animation
  useFrame((state, delta) => {
    if (groupRef.current && autoRotate) {
      groupRef.current.rotation.y += delta * 0.1;
    }

    // Update shader uniforms
    if (shaderMaterialRef.current) {
      shaderMaterialRef.current.uniforms.time.value = state.clock.elapsedTime;
      shaderMaterialRef.current.uniforms.illuminationLevel.value = illuminationLevel;
      shaderMaterialRef.current.uniforms.pulseIntensity.value = illuminationLevel;
      shaderMaterialRef.current.uniforms.cameraPosition.value.copy(camera.position);
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
      {/* Core Brain Sphere with custom shader */}
      <Sphere ref={coreRef} args={[2, 128, 128]} position={[0, 0, 0]}>
        <primitive 
          ref={shaderMaterialRef}
          object={customShaderMaterial} 
          attach="material" 
        />
      </Sphere>

      {/* Inner glow layer */}
      <Sphere args={[1.95, 64, 64]} position={[0, 0, 0]}>
        <meshBasicMaterial
          color="#00f0ff"
          transparent
          opacity={illuminationLevel * 0.1}
          side={THREE.BackSide}
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

      {/* Outer Glow Ring - Enhanced */}
      <mesh position={[0, 0, 0]} rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[3, 0.08, 16, 100]} />
        <meshStandardMaterial
          color="#00f0ff"
          emissive="#00f0ff"
          emissiveIntensity={illuminationLevel * 1.5}
          metalness={0.9}
          roughness={0.1}
          transparent
          opacity={0.7}
        />
      </mesh>

      {/* Additional ring for depth */}
      <mesh position={[0, 0, 0]} rotation={[Math.PI / 2, 0, Math.PI / 4]}>
        <torusGeometry args={[3.2, 0.05, 16, 100]} />
        <meshStandardMaterial
          color="#ff00ff"
          emissive="#ff00ff"
          emissiveIntensity={illuminationLevel * 1.2}
          metalness={0.8}
          roughness={0.2}
          transparent
          opacity={0.5}
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
  const glowRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (meshRef.current && region.illumination > 0) {
      // Enhanced pulsing effect for active nodes
      const pulse = Math.sin(state.clock.elapsedTime * 3) * 0.15 + 0.85;
      meshRef.current.scale.setScalar(0.3 * pulse);
      
      // Rotate the node slightly for dynamic effect
      meshRef.current.rotation.x = state.clock.elapsedTime * 0.5;
      meshRef.current.rotation.y = state.clock.elapsedTime * 0.3;
    }
    
    // Animate glow
    if (glowRef.current && region.illumination > 0) {
      const glowPulse = Math.sin(state.clock.elapsedTime * 4) * 0.2 + 0.8;
      glowRef.current.scale.setScalar(0.5 * glowPulse);
    }
  });

  const color = getStatusColor(region.status);
  const emissiveIntensity = region.illumination * 2.5;

  return (
    <group position={region.position}>
      {/* Main node sphere */}
      <Sphere
        ref={meshRef}
        args={[0.3, 32, 32]}
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
      
      {/* Outer glow */}
      {region.illumination > 0 && (
        <Sphere
          ref={glowRef}
          args={[0.5, 16, 16]}
        >
          <meshBasicMaterial
            color={color}
            transparent
            opacity={region.illumination * 0.2}
            side={THREE.BackSide}
          />
        </Sphere>
      )}
    </group>
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
