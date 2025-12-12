/**
 * DNA HELIX 3D Component
 *
 * Double hélice ADN qui orbite autour du cerveau neural.
 * Représente la relation entre les fichiers source et les tests.
 */

import React, { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { Line, Sphere } from '@react-three/drei';
import type { DNAHelixProps, SourceFileNode, TestFileNode } from '../../types/dna';
import { DNA_COLORS } from '../../types/dna';

// Simplified particle system - removed to fix TypeScript issues
// Will be re-implemented with proper Three.js types later

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

  // Calculer l'intensité de résonance pour chaque node
  const getResonanceIntensity = (nodeId: string) => {
    if (!resonatingFiles.includes(nodeId)) return 0;

    // Generate a unique phase based on nodeId to avoid synchronized pulsing
    const phase = nodeId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    const time = pulseTimeRef.current;

    // Create a smooth wave between 0.5 and 1.0 using sine
    // Frequency increased to 4 for more visible pulsing
    const pulse = Math.sin(time * 4 + phase * 0.1);

    // Map [-1, 1] to [0.5, 1.0] for intensity
    return 0.75 + pulse * 0.25;
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
  useFrame((_state, delta) => {
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
      {/* Brin source (cyan) - Enhanced with tube geometry */}
      {sourceStrandPoints.length > 1 && (
        <Line
          points={sourceStrandPoints}
          color={DNA_COLORS.SOURCE_STRAND}
          lineWidth={3}
          transparent
          opacity={0.9}
        />
      )}

      {/* Brin test (violet) - Enhanced with tube geometry */}
      {testStrandPoints.length > 1 && (
        <Line
          points={testStrandPoints}
          color={DNA_COLORS.TEST_STRAND}
          lineWidth={3}
          transparent
          opacity={0.9}
        />
      )}

      {/* Nodes source avec effet de résonance - Enhanced */}
      {sourceFiles.slice(0, sourcePositions.length).map((file, index) => {
        const position = sourcePositions[index];
        const color = getSourceNodeColor(file);
        const resonanceIntensity = getResonanceIntensity(file.id);

        // Effet visuel de résonance : pulsation et grossissement
        const sphereSize = 0.18 * (1 + resonanceIntensity * 0.5);
        const emissiveIntensity = pulseIntensity * 1.5 * (1 + resonanceIntensity);

        return (
          <group key={`source-${file.id}`} position={position}>
            <Sphere args={[sphereSize, 24, 24]}>
              <meshStandardMaterial
                color={color}
                emissive={color}
                emissiveIntensity={emissiveIntensity}
                metalness={0.8}
                roughness={0.2}
                transparent
                opacity={0.95 * (1 + resonanceIntensity * 0.2)}
              />
            </Sphere>
            
            {/* Outer glow for nodes */}
            {file.testStatus === 'passing' && (
              <Sphere args={[sphereSize * 1.5, 16, 16]}>
                <meshBasicMaterial
                  color={color}
                  transparent
                  opacity={pulseIntensity * 0.15}
                  side={THREE.BackSide}
                />
              </Sphere>
            )}
          </group>
        );
      })}

      {/* Nodes test avec effet de résonance - Enhanced */}
      {testFiles.slice(0, testPositions.length).map((file, index) => {
        const position = testPositions[index];
        const color = getTestNodeColor(file);
        const resonanceIntensity = getResonanceIntensity(file.id);

        // Effet visuel de résonance : pulsation et grossissement
        const sphereSize = 0.18 * (1 + resonanceIntensity * 0.5);
        const emissiveIntensity = pulseIntensity * 1.5 * (1 + resonanceIntensity);

        return (
          <group key={`test-${file.id}`} position={position}>
            <Sphere args={[sphereSize, 24, 24]}>
              <meshStandardMaterial
                color={color}
                emissive={color}
                emissiveIntensity={emissiveIntensity}
                metalness={0.8}
                roughness={0.2}
                transparent
                opacity={0.95 * (1 + resonanceIntensity * 0.2)}
              />
            </Sphere>
            
            {/* Outer glow for test nodes */}
            {file.passed > 0 && (
              <Sphere args={[sphereSize * 1.5, 16, 16]}>
                <meshBasicMaterial
                  color={color}
                  transparent
                  opacity={pulseIntensity * 0.15}
                  side={THREE.BackSide}
                />
              </Sphere>
            )}
          </group>
        );
      })}

      {/* Connexions entre source et test - Enhanced */}
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
            lineWidth={connection.strength * 2}
            transparent
            opacity={connection.strength * 0.8}
          />
        );
      })}

      {/* Effet de particules amélioré */}
      {pulseIntensity > 0.5 && (
        <group>
          {sourcePositions.map((pos, i) => (
            <mesh key={`particle-${i}`} position={pos}>
              <sphereGeometry args={[0.06, 8, 8]} />
              <meshStandardMaterial
                color={DNA_COLORS.SOURCE_STRAND}
                emissive={DNA_COLORS.SOURCE_STRAND}
                emissiveIntensity={Math.sin(pulseTimeRef.current * 2 + i) * 0.8 + 0.7}
                transparent
                opacity={0.6}
                metalness={0.9}
                roughness={0.1}
              />
            </mesh>
          ))}
          {testPositions.map((pos, i) => (
            <mesh key={`particle-test-${i}`} position={pos}>
              <sphereGeometry args={[0.06, 8, 8]} />
              <meshStandardMaterial
                color={DNA_COLORS.TEST_STRAND}
                emissive={DNA_COLORS.TEST_STRAND}
                emissiveIntensity={Math.sin(pulseTimeRef.current * 2.5 + i) * 0.8 + 0.7}
                transparent
                opacity={0.6}
                metalness={0.9}
                roughness={0.1}
              />
            </mesh>
          ))}
        </group>
      )}
    </group>
  );
};