/**
 * GitPulseTimeline
 *
 * Visualisation chronologique des événements Git (pulses)
 */

import React, { useState } from 'react';
import { GitPulseEvent, GIT_PULSE_COLORS } from '../../types/git';
import {
  GitCommit,
  GitBranch,
  GitPullRequest,
  Code,
  GitMerge,
  Zap
} from 'lucide-react';

interface GitPulseTimelineProps {
  pulses: GitPulseEvent[];
}

const PulseTypeIcon = {
  commit: GitCommit,
  merge: GitMerge,
  branch: GitBranch
};

export const GitPulseTimeline: React.FC<GitPulseTimelineProps> = ({ pulses }) => {
  const [selectedPulse, setSelectedPulse] = useState<GitPulseEvent | null>(null);

  // Trier les pulses par horodatage (plus récent en premier)
  const sortedPulses = [...pulses].sort(
    (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );

  const renderPulseDetails = (pulse: GitPulseEvent) => {
    const Icon = PulseTypeIcon[pulse.type] || Code;
    const color = pulse.color || GIT_PULSE_COLORS[pulse.type];

    return (
      <div
        className="bg-cyber-dark/80 border border-cyber-dark/50 rounded-lg p-4 space-y-2 animate-pulse-in"
        style={{ borderLeftColor: color, borderLeftWidth: 4 }}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Icon
              size={16}
              color={color}
              className="opacity-80"
            />
            <span className="font-bold text-white/80 capitalize">
              {pulse.type} Event
            </span>
          </div>
          <span className="text-xs text-white/60">
            {new Date(pulse.timestamp).toLocaleString()}
          </span>
        </div>

        <div className="text-sm">
          <p><strong>Author:</strong> {pulse.author}</p>
          <p><strong>Message:</strong> {pulse.message}</p>
        </div>

        <div className="flex space-x-3 text-xs">
          <span className="text-green-400">
            <Zap size={12} className="inline-block mr-1" />
            {pulse.insertions} Insertions
          </span>
          <span className="text-red-400">
            <Zap size={12} className="inline-block mr-1" />
            {pulse.deletions} Deletions
          </span>
        </div>

        <div className="mt-2">
          <p className="text-xs text-white/60">Changed Files:</p>
          <div className="flex flex-wrap gap-1 mt-1">
            {pulse.filesChanged.map(file => (
              <span
                key={file}
                className="bg-cyber-primary/10 text-cyber-primary px-2 py-1 rounded-full text-xs"
              >
                {file}
              </span>
            ))}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center mb-2">
        <h3 className="text-sm font-bold text-white/80 flex items-center">
          <GitPullRequest size={16} className="mr-2 text-cyber-accent" />
          Git Pulse Timeline
        </h3>
        <span className="text-xs text-white/60">
          {pulses.length} events
        </span>
      </div>

      <div className="space-y-2 max-h-[300px] overflow-y-auto">
        {sortedPulses.map((pulse, index) => (
          <div
            key={pulse.id}
            className={`
              relative p-2 rounded-lg cursor-pointer transition-all duration-300
              ${selectedPulse?.id === pulse.id
                ? 'bg-cyber-primary/10 border border-cyber-primary/30'
                : 'hover:bg-cyber-darker/50'}
            `}
            onClick={() => setSelectedPulse(pulse)}
          >
            <div className="flex items-center space-x-3">
              {React.createElement(PulseTypeIcon[pulse.type] || Code, {
                size: 16,
                color: pulse.color || GIT_PULSE_COLORS[pulse.type],
                className: 'opacity-70'
              })}
              <div className="flex-grow">
                <p className="text-sm truncate text-white/80">
                  {pulse.message}
                </p>
                <p className="text-xs text-white/60">
                  {pulse.author} • {new Date(pulse.timestamp).toLocaleString()}
                </p>
              </div>
              <span
                className="text-xs text-white/60 px-2 py-1 bg-cyber-darker rounded-full"
                style={{ backgroundColor: pulse.color || GIT_PULSE_COLORS[pulse.type] + '20' }}
              >
                {pulse.type}
              </span>
            </div>
          </div>
        ))}
      </div>

      {selectedPulse && (
        <div className="mt-4">
          {renderPulseDetails(selectedPulse)}
        </div>
      )}
    </div>
  );
};