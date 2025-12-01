/**
 * PULSE WAVE
 *
 * Animation visuelle déclenchée par un commit Git.
 *
 * Effet : Onde circulaire qui part du centre du cerveau
 * et s'étend vers l'extérieur, colorée selon l'intensité.
 *
 * L'onde traverse la double hélice ADN et fait "résonner"
 * les nodes des fichiers modifiés dans le commit.
 */

import React, { useRef, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { PulseWaveProps, DNA_COLORS } from '../../types/dna';

export const PulseWave: React.FC<PulseWaveProps> = ({
  active,
  intensity,
  color,
  affectedFiles,
  onComplete
}) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const materialRef = useRef<THREE.ShaderMaterial>(null);
  const startTimeRef = useRef(0);
  const animationDuration = 3; // secondes

  // Shader material pour l'effet d'onde
  const shaderMaterial = React.useMemo(() => {
    return new THREE.ShaderMaterial({
      uniforms: {
        time: { value: 0 },
        color: { value: new THREE.Color(color) },
        intensity: { value: intensity },
        radius: { value: 0 }
      },
      vertexShader: `
        varying vec3 vPosition;
        varying vec2 vUv;

        void main() {
          vPosition = position;
          vUv = uv;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: `
        uniform float time;
        uniform vec3 color;
        uniform float intensity;
        uniform float radius;

        varying vec3 vPosition;
        varying vec2 vUv;

        void main() {
          float dist = length(vUv - vec2(0.5, 0.5));

          // Créer un anneau plutôt qu'un disque
          float ring = smoothstep(radius - 0.1, radius, dist) *
                      (1.0 - smoothstep(radius, radius + 0.2, dist));

          // Fading avec le temps
          float opacity = ring * intensity * (1.0 - time / 3.0);

          // Effet de brillance
          vec3 finalColor = color + vec3(intensity * 0.5);

          gl_FragColor = vec4(finalColor, opacity);
        }
      `,
      transparent: true,
      side: THREE.DoubleSide,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    });
  }, [color, intensity]);

  // Reset quand l'animation démarre
  useEffect(() => {
    if (active) {
      startTimeRef.current = 0;
      if (materialRef.current) {
        materialRef.current.uniforms.time.value = 0;
        materialRef.current.uniforms.radius.value = 0;
      }
    }
  }, [active]);

  // Animation frame
  useFrame((state, delta) => {
    if (!active || !materialRef.current) return;

    startTimeRef.current += delta;

    // Mettre à jour le temps dans le shader
    materialRef.current.uniforms.time.value = startTimeRef.current;

    // Expansion du rayon
    const normalizedTime = startTimeRef.current / animationDuration;
    const radius = normalizedTime * 2; // Expansion jusqu'à rayon 2
    materialRef.current.uniforms.radius.value = radius;

    // Scale de la sphère
    if (meshRef.current) {
      const scale = 1 + normalizedTime * 5;
      meshRef.current.scale.set(scale, scale, scale);
    }

    // Vérifier si l'animation est terminée
    if (startTimeRef.current >= animationDuration) {
      onComplete();
    }
  });

  if (!active) return null;

  return (
    <mesh ref={meshRef} position={[0, 0, 0]}>
      <planeGeometry args={[10, 10, 32, 32]} />
      <primitive
        ref={materialRef}
        object={shaderMaterial}
        attach="material"
      />
    </mesh>
  );
};

// Composant pour gérer plusieurs pulses simultanés
interface PulseManagerProps {
  pulses: Array<{
    id: string;
    intensity: number;
    color: string;
    affectedFiles: string[];
  }>;
}

export const PulseManager: React.FC<PulseManagerProps> = ({ pulses }) => {
  const [activePulses, setActivePulses] = React.useState<typeof pulses>([]);

  // Ajouter les nouveaux pulses à la file
  useEffect(() => {
    pulses.forEach(pulse => {
      if (!activePulses.find(p => p.id === pulse.id)) {
        setActivePulses(prev => [...prev, pulse]);
      }
    });
  }, [pulses]);

  // Retirer un pulse quand son animation est terminée
  const handlePulseComplete = (pulseId: string) => {
    setActivePulses(prev => prev.filter(p => p.id !== pulseId));
  };

  return (
    <>
      {activePulses.map(pulse => (
        <PulseWave
          key={pulse.id}
          active={true}
          intensity={pulse.intensity}
          color={pulse.color}
          affectedFiles={pulse.affectedFiles}
          onComplete={() => handlePulseComplete(pulse.id)}
        />
      ))}
    </>
  );
};