/**
 * Types pour le Dashboard Git
 */

export interface GitBranchInfo {
  name: string;
  isActive: boolean;
  lastCommit: string;
  commitsAhead: number;
  color: string;
}

export interface GitFileHeatMap {
  path: string;
  modificationCount: number;
  lastModified: string;
  heatLevel: number;
}

export interface GitPulseEvent {
  id: string;
  type: 'commit' | 'merge' | 'branch';
  hash: string;
  author: string;
  message: string;
  timestamp: string;
  insertions: number;
  deletions: number;
  filesChanged: string[];
  intensity: number;
  color: string;
}

export interface GitCommitInfo extends GitPulseEvent {
  // Hérite de toutes les propriétés de GitPulseEvent
}

export interface GitDashboardData {
  branches: GitBranchInfo[];
  heatMap: GitFileHeatMap[];
  recentCommits: GitCommitInfo[];
  totalCommits: number;
  pulses: GitPulseEvent[];
  activeAuthors: Array<{
    name: string;
    commitCount: number;
    percentageOfTotal: number;
  }>;
  repositoryStats: {
    totalFiles: number;
    linesOfCode: number;
    lastUpdated: string;
  };
}

// Couleurs pour le dashboard
export const GIT_DASHBOARD_COLORS = {
  BRANCH_ACTIVE: '#00ff9f',
  BRANCH_INACTIVE: '#4b5563',
  HEAT_LOW: '#1a1f3a',
  HEAT_MEDIUM: '#ffa500',
  HEAT_HIGH: '#ff0055',
  COMMIT_BACKGROUND: '#22303c',
  COMMIT_BORDER: '#384a5b'
} as const;

export const GIT_PULSE_COLORS = {
  commit: '#22d3ee',       // Cyan pour les commits standard
  merge: '#a855f7',        // Violet pour les fusions
  branch: '#10b981',       // Vert émeraude pour les nouvelles branches
  hotfix: '#ff0055'        // Rouge vif pour les hotfixes
} as const;