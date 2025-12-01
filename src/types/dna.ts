/**
 * Types pour le système DNA Helix
 */

export interface SourceFileNode {
  id: string;
  path: string;
  name: string;
  extension: string;
  linesOfCode: number;
  hasTests: boolean;
  testStatus: TestStatus;
  position?: [number, number, number];  // Position 3D calculée
}

export interface TestFileNode {
  id: string;
  path: string;
  name: string;
  passed: number;
  failed: number;
  skipped: number;
  coverage: number;
  lastRun: string;
  position?: [number, number, number];
}

export interface FileConnection {
  id: string;
  sourceId: string;
  testId: string;
  strength: number;
  status: ConnectionStatus;
}

export type TestStatus = 'passing' | 'failing' | 'partial' | 'none' | 'running';
export type ConnectionStatus = 'active' | 'weak' | 'broken' | 'new';

export interface GitPulseEvent {
  id: string;
  hash: string;
  author: string;
  message: string;
  timestamp: string;
  filesChanged: string[];
  intensity: number;
  type: 'commit' | 'merge' | 'branch';
}

export interface NodeResonanceEffect {
  fileId: string;
  intensity: number;
  duration: number;
  startTime: number;
}

export interface DNAHelixState {
  sourceNodes: SourceFileNode[];
  testNodes: TestFileNode[];
  connections: FileConnection[];
  activePulses: GitPulseEvent[];
  resonatingFiles: NodeResonanceEffect[]; // Liste des fichiers "résonants"
  isRotating: boolean;
  rotationSpeed: number;
}

export interface DNAHelixProps {
  sourceFiles: SourceFileNode[];
  testFiles: TestFileNode[];
  connections: FileConnection[];
  rotationSpeed?: number;
  pulseIntensity?: number;
  visible?: boolean;
}

export interface PulseWaveProps {
  active: boolean;
  intensity: number;
  color: string;
  affectedFiles: string[];
  onComplete: () => void;
}

// Couleurs du thème
export const DNA_COLORS = {
  // Brins
  SOURCE_STRAND: '#22d3ee',    // Cyan
  TEST_STRAND: '#a855f7',       // Violet

  // Status nodes
  PASSING: '#00ff9f',           // Vert néon
  FAILING: '#ff0055',           // Rouge
  PARTIAL: '#ffa500',           // Orange
  NONE: '#1a1f3a',              // Gris sombre

  // Connexions
  CONNECTION_ACTIVE: '#6366f1',  // Indigo
  CONNECTION_WEAK: '#4b5563',    // Gris

  // Pulses
  PULSE_COMMIT: '#00f0ff',      // Cyan brillant
  PULSE_MERGE: '#f472b6',       // Rose
  PULSE_BRANCH: '#facc15',      // Jaune
} as const;