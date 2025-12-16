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
import { DNAHelixParticles } from './DNAHelixParticles';

// Component for a single DNA node that handles its own animation
const DNANode: React.FC<{
    position: [number, number, number];
    color: string;
    nodeId: string;
    isResonating: boolean;
    basePulseIntensity: number;
    hasGlow: boolean;
}> = ({ position, color, nodeId, isResonating, basePulseIntensity, hasGlow }) => {
    const meshRef = useRef<THREE.Mesh>(null);
    const materialRef = useRef<THREE.MeshStandardMaterial>(null);
    const glowRef = useRef<THREE.Mesh>(null);
    const glowMaterialRef = useRef<THREE.MeshBasicMaterial>(null);

    // Calculate phase once
    const phase = useMemo(() =>
        nodeId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
    , [nodeId]);

    useFrame(({ clock }) => {
        if (!isResonating) {
            // Reset to base state if needed, or keep static
            if (meshRef.current) meshRef.current.scale.setScalar(0.18);
            if (materialRef.current) materialRef.current.emissiveIntensity = basePulseIntensity * 1.5;
             // If not resonating, we might still want some base emission
            return;
        }

        const time = clock.getElapsedTime();
        const pulse = Math.sin(time * 4 + phase * 0.1);
        const resonanceIntensity = 0.75 + pulse * 0.25; // 0.5 to 1.0

        // Update main sphere
        if (meshRef.current) {
             const scale = 0.18 * (1 + resonanceIntensity * 0.5);
             meshRef.current.scale.setScalar(scale);
        }

        if (materialRef.current) {
            materialRef.current.emissiveIntensity = basePulseIntensity * 1.5 * (1 + resonanceIntensity);
            materialRef.current.opacity = 0.95 * (1 + resonanceIntensity * 0.2);
        }

        // Update glow sphere
        if (hasGlow && glowRef.current && glowMaterialRef.current) {
             const scale = 0.18 * (1 + resonanceIntensity * 0.5) * 1.5;
             glowRef.current.scale.setScalar(scale);
             glowMaterialRef.current.opacity = basePulseIntensity * 0.15;
        }
    });

    // Initial scale/props for static state or start
    const initialScale = 0.18;

    return (
        <group position={position}>
             <Sphere ref={meshRef} args={[1, 24, 24]} scale={[initialScale, initialScale, initialScale]}>
              <meshStandardMaterial
                ref={materialRef}
                color={color}
                emissive={color}
                emissiveIntensity={basePulseIntensity * 1.5}
                metalness={0.8}
                roughness={0.2}
                transparent
                opacity={0.95}
              />
            </Sphere>

            {hasGlow && (
              <Sphere ref={glowRef} args={[1, 16, 16]} scale={[initialScale * 1.5, initialScale * 1.5, initialScale * 1.5]}>
                <meshBasicMaterial
                  ref={glowMaterialRef}
                  color={color}
                  transparent
                  opacity={basePulseIntensity * 0.15}
                  side={THREE.BackSide}
                />
              </Sphere>
            )}
        </group>
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
  // pulseTimeRef removed as it is now handled per node in useFrame

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

        return (
            <DNANode
                key={`source-${file.id}`}
                position={position}
                color={color}
                nodeId={file.id}
                isResonating={resonatingFiles.includes(file.id)}
                basePulseIntensity={pulseIntensity}
                hasGlow={file.testStatus === 'passing'}
            />
        );
      })}

      {/* Nodes test avec effet de résonance - Enhanced */}
      {testFiles.slice(0, testPositions.length).map((file, index) => {
        const position = testPositions[index];
        const color = getTestNodeColor(file);

        return (
            <DNANode
                key={`test-${file.id}`}
                position={position}
                color={color}
                nodeId={file.id}
                isResonating={resonatingFiles.includes(file.id)}
                basePulseIntensity={pulseIntensity}
                hasGlow={file.passed > 0}
            />
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

      {/* Effet de particules amélioré - Optimized with InstancedMesh (Comment unchanged but implementation updated) */}
      {pulseIntensity > 0.5 && (
        <group>
          <DNAHelixParticles
            positions={sourcePositions}
            color={DNA_COLORS.SOURCE_STRAND}
            speed={2}
          />
          <DNAHelixParticles
            positions={testPositions}
            color={DNA_COLORS.TEST_STRAND}
            speed={2.5}
          />
        </group>
      )}
    </group>
  );
};
