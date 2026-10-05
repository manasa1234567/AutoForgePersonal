import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ApplicationForm from './ApplicationForm';

describe('ApplicationForm UI and Validation', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders all form fields and labels correctly', () => {
    render(<ApplicationForm />);
    expect(screen.getByLabelText(/First Name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Last Name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Date of Birth/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Phone Number/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Address Line 1/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Address Line 2/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/City/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/State\/Province/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Postal Code/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Country/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Signature/i)).toBeInTheDocument();
  });

  test('shows validation errors on submit with empty required fields', async () => {
    render(<ApplicationForm />);
    const submitBtn = screen.getByRole('button', { name: /submit application/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText(/First name is required./i)).toBeInTheDocument();
      expect(screen.getByText(/Last name is required./i)).toBeInTheDocument();
      expect(screen.getByText(/Date of birth is required./i)).toBeInTheDocument();
      expect(screen.getByText(/Email is required./i)).toBeInTheDocument();
      expect(screen.getByText(/Phone number is required./i)).toBeInTheDocument();
    });
  });

  test('submits form successfully with valid data', async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ id: 1 }),
      })
    ) as jest.Mock;

    render(<ApplicationForm />);

    fireEvent.change(screen.getByLabelText(/First Name/i), { target: { value: 'Jane' } });
    fireEvent.change(screen.getByLabelText(/Last Name/i), { target: { value: 'Smith' } });
    fireEvent.change(screen.getByLabelText(/Date of Birth/i), { target: { value: '1990-05-15' } });
    fireEvent.change(screen.getByLabelText(/Email/i), { target: { value: 'jane.smith@example.com' } });
    fireEvent.change(screen.getByLabelText(/Phone Number/i), { target: { value: '1234567890' } });
    fireEvent.change(screen.getByLabelText(/Address Line 1/i), { target: { value: '456 Oak St' } });
    fireEvent.change(screen.getByLabelText(/City/i), { target: { value: 'Sometown' } });
    fireEvent.change(screen.getByLabelText(/State\/Province/i), { target: { value: 'TX' } });
    fireEvent.change(screen.getByLabelText(/Postal Code/i), { target: { value: '78901' } });
    fireEvent.change(screen.getByLabelText(/Country/i), { target: { value: 'USA' } });
    fireEvent.change(screen.getByLabelText(/Signature/i), { target: { value: 'Jane Smith' } });

    fireEvent.click(screen.getByRole('button', { name: /submit application/i }));

    await waitFor(() => {
      expect(screen.getByText(/Application submitted successfully./i)).toBeInTheDocument();
    });
  });
});
