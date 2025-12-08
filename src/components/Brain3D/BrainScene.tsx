import { Canvas } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera, Stars } from '@react-three/drei';
import { NeuralBrain } from './NeuralBrain';
import { DNAHelix } from '../DNAHelix';
import { EffectComposer, Bloom, ChromaticAberration } from '@react-three/postprocessing';
import { BlendFunction } from 'postprocessing';
import * as THREE from 'three';
import type { BrainState } from '../../types';
import type { SourceFileNode, TestFileNode, FileConnection } from '../../types/dna';

interface BrainSceneProps {
  brainState: BrainState;
  sourceFiles?: SourceFileNode[];
  testFiles?: TestFileNode[];
  connections?: FileConnection[];
  resonatingFiles?: string[];
}

/**
 * BrainScene - The main 3D canvas container
 *
 * Sets up the Three.js scene with lighting, camera, and controls
 * for the Neural Brain visualization.
 */
export const BrainScene: React.FC<BrainSceneProps> = ({
  brainState,
  sourceFiles = [],
  testFiles = [],
  connections = [],
  resonatingFiles = []
}) => {
  return (
    <div className="w-full h-full relative">
      <Canvas
        className="bg-cyber-darker"
        gl={{
          antialias: true,
          alpha: true,
          powerPreference: 'high-performance',
          toneMapping: THREE.ACESFilmicToneMapping,
          toneMappingExposure: 1.2,
        }}
      >
        {/* Camera */}
        <PerspectiveCamera
          makeDefault
          position={[0, 0, 8]}
          fov={60}
          near={0.1}
          far={1000}
        />

        {/* Lights - Enhanced for better visual quality */}
        <ambientLight intensity={0.3} color="#0a1929" />
        
        {/* Key light - Cyan */}
        <pointLight
          position={[10, 10, 10]}
          intensity={1.5}
          color="#00f0ff"
          distance={50}
          decay={2}
        />
        
        {/* Fill light - Magenta */}
        <pointLight
          position={[-10, -10, -10]}
          intensity={0.8}
          color="#ff00ff"
          distance={50}
          decay={2}
        />
        
        {/* Back light - Accent */}
        <pointLight
          position={[0, -5, -10]}
          intensity={1.0}
          color="#00ff9f"
          distance={40}
          decay={2}
        />

        {/* Directional rim light */}
        <directionalLight
          position={[0, 5, 5]}
          intensity={0.8}
          color="#00ff9f"
          castShadow={false}
        />
        
        {/* Spot light for dramatic effect */}
        <spotLight
          position={[0, 10, 0]}
          angle={0.5}
          penumbra={0.5}
          intensity={0.5}
          color="#ffffff"
          distance={30}
          decay={2}
        />

        {/* Stars background - Enhanced */}
        <Stars
          radius={100}
          depth={50}
          count={8000}
          factor={5}
          saturation={0.6}
          fade
          speed={1.5}
        />

        {/* The Neural Brain */}
        <NeuralBrain
          regions={brainState.regions}
          autoRotate={brainState.autoRotate}
          illuminationLevel={brainState.illuminationLevel}
        />

        {/* DNA Helix orbiting the brain */}
        {(sourceFiles.length > 0 || testFiles.length > 0) && (
          <DNAHelix
            sourceFiles={sourceFiles}
            testFiles={testFiles}
            connections={connections}
            rotationSpeed={0.1}
            pulseIntensity={brainState.illuminationLevel}
            resonatingFiles={resonatingFiles}
            visible={true}
          />
        )}

        {/* Orbit Controls for user interaction */}
        <OrbitControls
          enablePan={false}
          enableZoom={true}
          minDistance={5}
          maxDistance={15}
          autoRotate={brainState.autoRotate}
          autoRotateSpeed={0.5}
          enableDamping
          dampingFactor={0.05}
        />
        
        {/* Post-processing effects */}
        <EffectComposer>
          {/* Bloom for glowing effects */}
          <Bloom
            intensity={brainState.illuminationLevel * 1.5 + 0.3}
            luminanceThreshold={0.2}
            luminanceSmoothing={0.9}
            mipmapBlur
            radius={0.8}
          />
          
          {/* Chromatic aberration for cyberpunk feel */}
          <ChromaticAberration
            blendFunction={BlendFunction.NORMAL}
            offset={[0.0015, 0.0015]}
            radialModulation={true}
            modulationOffset={0.5}
          />
        </EffectComposer>
      </Canvas>

      {/* Illumination level indicator */}
      <div className="absolute bottom-4 left-4 bg-cyber-dark/80 backdrop-blur-sm cyber-border rounded-lg p-4">
        <div className="text-xs text-cyber-primary font-mono mb-2">
          NEURAL ILLUMINATION
        </div>
        <div className="w-48 h-2 bg-cyber-darker rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-cyber-primary to-cyber-accent transition-all duration-500"
            style={{ width: `${brainState.illuminationLevel * 100}%` }}
          />
        </div>
        <div className="text-xs text-white/60 font-mono mt-1">
          {Math.round(brainState.illuminationLevel * 100)}% ACTIVE
        </div>
      </div>

      {/* Active region display */}
      {brainState.activeRegion && (
        <div className="absolute top-4 left-4 bg-cyber-dark/80 backdrop-blur-sm cyber-border rounded-lg p-4">
          <div className="text-xs text-cyber-accent font-mono">
            ACTIVE REGION: {brainState.activeRegion}
          </div>
        </div>
      )}
    </div>
  );
};
