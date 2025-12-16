import React, { useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface DNAHelixParticlesProps {
  positions: [number, number, number][];
  color: string;
  speed?: number;
  countPerNode?: number;
}

export const DNAHelixParticles: React.FC<DNAHelixParticlesProps> = ({
  positions,
  color,
  speed = 2,
  countPerNode = 8
}) => {
  const materialRef = useRef<THREE.ShaderMaterial>(null);

  // Generate particles
  const geometry = useMemo(() => {
    const totalParticles = positions.length * countPerNode;
    const geo = new THREE.BufferGeometry();

    const posArray = new Float32Array(totalParticles * 3);
    const scaleArray = new Float32Array(totalParticles);
    const phaseArray = new Float32Array(totalParticles);

    let ptr = 0;
    positions.forEach((pos) => {
      for (let i = 0; i < countPerNode; i++) {
        // Random offset in a sphere
        const theta = Math.random() * Math.PI * 2;
        const phi = Math.acos(2 * Math.random() - 1);
        const r = Math.random() * 0.5; // Radius of cloud around node

        const x = pos[0] + r * Math.sin(phi) * Math.cos(theta);
        const y = pos[1] + r * Math.sin(phi) * Math.sin(theta);
        const z = pos[2] + r * Math.cos(phi);

        posArray[ptr * 3] = x;
        posArray[ptr * 3 + 1] = y;
        posArray[ptr * 3 + 2] = z;

        scaleArray[ptr] = Math.random() * 0.5 + 0.5; // Random size variation
        phaseArray[ptr] = Math.random() * Math.PI * 2; // Random pulse phase

        ptr++;
      }
    });

    geo.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
    geo.setAttribute('aScale', new THREE.BufferAttribute(scaleArray, 1));
    geo.setAttribute('aPhase', new THREE.BufferAttribute(phaseArray, 1));

    return geo;
  }, [positions, countPerNode]);

  useFrame(({ clock }) => {
    if (materialRef.current) {
      materialRef.current.uniforms.uTime.value = clock.getElapsedTime();
    }
  });

  if (positions.length === 0) return null;

  return (
    <points geometry={geometry}>
      <shaderMaterial
        ref={materialRef}
        transparent
        depthWrite={false}
        blending={THREE.AdditiveBlending}
        uniforms={{
            uTime: { value: 0 },
            uColor: { value: new THREE.Color(color) },
            uSpeed: { value: speed }
        }}
        vertexShader={`
          uniform float uTime;
          uniform float uSpeed;
          attribute float aScale;
          attribute float aPhase;
          varying float vAlpha;

          void main() {
            vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
            gl_Position = projectionMatrix * mvPosition;

            float pulse = sin(uTime * uSpeed + aPhase) * 0.5 + 0.5;

            // Size attenuation
            gl_PointSize = (8.0 * aScale * (0.5 + 0.5 * pulse)) * (10.0 / -mvPosition.z);

            vAlpha = pulse * 0.8 + 0.2;
          }
        `}
        fragmentShader={`
          uniform vec3 uColor;
          varying float vAlpha;

          void main() {
            vec2 center = gl_PointCoord - 0.5;
            float dist = length(center);
            if (dist > 0.5) discard;

            float alpha = (1.0 - dist * 2.0) * vAlpha;
            alpha = pow(alpha, 1.5); // Soften

            gl_FragColor = vec4(uColor, alpha);
          }
        `}
      />
    </points>
  );
};
