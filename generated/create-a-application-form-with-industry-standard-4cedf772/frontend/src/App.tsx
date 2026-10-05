import React, { useState } from 'react';

interface FormData {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  address: string;
  city: string;
  state: string;
  postalCode: string;
  country: string;
}

interface FormErrors {
  firstName?: string;
  lastName?: string;
  email?: string;
  phone?: string;
  address?: string;
  city?: string;
  state?: string;
  postalCode?: string;
  country?: string;
}

const initialFormData: FormData = {
  firstName: '',
  lastName: '',
  email: '',
  phone: '',
  address: '',
  city: '',
  state: '',
  postalCode: '',
  country: '',
};

const Header: React.FC = () => (
  <header className="header">
    <h1>Application Form</h1>
  </header>
);

const Footer: React.FC = () => (
  <footer className="footer">
    <p>Contact us: support@example.com | &copy; 2024 Company Inc.</p>
    <p>Legal Disclaimer: This application is confidential and intended for authorized use only.</p>
  </footer>
);

const App: React.FC = () => {
  const [formData, setFormData] = useState<FormData>(initialFormData);
  const [errors, setErrors] = useState<FormErrors>({});
  const [submitStatus, setSubmitStatus] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validateEmail = (email: string) => {
    // Basic email regex
    return /^\S+@\S+\.\S+$/.test(email);
  };

  function validateForm(data: FormData): FormErrors {
    const newErrors: FormErrors = {};
    if (!data.firstName.trim()) {
      newErrors.firstName = 'First name is required';
    }
    if (!data.lastName.trim()) {
      newErrors.lastName = 'Last name is required';
    }
    if (!data.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!validateEmail(data.email)) {
      newErrors.email = 'Invalid email address';
    }
    return newErrors;
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));

    // Clear error on change for the field
    if (errors[name as keyof FormErrors]) {
      setErrors((prev) => {
        const copy = { ...prev };
        delete copy[name as keyof FormErrors];
        return copy;
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const formErrors = validateForm(formData);
    setErrors(formErrors);
    if (Object.keys(formErrors).length > 0) {
      setSubmitStatus('Please fix errors before submitting.');
      return;
    }

    setIsSubmitting(true);
    setSubmitStatus('');

    try {
      const response = await fetch('/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          first_name: formData.firstName,
          last_name: formData.lastName,
          email: formData.email,
          phone: formData.phone || undefined,
          address: formData.address || undefined,
          city: formData.city || undefined,
          state: formData.state || undefined,
          postal_code: formData.postalCode || undefined,
          country: formData.country || undefined,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        setSubmitStatus(`Submission failed: ${errorData.message || response.statusText}`);
      } else {
        setSubmitStatus('Application submitted successfully.');
        setFormData(initialFormData);
      }
    } catch (error) {
      setSubmitStatus(`Submission failed: ${(error as Error).message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="app-container">
      <Header />
      <main>
        <form onSubmit={handleSubmit} className="application-form" noValidate aria-label="Application form">
          <fieldset>
            <legend>Personal Information</legend>

            <label htmlFor="firstName">First Name<span aria-hidden="true">*</span></label>
            <input
              id="firstName"
              name="firstName"
              type="text"
              value={formData.firstName}
              onChange={handleChange}
              aria-required="true"
              aria-invalid={errors.firstName ? 'true' : 'false'}
              aria-describedby={errors.firstName ? 'error-firstName' : undefined}
            />
            {errors.firstName && <div id="error-firstName" className="error">{errors.firstName}</div>}

            <label htmlFor="lastName">Last Name<span aria-hidden="true">*</span></label>
            <input
              id="lastName"
              name="lastName"
              type="text"
              value={formData.lastName}
              onChange={handleChange}
              aria-required="true"
              aria-invalid={errors.lastName ? 'true' : 'false'}
              aria-describedby={errors.lastName ? 'error-lastName' : undefined}
            />
            {errors.lastName && <div id="error-lastName" className="error">{errors.lastName}</div>}

            <label htmlFor="email">Email Address<span aria-hidden="true">*</span></label>
            <input
              id="email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              aria-required="true"
              aria-invalid={errors.email ? 'true' : 'false'}
              aria-describedby={errors.email ? 'error-email' : undefined}
            />
            {errors.email && <div id="error-email" className="error">{errors.email}</div>}
          </fieldset>

          <fieldset>
            <legend>Contact Details</legend>

            <label htmlFor="phone">Phone Number</label>
            <input
              id="phone"
              name="phone"
              type="tel"
              value={formData.phone}
              onChange={handleChange}
              aria-required="false"
            />

            <label htmlFor="address">Address</label>
            <input
              id="address"
              name="address"
              type="text"
              value={formData.address}
              onChange={handleChange}
              aria-required="false"
            />

            <label htmlFor="city">City</label>
            <input
              id="city"
              name="city"
              type="text"
              value={formData.city}
              onChange={handleChange}
              aria-required="false"
            />

            <label htmlFor="state">State / Province</label>
            <input
              id="state"
              name="state"
              type="text"
              value={formData.state}
              onChange={handleChange}
              aria-required="false"
            />

            <label htmlFor="postalCode">Postal Code</label>
            <input
              id="postalCode"
              name="postalCode"
              type="text"
              value={formData.postalCode}
              onChange={handleChange}
              aria-required="false"
            />

            <label htmlFor="country">Country</label>
            <input
              id="country"
              name="country"
              type="text"
              value={formData.country}
              onChange={handleChange}
              aria-required="false"
            />
          </fieldset>

          <div className="form-actions">
            <button type="submit" disabled={isSubmitting} aria-busy={isSubmitting}>
              {isSubmitting ? 'Submitting...' : 'Submit Application'}
            </button>
          </div>

          {submitStatus && <p role="alert" className="submit-status">{submitStatus}</p>}
        </form>
      </main>
      <Footer />
      <style>{`
        * {
          box-sizing: border-box;
        }
        body,html,#root,.app-container {
          margin: 0; padding: 0; height: 100%; font-family: Arial, sans-serif; background-color: #f7f9fc;
        }
        .app-container {
          display: flex;
          flex-direction: column;
          min-height: 100vh;
        }
        header.header {
          background-color: #003366;
          color: #fff;
          padding: 1rem 2rem;
          text-align: center;
          font-weight: 700;
          font-size: 1.5rem;
          letter-spacing: 0.05em;
        }
        footer.footer {
          background-color: #222;
          color: #ccc;
          padding: 1rem 2rem;
          text-align: center;
          font-size: 0.875rem;
          margin-top: auto;
          user-select: none;
        }
        main {
          flex-grow: 1;
          padding: 2rem;
          max-width: 700px;
          margin: 0 auto;
          width: 90%;
          background-color: #fff;
          border-radius: 8px;
          box-shadow: 0 3px 12px rgba(0,0,0,0.1);
        }
        .application-form fieldset {
          border: 1px solid #ddd;
          border-radius: 4px;
          padding: 1rem 1.5rem 2rem 1.5rem;
          margin-bottom: 1.5rem;
        }
        .application-form legend {
          font-weight: 600;
          padding: 0 0.5rem;
          font-size: 1.1rem;
          color: #222;
        }
        label {
          display: block;
          margin-bottom: 0.3rem;
          font-weight: 600;
          color: #333;
          margin-top: 1rem;
        }
        input[type="text"],
        input[type="email"],
        input[type="tel"] {
          width: 100%;
          border: 1px solid #ccc;
          border-radius: 4px;
          padding: 0.45rem 0.6rem;
          font-size: 1rem;
          transition: border-color 0.2s ease-in-out;
        }
        input[type="text"]:focus,
        input[type="email"]:focus,
        input[type="tel"]:focus {
          border-color: #0052cc;
          outline: none;
          box-shadow: 0 0 5px #b3d1ff;
        }
        .error {
          color: #d93025;
          font-size: 0.875rem;
          margin-top: 0.2rem;
        }
        .form-actions {
          margin-top: 2rem;
          text-align: right;
        }
        button {
          background-color: #0052cc;
          color: white;
          border: none;
          border-radius: 6px;
          padding: 0.8rem 1.6rem;
          font-size: 1rem;
          font-weight: 700;
          cursor: pointer;
          user-select: none;
          transition: background-color 0.3s ease;
        }
        button:disabled {
          background-color: #92a6d9;
          cursor: not-allowed;
        }
        button:not(:disabled):hover {
          background-color: #003d99;
        }
        .submit-status {
          margin-top: 1rem;
          font-weight: 600;
          color: #0052cc;
        }
        @media (max-width: 600px) {
          main {
            padding: 1.5rem 1rem;
          }
          header.header, footer.footer {
            padding: 1rem 1rem;
          }
        }
      `}</style>
    </div>
  );
};

export default App;
