import { render, screen } from '@testing-library/react';
import { DebugConsole } from '../components/DebugConsole/DebugConsole';
import { describe, it, expect, vi } from 'vitest';
import React from 'react';

describe('DebugConsole', () => {
  const mockProps = {
    logs: [],
    onClose: vi.fn(),
    onClear: vi.fn(),
    isOpen: true,
  };

  it('renders correctly when open', () => {
    render(<DebugConsole {...mockProps} />);
    expect(screen.getByText('SYSTEM_LOGS')).toBeInTheDocument();
  });

  it('minimize button has aria-label', () => {
    render(<DebugConsole {...mockProps} />);
    const minimizeButton = screen.getByTitle('Minimize Console');
    expect(minimizeButton).toBeInTheDocument();
    expect(minimizeButton).toHaveAttribute('aria-label', 'Minimize Console');
  });

  it('logs container has log role', () => {
    render(<DebugConsole {...mockProps} />);
    const logRegion = screen.getByRole('log');
    expect(logRegion).toBeInTheDocument();
    expect(logRegion).toHaveAttribute('aria-live', 'polite');
    expect(logRegion).toHaveAttribute('aria-label', 'System Logs');
  });
});
