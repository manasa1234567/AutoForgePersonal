import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ApplicationForm from '../ApplicationForm';

describe('ApplicationForm', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  it('renders all expected input fields', () => {
    render(<ApplicationForm />);
    expect(screen.getByLabelText(/First Name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Last Name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Phone Number/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Date of Birth/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Address Line 1/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Address Line 2/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/City/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/State\/Province/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Postal Code/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Country/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Highest Education Level/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Employment Status/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Resume Text/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/I agree to the terms and conditions/i)).toBeInTheDocument();
  });

  it('shows validation errors on submit when required fields are empty or unchecked', async () => {
    render(<ApplicationForm />);
    const submitButton = screen.getByRole('button', { name: /submit application/i });
    userEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/First name is required/i)).toBeInTheDocument();
      expect(screen.getByText(/Last name is required/i)).toBeInTheDocument();
      expect(screen.getByText(/Email is required/i)).toBeInTheDocument();
      expect(screen.getByText(/Date of birth is required/i)).toBeInTheDocument();
      expect(screen.getByText(/Address Line 1 is required/i)).toBeInTheDocument();
      expect(screen.getByText(/City is required/i)).toBeInTheDocument();
      expect(screen.getByText(/State\/Province is required/i)).toBeInTheDocument();
      expect(screen.getByText(/Postal code is required/i)).toBeInTheDocument();
      expect(screen.getByText(/Country is required/i)).toBeInTheDocument();
      expect(screen.getByText(/Education level is required/i)).toBeInTheDocument();
      expect(screen.getByText(/Employment status is required/i)).toBeInTheDocument();
      expect(screen.getByText(/You must agree to the terms/i)).toBeInTheDocument();
    });
  });

  it('submits form successfully with valid data', async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({ ok: true, json: () => Promise.resolve({ message: 'Your application has been submitted successfully.' }) })
    ) as jest.Mock;

    render(<ApplicationForm />);
    const firstNameInput = screen.getByLabelText(/First Name/i);
    const lastNameInput = screen.getByLabelText(/Last Name/i);
    const emailInput = screen.getByLabelText(/Email/i);
    const dobInput = screen.getByLabelText(/Date of Birth/i);
    const addressLine1Input = screen.getByLabelText(/Address Line 1/i);
    const cityInput = screen.getByLabelText(/City/i);
    const stateInput = screen.getByLabelText(/State\/Province/i);
    const postalInput = screen.getByLabelText(/Postal Code/i);
    const countryInput = screen.getByLabelText(/Country/i);
    const educationInput = screen.getByLabelText(/Highest Education Level/i);
    const employmentInput = screen.getByLabelText(/Employment Status/i);
    const agreeCheckbox = screen.getByLabelText(/I agree to the terms and conditions/i);
    const submitButton = screen.getByRole('button', { name: /submit application/i });

    userEvent.type(firstNameInput, 'Jane');
    userEvent.type(lastNameInput, 'Doe');
    userEvent.type(emailInput, 'jane.doe@example.com');
    userEvent.type(dobInput, '1985-05-20');
    userEvent.type(addressLine1Input, '456 Elm St');
    userEvent.type(cityInput, 'Somewhere');
    userEvent.type(stateInput, 'Province');
    userEvent.type(postalInput, '54321');
    userEvent.selectOptions(countryInput, 'United States');
    userEvent.selectOptions(educationInput, 'Bachelor’s Degree');
    userEvent.selectOptions(employmentInput, 'Full-time');
    userEvent.click(agreeCheckbox);

    userEvent.click(submitButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled();
      expect(screen.getByText(/Your application has been submitted successfully./i)).toBeInTheDocument();
    });
  });

  it('shows error message on submission failure', async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({ ok: false, json: () => Promise.resolve({ detail: 'Terms agreement is required.' }) })
    ) as jest.Mock;

    render(<ApplicationForm />);
    const firstNameInput = screen.getByLabelText(/First Name/i);
    const lastNameInput = screen.getByLabelText(/Last Name/i);
    const emailInput = screen.getByLabelText(/Email/i);
    const dobInput = screen.getByLabelText(/Date of Birth/i);
    const addressLine1Input = screen.getByLabelText(/Address Line 1/i);
    const cityInput = screen.getByLabelText(/City/i);
    const stateInput = screen.getByLabelText(/State\/Province/i);
    const postalInput = screen.getByLabelText(/Postal Code/i);
    const countryInput = screen.getByLabelText(/Country/i);
    const educationInput = screen.getByLabelText(/Highest Education Level/i);
    const employmentInput = screen.getByLabelText(/Employment Status/i);
    const agreeCheckbox = screen.getByLabelText(/I agree to the terms and conditions/i);
    const submitButton = screen.getByRole('button', { name: /submit application/i });

    userEvent.type(firstNameInput, 'Jane');
    userEvent.type(lastNameInput, 'Doe');
    userEvent.type(emailInput, 'jane.doe@example.com');
    userEvent.type(dobInput, '1985-05-20');
    userEvent.type(addressLine1Input, '456 Elm St');
    userEvent.type(cityInput, 'Somewhere');
    userEvent.type(stateInput, 'Province');
    userEvent.type(postalInput, '54321');
    userEvent.selectOptions(countryInput, 'United States');
    userEvent.selectOptions(educationInput, 'Bachelor’s Degree');
    userEvent.selectOptions(employmentInput, 'Full-time');
    // Intentionally do NOT check terms

    userEvent.click(submitButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled();
      expect(screen.getByText(/Terms agreement is required./i)).toBeInTheDocument();
    });
  });
});
