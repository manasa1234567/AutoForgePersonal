import React from 'react';
import { render, screen } from '@testing-library/react';
import Dashboard from './Dashboard';

describe('Dashboard component', () => {
  test('renders dashboard title', () => {
    render(<Dashboard />);
    const heading = screen.getByRole('heading', { name: /dashboard/i });
    expect(heading).toBeInTheDocument();
  });

  test('renders key statistics cards', () => {
    render(<Dashboard />);
    const statCards = screen.getAllByRole('article');
    expect(statCards.length).toBeGreaterThanOrEqual(4);
    expect(screen.getByText('Users')).toBeInTheDocument();
    expect(screen.getByText('$43,215')).toBeInTheDocument();
  });

  test('renders recent activities section', () => {
    render(<Dashboard />);
    const recentActivities = screen.getByRole('region', { name: /recent activities/i });
    expect(recentActivities).toBeInTheDocument();
    expect(screen.getByText(/New user registered/i)).toBeInTheDocument();
  });
});
