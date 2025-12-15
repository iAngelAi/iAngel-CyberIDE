import React, { useRef, useLayoutEffect, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface DNAHelixParticlesProps {
  positions: [number, number, number][];
  color: string;
  speed?: number;
  baseScale?: number;
  opacity?: number;
}

// Custom shader material to handle per-instance emissive intensity
// This preserves the original visual intent (pulsating glow) while using InstancedMesh
const ParticleMaterial = new THREE.MeshStandardMaterial({
  transparent: true,
  metalness: 0.9,
  roughness: 0.1,
});

// Définition manuelle stricte pour le Shader Three.js
interface ThreeShader {
  uniforms: {
    [key: string]: { value: unknown };
  };
  vertexShader: string;
  fragmentShader: string;
}

export const DNAHelixParticles: React.FC<DNAHelixParticlesProps> = ({
  positions,
  color,
  speed = 2,
  baseScale = 1,
  opacity = 0.6
}) => {
  const meshRef = useRef<THREE.InstancedMesh>(null);
  const shaderRef = useRef<ThreeShader | null>(null);
  const dummy = useMemo(() => new THREE.Object3D(), []);

  // Clone material to avoid sharing uniforms between different helix strands
  const material = useMemo(() => {
    const mat = ParticleMaterial.clone();
    mat.color.set(color);
    mat.emissive.set(color);
    mat.emissiveIntensity = 1; // Base intensity, modulated by shader
    mat.opacity = opacity;
    return mat;
  }, [color, opacity]);

  useLayoutEffect(() => {
    // We need to re-attach the onBeforeCompile because cloning might lose the closure context or we want specific speed
    // eslint-disable-next-line
    material.onBeforeCompile = (shader) => {
        shader.uniforms.uTime = { value: 0 };
        shader.uniforms.uSpeed = { value: speed };

        // Simpler injection for robustness:
        const header = 'uniform float uTime;\nuniform float uSpeed;\nvarying float vPulse;\n';
        if (!shader.vertexShader.includes(header)) {
             shader.vertexShader = header + shader.vertexShader;
        }

        shader.vertexShader = shader.vertexShader.replace(
          '#include <begin_vertex>',
          `
          #include <begin_vertex>
          float phase = float(gl_InstanceID);
          vPulse = sin(uTime * uSpeed + phase) * 0.4 + 0.6; // [0.2, 1.0] range
          `
        );

        const fragHeader = 'varying float vPulse;\n';
        if (!shader.fragmentShader.includes(fragHeader)) {
            shader.fragmentShader = fragHeader + shader.fragmentShader;
        }

        shader.fragmentShader = shader.fragmentShader.replace(
          '#include <emissivemap_fragment>',
          `
          #include <emissivemap_fragment>
          totalEmissiveRadiance *= vPulse;
          `
        );

        shaderRef.current = shader;
    };

    material.needsUpdate = true;
  }, [material, speed]);

  useLayoutEffect(() => {
    if (!meshRef.current) return;

    positions.forEach((pos, i) => {
      dummy.position.set(pos[0], pos[1], pos[2]);
      dummy.scale.set(baseScale, baseScale, baseScale);
      dummy.updateMatrix();
      meshRef.current!.setMatrixAt(i, dummy.matrix);
    });
    meshRef.current.instanceMatrix.needsUpdate = true;
  }, [positions, dummy, baseScale]);

  useFrame(({ clock }) => {
    if (shaderRef.current && shaderRef.current.uniforms.uTime) {
      shaderRef.current.uniforms.uTime.value = clock.getElapsedTime();
    }
  });

  if (positions.length === 0) return null;

  return (
    <instancedMesh
      ref={meshRef}
      args={[undefined, undefined, positions.length]}
      material={material}
    >
      <sphereGeometry args={[0.06, 8, 8]} />
    </instancedMesh>
  );
};
