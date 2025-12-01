/**
 * DNA HELIX 3D Component
 *
 * Double hélice ADN qui orbite autour du cerveau neural.
 * Représente la relation entre les fichiers source et les tests.
 */

import React, { useRef, useMemo, useEffect } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import * as THREE from 'three';
import { Line, Sphere, Points, PointMaterial } from '@react-three/drei';
import { DNAHelixProps, DNA_COLORS, SourceFileNode, TestFileNode } from '../../types/dna';

// Composant pour les particules dynamiques
const Particles: React.FC<{
  sourcePositions: [number, number, number][];
  testPositions: [number, number, number][];
  pulseIntensity: number;
  pulseTime: number;
}> = ({ sourcePositions, testPositions, pulseIntensity, pulseTime }) => {
  const { viewport } = useThree();
  const MAX_PARTICLES = 1000; // Augmenter le nombre de particules pour la capture

  // Générer des particules le long des deux brins
  const particlesRef = useRef<THREE.Points>(null);

  // Positions des particules
  const particlePositions = useMemo(() => {
    const positions: number[] = [];
    const interpolate = (start: [number, number, number], end: [number, number, number], steps: number) => {
      const interpolatedPoints: [number, number, number][] = [];
      for (let i = 0; i <= steps; i++) {
        const t = i / steps;
        interpolatedPoints.push([
          start[0] + (end[0] - start[0]) * t,
          start[1] + (end[1] - start[1]) * t,
          start[2] + (end[2] - start[2]) * t
        ]);
      }
      return interpolatedPoints;
    };

    // Ajouter des particules pour le brin source (cyan)
    // Génération de particules avec variation de densité
    const generateParticlesForStrand = (strand: [number, number, number][], baseColor: string) => {
      const strandParticles: number[] = [];

      // Calculer le nombre de particules par segment
      const particlesPerSegment = Math.floor(MAX_PARTICLES / (strand.length * 2));

      for (let i = 0; i < strand.length - 1; i++) {
        const pointsAlongSegment = interpolate(strand[i], strand[i + 1], particlesPerSegment);

        pointsAlongSegment.forEach((pos, index) => {
          // Variation de densité avec un gradient
          const densityFactor = Math.sin(index / pointsAlongSegment.length * Math.PI);

          // Bruit et variation
          const noiseX = (Math.random() - 0.5) * 0.2;
          const noiseY = (Math.random() - 0.5) * 0.2;
          const noiseZ = (Math.random() - 0.5) * 0.2;

          // Ajouter les particules avec bruit et gradient
          if (Math.random() < densityFactor) {
            strandParticles.push(
              pos[0] + noiseX,
              pos[1] + noiseY,
              pos[2] + noiseZ
            );
          }
        });
      }

      return strandParticles;
    };

    // Générer des particules pour chaque brin
    const sourceParticles = generateParticlesForStrand(sourcePositions, DNA_COLORS.SOURCE_STRAND);
    const testParticles = generateParticlesForStrand(testPositions, DNA_COLORS.TEST_STRAND);

    // Combiner les particules
    positions.push(...sourceParticles, ...testParticles);

    return new Float32Array(positions);
  }, [sourcePositions, testPositions]);

  // Animation des particules
  useFrame((state, delta) => {
    if (!particlesRef.current) return;

    // Animation de défilement
    const instanceMatrix = particlesRef.current.instanceMatrix;
    const positions = particlesRef.current.geometry.getAttribute('position') as THREE.BufferAttribute;

    for (let i = 0; i < positions.count; i++) {
      // Mouvement ondulatoire le long de l'hélice
      const offset = Math.sin(pulseTime * 2 + i * 0.1) * 0.05 * pulseIntensity;
      positions.setY(i, positions.getY(i) + offset * delta);
    }

    positions.needsUpdate = true;
  });

  return (
    <Points
      ref={particlesRef}
      positions={particlePositions}
      stride={3}
      frustumCulled={false}
    >
      <PointMaterial
        transparent
        color={[DNA_COLORS.SOURCE_STRAND, DNA_COLORS.TEST_STRAND]}
        size={0.05}
        sizeAttenuation
        depthWrite={false}
        opacity={Math.min(pulseIntensity * 1.5, 1)}
      />
    </Points>
  );
};

export const DNAHelix: React.FC<DNAHelixProps & {
  resonatingFiles?: string[];
}> = ({
  sourceFiles,
  testFiles,
  connections,
  rotationSpeed = 0.1,
  pulseIntensity = 0.5,
  visible = true,
  resonatingFiles = []
}) => {
  const groupRef = useRef<THREE.Group>(null);
  const pulseTimeRef = useRef(0);
  const resonanceEffectRef = useRef<number[]>([]);

  // Calculer l'intensité de résonance pour chaque node
  const getResonanceIntensity = (nodeId: string) => {
    if (!resonatingFiles.includes(nodeId)) return 0;

    // Calculer une intensité basée sur le temps écoulé depuis le commit
    const currentTime = Date.now();
    const resonanceIndex = resonanceEffectRef.current.findIndex(
      (startTime, index) => resonatingFiles[index] === nodeId
    );

    if (resonanceIndex === -1) return 0;

    const startTime = resonanceEffectRef.current[resonanceIndex];
    const timeSinceCommit = (currentTime - startTime) / 1000; // en secondes

    // Diminution exponentielle de l'intensité
    return Math.max(1 - timeSinceCommit / 3, 0);
  };

  // Calculer les positions des nodes sur l'hélice
  const { sourcePositions, testPositions } = useMemo(() => {
    const maxNodes = 50; // Limite performance
    const sourceCount = Math.min(sourceFiles.length, maxNodes);
    const testCount = Math.min(testFiles.length, maxNodes);

    const calculateHelixPosition = (
      index: number,
      total: number,
      strand: 'source' | 'test'
    ): [number, number, number] => {
      const t = index / Math.max(total - 1, 1); // 0 à 1
      const angle = t * Math.PI * 4; // 2 tours complets
      const height = (t - 0.5) * 8; // -4 à 4
      const radius = 4;

      // Décalage de phase entre les deux brins
      const phaseOffset = strand === 'source' ? 0 : Math.PI;

      const x = Math.cos(angle + phaseOffset) * radius;
      const z = Math.sin(angle + phaseOffset) * radius;

      return [x, height, z];
    };

    const sourcePos = sourceFiles
      .slice(0, sourceCount)
      .map((_, index) => calculateHelixPosition(index, sourceCount, 'source'));

    const testPos = testFiles
      .slice(0, testCount)
      .map((_, index) => calculateHelixPosition(index, testCount, 'test'));

    return {
      sourcePositions: sourcePos,
      testPositions: testPos
    };
  }, [sourceFiles, testFiles]);

  // Animation de rotation
  useFrame((state, delta) => {
    if (!groupRef.current || !visible) return;

    // Rotation autour de l'axe Y
    groupRef.current.rotation.y += rotationSpeed * delta;

    // Mise à jour du temps pour les pulsations
    pulseTimeRef.current += delta;
  });

  // Fonction pour obtenir la couleur d'un node source
  const getSourceNodeColor = (node: SourceFileNode) => {
    switch (node.testStatus) {
      case 'passing':
        return DNA_COLORS.PASSING;
      case 'failing':
        return DNA_COLORS.FAILING;
      case 'partial':
        return DNA_COLORS.PARTIAL;
      default:
        return DNA_COLORS.NONE;
    }
  };

  // Fonction pour obtenir la couleur d'un node test
  const getTestNodeColor = (node: TestFileNode) => {
    if (node.failed > 0) return DNA_COLORS.FAILING;
    if (node.passed > 0) return DNA_COLORS.PASSING;
    return DNA_COLORS.NONE;
  };

  // Fonction pour obtenir la couleur d'une connexion
  const getConnectionColor = (strength: number, status: string) => {
    if (status === 'active' || strength > 0.7) {
      return DNA_COLORS.CONNECTION_ACTIVE;
    }
    return DNA_COLORS.CONNECTION_WEAK;
  };

  // Créer les lignes de l'hélice (brins)
  const sourceStrandPoints = useMemo(() => {
    return sourcePositions.map(pos => new THREE.Vector3(...pos));
  }, [sourcePositions]);

  const testStrandPoints = useMemo(() => {
    return testPositions.map(pos => new THREE.Vector3(...pos));
  }, [testPositions]);

  if (!visible) return null;

  return (
    <group ref={groupRef}>
      {/* Brin source (cyan) */}
      {sourceStrandPoints.length > 1 && (
        <Line
          points={sourceStrandPoints}
          color={DNA_COLORS.SOURCE_STRAND}
          lineWidth={2}
          transparent
          opacity={0.8}
        />
      )}

      {/* Brin test (violet) */}
      {testStrandPoints.length > 1 && (
        <Line
          points={testStrandPoints}
          color={DNA_COLORS.TEST_STRAND}
          lineWidth={2}
          transparent
          opacity={0.8}
        />
      )}

      {/* Nodes source avec effet de résonance */}
      {sourceFiles.slice(0, sourcePositions.length).map((file, index) => {
        const position = sourcePositions[index];
        const color = getSourceNodeColor(file);
        const resonanceIntensity = getResonanceIntensity(file.id);

        // Effet visuel de résonance : pulsation et grossissement
        const sphereSize = 0.15 * (1 + resonanceIntensity * 0.5);
        const emissiveIntensity = pulseIntensity * (1 + resonanceIntensity);

        return (
          <Sphere
            key={`source-${file.id}`}
            position={position}
            args={[sphereSize, 16, 16]}
          >
            <meshStandardMaterial
              color={color}
              emissive={color}
              emissiveIntensity={emissiveIntensity}
              transparent
              opacity={0.9 * (1 + resonanceIntensity * 0.2)}
            />
          </Sphere>
        );
      })}

      {/* Nodes test avec effet de résonance */}
      {testFiles.slice(0, testPositions.length).map((file, index) => {
        const position = testPositions[index];
        const color = getTestNodeColor(file);
        const resonanceIntensity = getResonanceIntensity(file.id);

        // Effet visuel de résonance : pulsation et grossissement
        const sphereSize = 0.15 * (1 + resonanceIntensity * 0.5);
        const emissiveIntensity = pulseIntensity * (1 + resonanceIntensity);

        return (
          <Sphere
            key={`test-${file.id}`}
            position={position}
            args={[sphereSize, 16, 16]}
          >
            <meshStandardMaterial
              color={color}
              emissive={color}
              emissiveIntensity={emissiveIntensity}
              transparent
              opacity={0.9 * (1 + resonanceIntensity * 0.2)}
            />
          </Sphere>
        );
      })}

      {/* Connexions entre source et test */}
      {connections.map((connection) => {
        const sourceIndex = sourceFiles.findIndex(f => f.id === connection.sourceId);
        const testIndex = testFiles.findIndex(f => f.id === connection.testId);

        if (
          sourceIndex === -1 ||
          testIndex === -1 ||
          sourceIndex >= sourcePositions.length ||
          testIndex >= testPositions.length
        ) {
          return null;
        }

        const sourcePos = sourcePositions[sourceIndex];
        const testPos = testPositions[testIndex];
        const color = getConnectionColor(connection.strength, connection.status);

        return (
          <Line
            key={`conn-${connection.id}`}
            points={[
              new THREE.Vector3(...sourcePos),
              new THREE.Vector3(...testPos)
            ]}
            color={color}
            lineWidth={1}
            transparent
            opacity={connection.strength * 0.7}
          />
        );
      })}

      {/* Effet de particules optionnel */}
      {pulseIntensity > 0.7 && (
        <group>
          {sourcePositions.map((pos, i) => (
            <mesh key={`particle-${i}`} position={pos}>
              <sphereGeometry args={[0.05, 8, 8]} />
              <meshStandardMaterial
                color={DNA_COLORS.SOURCE_STRAND}
                emissive={DNA_COLORS.SOURCE_STRAND}
                emissiveIntensity={Math.sin(pulseTimeRef.current * 2 + i) * 0.5 + 0.5}
                transparent
                opacity={0.5}
              />
            </mesh>
          ))}
        </group>
      )}
    </group>
  );
};