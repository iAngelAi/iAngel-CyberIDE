import React, { useRef, useEffect } from 'react';
import { Terminal, Trash2, ChevronDown } from 'lucide-react';

export interface LogEntry {
  id: string;
  timestamp: Date;
  level: 'info' | 'warn' | 'error' | 'success';
  message: string;
  source: string;
}

interface DebugConsoleProps {
  logs: LogEntry[];
  onClose: () => void;
  onClear: () => void;
  isOpen: boolean;
}

export const DebugConsole: React.FC<DebugConsoleProps> = ({
  logs,
  onClose,
  onClear,
  isOpen,
}) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (scrollRef.current && isOpen) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs, isOpen]);

  if (!isOpen) return null;

  return (
    <div className="absolute bottom-0 left-0 right-0 z-50 h-[300px] bg-black/90 backdrop-blur-md border-t border-cyber-primary/30 flex flex-col shadow-[0_-4px_20px_rgba(0,0,0,0.5)] transition-transform duration-300 ease-in-out font-mono">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-cyber-primary/20 bg-cyber-dark/80">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-cyber-primary" />
          <span className="text-sm font-bold text-cyber-primary tracking-wider">
            SYSTEM_LOGS
          </span>
          <span className="text-xs text-cyber-primary/50 ml-2 px-2 py-0.5 border border-cyber-primary/20 rounded">
            {logs.length} events
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={onClear}
            className="p-1.5 hover:bg-cyber-primary/10 rounded text-cyber-primary/60 hover:text-cyber-primary transition-colors flex items-center gap-1 text-xs"
            title="Clear Console"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>CLEAR</span>
          </button>
          <div className="w-px h-4 bg-cyber-primary/20 mx-1" />
          <button
            onClick={onClose}
            className="p-1.5 hover:bg-cyber-primary/10 rounded text-cyber-primary/60 hover:text-cyber-primary transition-colors"
            title="Minimize Console"
          >
            <ChevronDown className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Logs Area */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-2 text-xs space-y-0.5"
      >
        {logs.length === 0 ? (
          <div className="text-cyber-primary/30 italic p-2">No system events recorded. Waiting for neural activity...</div>
        ) : (
          logs.map((log) => (
            <div key={log.id} className="flex gap-3 hover:bg-white/5 p-1 rounded px-2 group">
              <span className="text-cyber-primary/30 shrink-0 select-none">
                {log.timestamp.toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit', fractionalSecondDigits: 3 })}
              </span>
              <span className={`shrink-0 font-bold w-20 text-right select-none ${
                log.level === 'error' ? 'text-red-500' :
                log.level === 'warn' ? 'text-yellow-500' :
                log.level === 'success' ? 'text-green-500' :
                'text-blue-400'
              }`}>
                [{log.source}]
              </span>
              <span className={`font-mono ${
                log.level === 'error' ? 'text-red-400' :
                log.level === 'warn' ? 'text-yellow-400' :
                log.level === 'success' ? 'text-green-400' :
                'text-cyber-primary/80'
              } break-all selection:bg-cyber-primary/30 selection:text-white`}>
                {log.message}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
