/**
 * Dashboard Git pour CyberIDE
 *
 * Visualisation comprehensive de l'activité Git du projet
 */

import React, { useState, useEffect } from 'react';
import type {
  GitDashboardData
} from '../../types/git';
import { GIT_DASHBOARD_COLORS } from '../../types/git';
import {
  GitBranch,
  GitCommit,
  GitPullRequest,
  Flame,
  Clock,
  Code,
  Zap,
  Activity
} from 'lucide-react';
import { GitPulseTimeline } from './GitPulseTimeline';
import { MetricsMonitor } from '../MetricsMonitor';

interface GitDashboardProps {
  fetchDashboardData: () => Promise<GitDashboardData>;
}

export const GitDashboard: React.FC<GitDashboardProps> = ({ fetchDashboardData }) => {
  const [dashboardData, setDashboardData] = useState<GitDashboardData | null>(null);
  const [activeTab, setActiveTab] = useState<'branches' | 'heatmap' | 'commits' | 'pulses' | 'metrics'>('branches');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setIsLoading(true);
        const data = await fetchDashboardData();
        setDashboardData(data);
      } catch (err) {
        console.error('Error fetching Git dashboard data:', err);
        setError('Failed to load Git dashboard');
      } finally {
        setIsLoading(false);
      }
    };

    loadDashboardData();
  }, [fetchDashboardData]);

  const renderBranchesTab = () => {
    if (!dashboardData) return null;

    return (
      <div className="grid grid-cols-2 gap-4">
        {dashboardData.branches.map(branch => (
          <div
            key={branch.name}
            className={`
              p-3 rounded-lg transition-all duration-300
              ${branch.isActive
                ? 'bg-cyber-primary/10 border-2 border-cyber-primary/50'
                : 'bg-cyber-darker border border-cyber-dark/50'}
            `}
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center">
                <GitBranch
                  size={16}
                  color={branch.isActive ? GIT_DASHBOARD_COLORS.BRANCH_ACTIVE : GIT_DASHBOARD_COLORS.BRANCH_INACTIVE}
                  className="mr-2"
                />
                <span className={`font-bold ${branch.isActive ? 'text-cyber-primary' : 'text-white/60'}`}>
                  {branch.name}
                </span>
              </div>
              {branch.isActive && (
                <span className="text-xs bg-cyber-primary/20 px-2 py-1 rounded-full">
                  Active
                </span>
              )}
            </div>
            <div className="text-sm text-white/70">
              <p>Last Commit: {new Date(branch.lastCommit).toLocaleString()}</p>
              <p>Commits Ahead: {branch.commitsAhead}</p>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderHeatMapTab = () => {
    if (!dashboardData) return null;

    return (
      <div className="space-y-2">
        {dashboardData.heatMap.map(file => (
          <div
            key={file.path}
            className="flex items-center bg-cyber-darker rounded-lg p-2"
          >
            <Flame
              size={20}
              color={
                file.heatLevel < 0.3
                  ? GIT_DASHBOARD_COLORS.HEAT_LOW
                  : file.heatLevel < 0.7
                    ? GIT_DASHBOARD_COLORS.HEAT_MEDIUM
                    : GIT_DASHBOARD_COLORS.HEAT_HIGH
              }
              className="mr-3"
            />
            <div className="flex-grow">
              <div className="flex justify-between text-sm">
                <span>{file.path}</span>
                <span>{file.modificationCount} modifications</span>
              </div>
              <div
                className="h-1 mt-1 rounded-full"
                style={{
                  width: `${file.heatLevel * 100}%`,
                  backgroundColor:
                    file.heatLevel < 0.3
                      ? GIT_DASHBOARD_COLORS.HEAT_LOW
                      : file.heatLevel < 0.7
                        ? GIT_DASHBOARD_COLORS.HEAT_MEDIUM
                        : GIT_DASHBOARD_COLORS.HEAT_HIGH
                }}
              />
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderCommitsTab = () => {
    if (!dashboardData) return null;

    return (
      <div className="space-y-3">
        {dashboardData.recentCommits.map(commit => (
          <div
            key={commit.hash}
            className="bg-cyber-darker border border-cyber-dark/50 rounded-lg p-3"
          >
            <div className="flex justify-between items-center mb-2">
              <div className="flex items-center">
                <GitCommit size={16} className="mr-2 text-cyber-accent" />
                <span className="font-bold text-white/80 truncate max-w-[200px]">
                  {commit.message}
                </span>
              </div>
              <span className="text-xs text-white/60">
                {new Date(commit.timestamp).toLocaleString()}
              </span>
            </div>
            <div className="text-sm text-white/70">
              <p>Author: {commit.author}</p>
              <div className="flex space-x-3 mt-1">
                <span className="text-green-400">+ {commit.insertions}</span>
                <span className="text-red-400">- {commit.deletions}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderRepositoryStats = () => {
    if (!dashboardData) return null;

    return (
      <div className="bg-cyber-darker rounded-lg p-4 grid grid-cols-3 gap-4 text-center">
        <div>
          <Code size={24} className="mx-auto mb-2 text-cyber-primary" />
          <p className="text-sm text-white/70">Total Files</p>
          <p className="font-bold">{dashboardData.repositoryStats.totalFiles}</p>
        </div>
        <div>
          <Clock size={24} className="mx-auto mb-2 text-cyber-accent" />
          <p className="text-sm text-white/70">Last Updated</p>
          <p className="font-bold">{new Date(dashboardData.repositoryStats.lastUpdated).toLocaleString()}</p>
        </div>
        <div>
          <GitPullRequest size={24} className="mx-auto mb-2 text-cyber-primary" />
          <p className="text-sm text-white/70">Lines of Code</p>
          <p className="font-bold">{dashboardData.repositoryStats.linesOfCode.toLocaleString()}</p>
        </div>
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-full">
        <div className="animate-pulse text-cyber-primary">Loading Git Dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-red-500 text-center p-4">
        {error}
      </div>
    );
  }

  return (
    <div className="p-4 bg-cyber-dark/80 backdrop-blur-sm rounded-lg space-y-4">
      {/* Tabs */}
      <div className="flex space-x-4 mb-4 border-b border-cyber-dark/50 pb-2">
        {['branches', 'heatmap', 'commits', 'pulses', 'metrics'].map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab as 'branches' | 'heatmap' | 'commits' | 'pulses' | 'metrics')}
            className={`
              px-4 py-2 rounded-lg transition-all duration-300 flex items-center
              ${activeTab === tab
                ? 'bg-cyber-primary/20 text-cyber-primary'
                : 'text-white/60 hover:bg-cyber-primary/10'}
            `}
          >
            {tab === 'pulses' && <Zap size={14} className="mr-2" />}
            {tab === 'metrics' && <Activity size={14} className="mr-2" />}
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Repository Stats */}
      {renderRepositoryStats()}

      {/* Dynamic Content */}
      <div>
        {activeTab === 'branches' && renderBranchesTab()}
        {activeTab === 'heatmap' && renderHeatMapTab()}
        {activeTab === 'commits' && renderCommitsTab()}
        {activeTab === 'pulses' && dashboardData && (
          <GitPulseTimeline pulses={dashboardData.pulses} />
        )}
        {activeTab === 'metrics' && (
          <MetricsMonitor pollIntervalMs={5000} />
        )}
      </div>
    </div>
  );
};