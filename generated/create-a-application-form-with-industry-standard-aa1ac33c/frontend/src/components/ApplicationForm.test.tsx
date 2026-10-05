import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ApplicationForm from './ApplicationForm';

const mockFetch = jest.fn();

beforeEach(() => {
  jest.spyOn(window, 'fetch').mockImplementation(mockFetch);
});

afterEach(() => {
  jest.restoreAllMocks();
  mockFetch.mockReset();
});

describe('ApplicationForm', () => {
  test('renders all sections and fields', () => {
    render(<ApplicationForm />);

    expect(screen.getByRole('heading', { name: /Personal Information/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Address Information/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Job Information/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Supporting Documents/i })).toBeInTheDocument();

    expect(screen.getByLabelText(/First Name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Last Name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Phone/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Date of Birth/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Gender/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Street Address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/City/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/State/Province/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Postal Code/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Country/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Position Applied For/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Expected Salary/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Available Start Date/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Resume/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Cover Letter/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/I agree to the terms/i)).toBeInTheDocument();
  });

  test('shows validation errors on submit if required fields are empty', async () => {
    render(<ApplicationForm />);

    fireEvent.click(screen.getByRole('button', { name: /submit application/i }));

    await waitFor(() => {
      expect(screen.getByText(/First name is required/i)).toBeInTheDocument();
      expect(screen.getByText(/Last name is required/i)).toBeInTheDocument();
      expect(screen.getByText(/Email is required/i)).toBeInTheDocument();
      expect(screen.getByText(/Phone number is required/i)).toBeInTheDocument();
      expect(screen.getByText(/Date of birth is required/i)).toBeInTheDocument();
      expect(screen.getByText(/Gender selection is required/i)).toBeInTheDocument();
      expect(screen.getByText(/Address is required/i)).toBeInTheDocument();
      expect(screen.getByText(/City is required/i)).toBeInTheDocument();
      expect(screen.getByText(/State/Province is required/i)).toBeInTheDocument();
      expect(screen.getByText(/Postal Code is required/i)).toBeInTheDocument();
      expect(screen.getByText(/Country is required/i)).toBeInTheDocument();
      expect(screen.getByText(/Position applied for is required/i)).toBeInTheDocument();
      expect(screen.getByText(/Expected salary is required/i)).toBeInTheDocument();
      expect(screen.getByText(/Available start date is required/i)).toBeInTheDocument();
      expect(screen.getByText(/Resume upload is required/i)).toBeInTheDocument();
      expect(screen.getByText(/You must agree to the terms/i)).toBeInTheDocument();
    });
  });

  test('submits form successfully and shows success alert', async () => {
    mockFetch.mockResolvedValueOnce({ ok: true });

    render(<ApplicationForm />);

    fireEvent.input(screen.getByLabelText(/First Name/i), { target: { value: 'Alice' } });
    fireEvent.input(screen.getByLabelText(/Last Name/i), { target: { value: 'Smith' } });
    fireEvent.input(screen.getByLabelText(/Email/i), { target: { value: 'alice@example.com' } });
    fireEvent.input(screen.getByLabelText(/Phone/i), { target: { value: '+1234567890' } });
    fireEvent.input(screen.getByLabelText(/Date of Birth/i), { target: { value: '1995-05-10' } });
    fireEvent.change(screen.getByLabelText(/Gender/i), { target: { value: 'female' } });
    fireEvent.input(screen.getByLabelText(/Street Address/i), { target: { value: '456 Park Ave' } });
    fireEvent.input(screen.getByLabelText(/City/i), { target: { value: 'Somewhere' } });
    fireEvent.input(screen.getByLabelText(/State/Province/i), { target: { value: 'Somestate' } });
    fireEvent.input(screen.getByLabelText(/Postal Code/i), { target: { value: '67890' } });
    fireEvent.input(screen.getByLabelText(/Country/i), { target: { value: 'USA' } });
    fireEvent.input(screen.getByLabelText(/Position Applied For/i), { target: { value: 'Designer' } });
    fireEvent.input(screen.getByLabelText(/Expected Salary/i), { target: { value: '40000' } });
    fireEvent.input(screen.getByLabelText(/Available Start Date/i), { target: { value: '2024-09-01' } });

    // Mock file upload
    const file = new File(['dummy content'], 'resume.pdf', { type: 'application/pdf' });
    fireEvent.change(screen.getByLabelText(/Resume/i), { target: { files: [file] } });

    fireEvent.change(screen.getByLabelText(/I agree to the terms/i), { target: { checked: true } });

    window.alert = jest.fn();

    fireEvent.click(screen.getByRole('button', { name: /submit application/i }));

    await waitFor(() => {
      expect(window.alert).toHaveBeenCalledWith('Application submitted successfully.');
    });
  });

  test('shows error alert on submit failure', async () => {
    mockFetch.mockResolvedValueOnce({ ok: false });

    render(<ApplicationForm />);
    const requiredFields = [
      { label: /First Name/i, value: 'John' },
      { label: /Last Name/i, value: 'Doe' },
      { label: /Email/i, value: 'john@example.com' },
      { label: /Phone/i, value: '+1234567890' },
      { label: /Date of Birth/i, value: '1990-01-01' },
      { label: /Gender/i, value: 'male' },
      { label: /Street Address/i, value: '123 Road' },
      { label: /City/i, value: 'Town' },
      { label: /State/Province/i, value: 'State' },
      { label: /Postal Code/i, value: '12345' },
      { label: /Country/i, value: 'Country' },
      { label: /Position Applied For/i, value: 'Engineer' },
      { label: /Expected Salary/i, value: '30000' },
      { label: /Available Start Date/i, value: '2024-10-10' },
    ];

    for (const field of requiredFields) {
      fireEvent.input(screen.getByLabelText(field.label), { target: { value: field.value } });
    }

    const file = new File(['dummy content'], 'resume.pdf', { type: 'application/pdf' });
    fireEvent.change(screen.getByLabelText(/Resume/i), { target: { files: [file] } });
    fireEvent.click(screen.getByLabelText(/I agree to the terms/i));

    window.alert = jest.fn();

    fireEvent.click(screen.getByRole('button', { name: /submit application/i }));

    await waitFor(() => {
      expect(window.alert).toHaveBeenCalledWith('Failed to submit application. Please try again later.');
    });
  });

  test('shows error alert on network error', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'));

    render(<ApplicationForm />);

    // Fill required fields
    fireEvent.input(screen.getByLabelText(/First Name/i), { target: { value: 'Jane' } });
    fireEvent.input(screen.getByLabelText(/Last Name/i), { target: { value: 'Doe' } });
    fireEvent.input(screen.getByLabelText(/Email/i), { target: { value: 'jane@example.com' } });
    fireEvent.input(screen.getByLabelText(/Phone/i), { target: { value: '+1234567890' } });
    fireEvent.input(screen.getByLabelText(/Date of Birth/i), { target: { value: '1992-02-02' } });
    fireEvent.change(screen.getByLabelText(/Gender/i), { target: { value: 'female' } });
    fireEvent.input(screen.getByLabelText(/Street Address/i), { target: { value: '789 Street' } });
    fireEvent.input(screen.getByLabelText(/City/i), { target: { value: 'City' } });
    fireEvent.input(screen.getByLabelText(/State/Province/i), { target: { value: 'State' } });
    fireEvent.input(screen.getByLabelText(/Postal Code/i), { target: { value: '98765' } });
    fireEvent.input(screen.getByLabelText(/Country/i), { target: { value: 'Country' } });
    fireEvent.input(screen.getByLabelText(/Position Applied For/i), { target: { value: 'Manager' } });
    fireEvent.input(screen.getByLabelText(/Expected Salary/i), { target: { value: '60000' } });
    fireEvent.input(screen.getByLabelText(/Available Start Date/i), { target: { value: '2024-08-01' } });
    const file = new File(['dummy content'], 'resume.pdf', { type: 'application/pdf' });
    fireEvent.change(screen.getByLabelText(/Resume/i), { target: { files: [file] } });
    fireEvent.click(screen.getByLabelText(/I agree to the terms/i));

    window.alert = jest.fn();

    fireEvent.click(screen.getByRole('button', { name: /submit application/i }));

    await waitFor(() => {
      expect(window.alert).toHaveBeenCalledWith('Failed to submit application, an error occurred.');
    });
  });
});
