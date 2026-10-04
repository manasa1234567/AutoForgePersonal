import { render, screen } from '@testing-library/react';
import App from './App';

test('renders the greeting text Hi', () => {
  render(<App />);
  const greetingElement = screen.getByText(/Hi/i);
  expect(greetingElement).toBeInTheDocument();
});
