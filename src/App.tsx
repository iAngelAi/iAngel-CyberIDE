import { useState, useCallback } from 'react';
import { BrainScene } from './components/Brain3D';
import { useBrainState } from './hooks/useBrainState';
import { useWebSocket } from './hooks/useWebSocket';
import {
  isNeuralStatusMessage,
  isFileChangeMessage,
  isTestResultMessage,
  isDiagnosticMessage,
  isFileMappingMessage,
  isGitPulseMessage,
} from './types/backend';
import type { BackendWebSocketMessage } from './types/backend';
import type { SourceFileNode, TestFileNode, FileConnection } from './types/dna';
import { Brain, Activity, Zap, Wifi, WifiOff, AlertCircle, Server, Terminal } from 'lucide-react';
import { GitDashboard } from './components/GitDashboard';
import { DebugConsole } from './components/DebugConsole';
import type { LogEntry } from './components/DebugConsole';
import type { GitDashboardData } from './types/git';

/**
 * CyberIDE - Neural Architect Main Application
 *
 * The core interface featuring a 3D neural brain that visualizes
 * project health, test coverage, and development progress in real-time.
 */
function App() {
  const [isInitialized, setIsInitialized] = useState(false);
  const [lastNotification, setLastNotification] = useState<string | null>(null);

  // DNA Helix state for file mapping
  const [sourceFiles, setSourceFiles] = useState<SourceFileNode[]>([]);
  const [testFiles, setTestFiles] = useState<TestFileNode[]>([]);
  const [connections, setConnections] = useState<FileConnection[]>([]);
  const [resonatingFiles, setResonatingFiles] = useState<string[]>([]);

  // Debug Console State
  const [showDebugConsole, setShowDebugConsole] = useState(false);
  const [logs, setLogs] = useState<LogEntry[]>([]);

  const addLog = useCallback((message: string, source: string = 'System', level: LogEntry['level'] = 'info') => {
    setLogs(prev => {
      const newLogs = [...prev, {
        id: crypto.randomUUID(),
        timestamp: new Date(),
        level,
        message,
        source
      }];
      return newLogs.slice(-200); // Keep last 200 logs
    });
  }, []);

  // Initialize brain state management
  const {
    brainState,
    updateFromBackend,
    setRegionError,
    simulateActivation,
  } = useBrainState();

  // WebSocket message handler
  const handleWebSocketMessage = useCallback(
    (message: BackendWebSocketMessage) => {
      console.log('[App] Received WebSocket message:', message.type);
      addLog(`Received message: ${message.type}`, 'WebSocket', 'info');

      if (isNeuralStatusMessage(message)) {
        // Update brain state with backend data
        updateFromBackend(message.data);
        setIsInitialized(true);
        addLog('Neural status updated', 'Brain', 'success');
      } else if (isFileChangeMessage(message)) {
        // Show notification for file changes
        const { file_path, event_type } = message.data;
        setLastNotification(`File ${event_type}: ${file_path}`);
        addLog(`File ${event_type}: ${file_path}`, 'FileWatcher', 'info');
        setTimeout(() => setLastNotification(null), 5000);
      } else if (isTestResultMessage(message)) {
        // Show notification for test results
        const { passed, failed, total_tests } = message.data;
        const msg = failed > 0 
          ? `Tests: ${passed}/${total_tests} passed, ${failed} failed`
          : `All ${total_tests} tests passed!`;
        
        if (failed > 0) {
          setLastNotification(msg);
          addLog(msg, 'TestRunner', 'error');
        } else {
          setLastNotification(msg);
          addLog(msg, 'TestRunner', 'success');
        }
        setTimeout(() => setLastNotification(null), 5000);
      } else if (isDiagnosticMessage(message)) {
        // Show diagnostic as error state
        const { region, message: diagMessage, level } = message.data;
        setRegionError(region, `${level}: ${diagMessage}`);
        setLastNotification(`${level} in ${region}: ${diagMessage}`);
        const logSeverity = level === 'ALERT' ? 'error' : 'warn';
        addLog(`${level} in ${region}: ${diagMessage}`, 'Diagnostic', logSeverity);
        setTimeout(() => setLastNotification(null), 8000);
      } else if (isFileMappingMessage(message)) {
        // Update file mapping data for DNA Helix
        const mappingData = message.data;

        // Convert backend data to frontend types
        const newSourceFiles: SourceFileNode[] = mappingData.source_files.map(f => ({
          id: f.id,
          path: f.path,
          name: f.name,
          extension: f.extension,
          linesOfCode: f.linesOfCode,
          hasTests: f.hasTests,
          testStatus: f.testStatus as any
        }));

        const newTestFiles: TestFileNode[] = mappingData.test_files.map(f => ({
          id: f.id,
          path: f.path,
          name: f.name,
          passed: f.passed,
          failed: f.failed,
          skipped: f.skipped,
          coverage: f.coverage,
          lastRun: f.lastRun
        }));

        const newConnections: FileConnection[] = mappingData.connections.map(c => ({
          id: c.id,
          sourceId: c.source_id,
          testId: c.test_id,
          strength: c.strength,
          status: c.status as any
        }));

        setSourceFiles(newSourceFiles);
        setTestFiles(newTestFiles);
        setConnections(newConnections);

        const msg = `File mapping updated: ${newSourceFiles.length} sources, ${newTestFiles.length} tests`;
        setLastNotification(msg);
        addLog(msg, 'Mapper', 'info');
        setTimeout(() => setLastNotification(null), 3000);
      } else if (isGitPulseMessage(message)) {
        // Handle Git pulse events
        const { hash, author, message: commitMsg, intensity, files_changed } = message.data;

        // Mise à jour des fichiers résonants basée sur les fichiers modifiés
        const newResonatingFiles = sourceFiles
          .filter(file => files_changed.some((changedFile: string) => file.path.includes(changedFile)))
          .map(file => file.id);

        setResonatingFiles(newResonatingFiles);

        const notification = `Git Pulse: ${commitMsg.slice(0, 50)} by ${author} (${intensity.toFixed(1)})`;
        setLastNotification(notification);
        addLog(`${notification} [${hash.slice(0, 7)}]`, 'GitPulse', 'info');
        setTimeout(() => {
          // Réinitialiser les fichiers résonants après 3 secondes
          setResonatingFiles([]);
        }, 5000);
      }
    },
    [updateFromBackend, setRegionError, addLog, sourceFiles]
  );

  // Initialize WebSocket connection
  const { isConnected, sendMessage } = useWebSocket<BackendWebSocketMessage>({
    onMessage: handleWebSocketMessage,
    onOpen: () => {
      console.log('[App] WebSocket connected, requesting initial status');
      addLog('WebSocket connected', 'Network', 'success');
      // Request initial status after connection
      setTimeout(() => sendMessage({ command: 'refresh_status' }), 500);
    },
    onClose: () => {
      console.log('[App] WebSocket disconnected');
      addLog('WebSocket disconnected', 'Network', 'warn');
      setIsInitialized(false);
    },
  });

  // Helper to refresh status manually if needed
  const requestStatusRefresh = useCallback(() => {
    sendMessage({ command: 'refresh_status' });
  }, [sendMessage]);

  // Simulate neural initialization (for demo when backend is offline)
  const [showGitDashboard, setShowGitDashboard] = useState(false);

  const fetchGitDashboardData = async (): Promise<GitDashboardData> => {
    try {
      const response = await fetch('/git/dashboard');
      if (!response.ok) {
        throw new Error('Failed to fetch Git dashboard data');
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching Git dashboard:', error);
      throw error;
    }
  };

  const handleManualInitialize = () => {
    if (isInitialized || isConnected) return;
    setIsInitialized(true);
    simulateActivation();
  };

  return (
    <div className="w-full h-screen bg-cyber-darker relative overflow-hidden cyber-grid">
      {/* Scanline effect overlay */}
      <div className="absolute inset-0 scanlines pointer-events-none z-10" />

      {/* Header */}
      <header className="absolute top-0 left-0 right-0 z-20 bg-cyber-dark/80 backdrop-blur-sm border-b border-cyber-primary/30">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Brain className="w-8 h-8 text-cyber-primary" />
            <div>
              <h1 className="text-2xl font-bold neural-glow text-cyber-primary">
                CyberIDE
              </h1>
              <p className="text-xs text-cyber-primary/60 font-mono">
                Neural Architect v1.0
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {/* Connection Status Indicator */}
            <div
              className={`
                flex items-center gap-2 px-4 py-2 rounded-lg font-mono text-xs
                transition-all duration-300
                ${
                  isConnected
                    ? 'bg-cyber-accent/20 text-cyber-accent border border-cyber-accent/30'
                    : 'bg-red-500/20 text-red-400 border border-red-500/30'
                }
              `}
            >
              {isConnected ? (
                <>
                  <Wifi className="w-4 h-4" />
                  <span>NEURAL CORE ONLINE</span>
                </>
              ) : (
                <>
                  <WifiOff className="w-4 h-4" />
                  <span>OFFLINE</span>
                </>
              )}
            </div>

            {/* Git Dashboard Toggle */}
            <button
              onClick={() => setShowGitDashboard(!showGitDashboard)}
              className={`
                flex items-center gap-2 px-4 py-2 rounded-lg font-mono text-sm
                transition-all duration-300
                ${
                  showGitDashboard
                    ? 'bg-cyber-primary/20 text-cyber-primary'
                    : 'cyber-border bg-cyber-dark text-white/70 hover:bg-cyber-primary/10'
                }
              `}
            >
              <Server className="w-4 h-4" />
              {showGitDashboard ? 'HIDE GIT' : 'GIT DASHBOARD'}
            </button>

            {/* Debug Console Toggle */}
            <button
              onClick={() => setShowDebugConsole(!showDebugConsole)}
              className={`
                flex items-center gap-2 px-4 py-2 rounded-lg font-mono text-sm
                transition-all duration-300
                ${
                  showDebugConsole
                    ? 'bg-cyber-primary/20 text-cyber-primary'
                    : 'cyber-border bg-cyber-dark text-white/70 hover:bg-cyber-primary/10'
                }
              `}
            >
              <Terminal className="w-4 h-4" />
              {showDebugConsole ? 'HIDE LOGS' : 'DEBUG LOGS'}
            </button>

            {/* Manual Initialize (Demo Mode) */}
            {!isConnected && (
              <button
                onClick={handleManualInitialize}
                disabled={isInitialized}
                className={`
                  flex items-center gap-2 px-6 py-2 rounded-lg font-mono text-sm
                  transition-all duration-300
                  ${
                    isInitialized
                      ? 'bg-cyber-dark text-cyber-primary/40 cursor-not-allowed'
                      : 'cyber-border bg-cyber-dark text-cyber-primary hover:bg-cyber-primary hover:text-cyber-dark'
                  }
                `}
              >
                <Zap className="w-4 h-4" />
                {isInitialized ? 'DEMO ACTIVE' : 'DEMO MODE'}
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Notification Banner */}
      {lastNotification && (
        <div className="absolute top-24 left-1/2 transform -translate-x-1/2 z-30 animate-fade-in">
          <div className="flex items-center gap-2 px-6 py-3 bg-cyber-dark/90 backdrop-blur-sm cyber-border rounded-lg shadow-lg">
            <AlertCircle className="w-5 h-5 text-cyber-accent" />
            <span className="text-sm font-mono text-white">{lastNotification}</span>
          </div>
        </div>
      )}

      {/* Main 3D Brain Visualization */}
      <main className="w-full h-full">
        <BrainScene
          brainState={brainState}
          sourceFiles={sourceFiles}
          testFiles={testFiles}
          connections={connections}
          resonatingFiles={resonatingFiles}
        />
      </main>

      {/* Status Panel */}
      <aside className="absolute top-20 right-4 z-20 w-80 bg-cyber-dark/80 backdrop-blur-sm cyber-border rounded-lg p-4">
        <div className="flex items-center gap-2 mb-4">
          <Activity className="w-5 h-5 text-cyber-accent" />
          <h2 className="text-lg font-bold text-cyber-accent font-mono">
            NEURAL STATUS
          </h2>
        </div>

        <div className="space-y-3">
          {brainState.regions.map((region) => (
            <div
              key={region.id}
              className="bg-cyber-darker/50 rounded p-3 border border-cyber-primary/20"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-mono text-white/80">
                  {region.name}
                </span>
                <span
                  className={`text-xs font-mono ${
                    region.status === 'healthy'
                      ? 'text-cyber-accent'
                      : 'text-white/40'
                  }`}
                >
                  {region.status.toUpperCase()}
                </span>
              </div>
              <div className="w-full h-1 bg-cyber-darker rounded-full overflow-hidden">
                <div
                  className="h-full bg-cyber-accent transition-all duration-500"
                  style={{ width: `${region.progress}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </aside>

      {/* Footer Info */}
      <footer className="absolute bottom-0 left-0 right-0 z-20 bg-cyber-dark/60 backdrop-blur-sm border-t border-cyber-primary/20 p-3">
        <p className="text-xs text-center text-cyber-primary/60 font-mono">
          {isConnected && isInitialized
            ? '⚡ Neural pathways restored. System optimal.'
            : isConnected && !isInitialized
            ? '🔄 Awaiting neural status from backend...'
            : !isConnected && isInitialized
            ? '📡 Demo mode active - Backend offline'
            : '⏳ Connecting to Neural Core...'}
        </p>
      </footer>

      {/* Git Dashboard Overlay */}
      {showGitDashboard && (
        <div className="absolute top-24 right-4 z-40 w-[500px] max-h-[calc(100vh-8rem)] overflow-y-auto">
          <GitDashboard fetchDashboardData={fetchGitDashboardData} />
        </div>
      )}

      {/* Debug Console */}
      <DebugConsole
        logs={logs}
        isOpen={showDebugConsole}
        onClose={() => setShowDebugConsole(false)}
        onClear={() => setLogs([])}
      />
    </div>
  );
}

export default App;
