import React, { useState } from 'react';

interface FormData {
  firstName: string;
  lastName: string;
  dateOfBirth: string;
  email: string;
  phone: string;
  addressLine1: string;
  addressLine2: string;
  city: string;
  stateProvince: string;
  postalCode: string;
  country: string;
  signature: string;
}

interface FormErrors {
  [key: string]: string;
}

const initialFormData: FormData = {
  firstName: '',
  lastName: '',
  dateOfBirth: '',
  email: '',
  phone: '',
  addressLine1: '',
  addressLine2: '',
  city: '',
  stateProvince: '',
  postalCode: '',
  country: '',
  signature: '',
};

const ApplicationForm: React.FC = () => {
  const [formData, setFormData] = useState<FormData>(initialFormData);
  const [errors, setErrors] = useState<FormErrors>({});
  const [submitSucceeded, setSubmitSucceeded] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080';

  const validate = (): FormErrors => {
    const newErrors: FormErrors = {};
    if (!formData.firstName.trim()) newErrors.firstName = 'First name is required.';
    if (!formData.lastName.trim()) newErrors.lastName = 'Last name is required.';
    if (!formData.dateOfBirth) {
      newErrors.dateOfBirth = 'Date of birth is required.';
    } else {
      const dob = new Date(formData.dateOfBirth);
      if (isNaN(dob.getTime())) {
        newErrors.dateOfBirth = 'Date of birth must be a valid date.';
      }
    }
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required.';
    } else {
      const emailRegex = /^[\w-.]+@([\w-]+\.)+[\w-]{2,4}$/;
      if (!emailRegex.test(formData.email)) {
        newErrors.email = 'Email is invalid.';
      }
    }
    if (!formData.phone.trim()) newErrors.phone = 'Phone number is required.';
    if (!formData.addressLine1.trim()) newErrors.addressLine1 = 'Address line 1 is required.';
    if (!formData.city.trim()) newErrors.city = 'City is required.';
    if (!formData.stateProvince.trim()) newErrors.stateProvince = 'State/Province is required.';
    if (!formData.postalCode.trim()) newErrors.postalCode = 'Postal code is required.';
    if (!formData.country.trim()) newErrors.country = 'Country is required.';
    if (!formData.signature.trim() || formData.signature.length < 3)
      newErrors.signature = 'Signature is required (type your full name).';

    return newErrors;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitError(null);
    const validationErrors = validate();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      setSubmitSucceeded(false);
      return;
    }
    setErrors({});

    try {
      const response = await fetch(`${API_URL}/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          first_name: formData.firstName,
          last_name: formData.lastName,
          date_of_birth: formData.dateOfBirth,
          email: formData.email,
          phone: formData.phone,
          address_line1: formData.addressLine1,
          address_line2: formData.addressLine2,
          city: formData.city,
          state_province: formData.stateProvince,
          postal_code: formData.postalCode,
          country: formData.country,
          signature: formData.signature,
        }),
      });

      if (!response.ok) {
        throw new Error(`Submission failed with status ${response.status}`);
      }
      setSubmitSucceeded(true);
      setFormData(initialFormData);
    } catch (error: any) {
      setSubmitError(error.message || 'Submission failed');
      setSubmitSucceeded(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} noValidate className="application-form" aria-label="Application Form">
      <fieldset>
        <legend>Personal Information</legend>
        <label htmlFor="firstName">First Name *</label>
        <input
          id="firstName"
          name="firstName"
          type="text"
          value={formData.firstName}
          onChange={handleChange}
          aria-invalid={errors.firstName ? 'true' : 'false'}
          aria-describedby={errors.firstName ? 'firstName-error' : undefined}
          required
        />
        {errors.firstName && <span id="firstName-error" role="alert" className="error-message">{errors.firstName}</span>}

        <label htmlFor="lastName">Last Name *</label>
        <input
          id="lastName"
          name="lastName"
          type="text"
          value={formData.lastName}
          onChange={handleChange}
          aria-invalid={errors.lastName ? 'true' : 'false'}
          aria-describedby={errors.lastName ? 'lastName-error' : undefined}
          required
        />
        {errors.lastName && <span id="lastName-error" role="alert" className="error-message">{errors.lastName}</span>}

        <label htmlFor="dateOfBirth">Date of Birth *</label>
        <input
          id="dateOfBirth"
          name="dateOfBirth"
          type="date"
          value={formData.dateOfBirth}
          onChange={handleChange}
          aria-invalid={errors.dateOfBirth ? 'true' : 'false'}
          aria-describedby={errors.dateOfBirth ? 'dateOfBirth-error' : undefined}
          required
        />
        {errors.dateOfBirth && <span id="dateOfBirth-error" role="alert" className="error-message">{errors.dateOfBirth}</span>}
      </fieldset>

      <fieldset>
        <legend>Contact Information</legend>
        <label htmlFor="email">Email *</label>
        <input
          id="email"
          name="email"
          type="email"
          value={formData.email}
          onChange={handleChange}
          aria-invalid={errors.email ? 'true' : 'false'}
          aria-describedby={errors.email ? 'email-error' : undefined}
          required
        />
        {errors.email && <span id="email-error" role="alert" className="error-message">{errors.email}</span>}

        <label htmlFor="phone">Phone Number *</label>
        <input
          id="phone"
          name="phone"
          type="tel"
          value={formData.phone}
          onChange={handleChange}
          aria-invalid={errors.phone ? 'true' : 'false'}
          aria-describedby={errors.phone ? 'phone-error' : undefined}
          required
        />
        {errors.phone && <span id="phone-error" role="alert" className="error-message">{errors.phone}</span>}
      </fieldset>

      <fieldset>
        <legend>Address</legend>
        <label htmlFor="addressLine1">Address Line 1 *</label>
        <input
          id="addressLine1"
          name="addressLine1"
          type="text"
          value={formData.addressLine1}
          onChange={handleChange}
          aria-invalid={errors.addressLine1 ? 'true' : 'false'}
          aria-describedby={errors.addressLine1 ? 'addressLine1-error' : undefined}
          required
        />
        {errors.addressLine1 && <span id="addressLine1-error" role="alert" className="error-message">{errors.addressLine1}</span>}

        <label htmlFor="addressLine2">Address Line 2</label>
        <input
          id="addressLine2"
          name="addressLine2"
          type="text"
          value={formData.addressLine2}
          onChange={handleChange}
        />

        <label htmlFor="city">City *</label>
        <input
          id="city"
          name="city"
          type="text"
          value={formData.city}
          onChange={handleChange}
          aria-invalid={errors.city ? 'true' : 'false'}
          aria-describedby={errors.city ? 'city-error' : undefined}
          required
        />
        {errors.city && <span id="city-error" role="alert" className="error-message">{errors.city}</span>}

        <label htmlFor="stateProvince">State/Province *</label>
        <input
          id="stateProvince"
          name="stateProvince"
          type="text"
          value={formData.stateProvince}
          onChange={handleChange}
          aria-invalid={errors.stateProvince ? 'true' : 'false'}
          aria-describedby={errors.stateProvince ? 'stateProvince-error' : undefined}
          required
        />
        {errors.stateProvince && <span id="stateProvince-error" role="alert" className="error-message">{errors.stateProvince}</span>}

        <label htmlFor="postalCode">Postal Code *</label>
        <input
          id="postalCode"
          name="postalCode"
          type="text"
          value={formData.postalCode}
          onChange={handleChange}
          aria-invalid={errors.postalCode ? 'true' : 'false'}
          aria-describedby={errors.postalCode ? 'postalCode-error' : undefined}
          required
        />
        {errors.postalCode && <span id="postalCode-error" role="alert" className="error-message">{errors.postalCode}</span>}

        <label htmlFor="country">Country *</label>
        <input
          id="country"
          name="country"
          type="text"
          value={formData.country}
          onChange={handleChange}
          aria-invalid={errors.country ? 'true' : 'false'}
          aria-describedby={errors.country ? 'country-error' : undefined}
          required
        />
        {errors.country && <span id="country-error" role="alert" className="error-message">{errors.country}</span>}
      </fieldset>

      <fieldset>
        <legend>Signature</legend>
        <p>Type your full name to sign *</p>
        <input
          id="signature"
          name="signature"
          type="text"
          value={formData.signature}
          onChange={handleChange}
          aria-invalid={errors.signature ? 'true' : 'false'}
          aria-describedby={errors.signature ? 'signature-error' : undefined}
          required
        />
        {errors.signature && <span id="signature-error" role="alert" className="error-message">{errors.signature}</span>}
      </fieldset>

      <button type="submit">Submit Application</button>

      {submitSucceeded && <p className="success-message" role="status">Application submitted successfully.</p>}
      {submitError && <p className="error-message" role="alert">{submitError}</p>}
    </form>
  );
};

export default ApplicationForm;
