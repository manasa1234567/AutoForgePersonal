import React, { useState } from 'react';

interface FormData {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  dateOfBirth: string;
  address: string;
  city: string;
  state: string;
  zipCode: string;
  country: string;
  highestEducation: string;
  employmentStatus: string;
  resumeLink: string;
  agreeToTerms: boolean;
}

const initialFormData: FormData = {
  firstName: '',
  lastName: '',
  email: '',
  phone: '',
  dateOfBirth: '',
  address: '',
  city: '',
  state: '',
  zipCode: '',
  country: '',
  highestEducation: '',
  employmentStatus: '',
  resumeLink: '',
  agreeToTerms: false,
};

const ApplicationForm: React.FC = () => {
  const [formData, setFormData] = useState<FormData>(initialFormData);
  const [errors, setErrors] = useState<Partial<Record<keyof FormData, string>>>({});
  const [submitted, setSubmitted] = useState(false);

  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof FormData, string>> = {};

    if (!formData.firstName.trim()) newErrors.firstName = 'First name is required';
    if (!formData.lastName.trim()) newErrors.lastName = 'Last name is required';

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[\w-.]+@[\w-]+(\.[\w-]+)+$/.test(formData.email)) {
      newErrors.email = 'Email address is invalid';
    }

    if (formData.phone.trim()) {
      // Basic phone validation
      if (!/^\+?[0-9\-() ]{7,20}$/.test(formData.phone)) {
        newErrors.phone = 'Phone number is invalid';
      }
    }

    if (!formData.dateOfBirth) {
      newErrors.dateOfBirth = 'Date of birth is required';
    }

    if (!formData.address.trim()) newErrors.address = 'Address is required';
    if (!formData.city.trim()) newErrors.city = 'City is required';
    if (!formData.state.trim()) newErrors.state = 'State/Province is required';
    if (!formData.zipCode.trim()) newErrors.zipCode = 'ZIP/Postal code is required';
    if (!formData.country.trim()) newErrors.country = 'Country is required';

    if (!formData.highestEducation) newErrors.highestEducation = 'Please select your highest education level';
    if (!formData.employmentStatus) newErrors.employmentStatus = 'Please select your employment status';

    if (!formData.agreeToTerms) newErrors.agreeToTerms = 'You must agree to the terms and conditions';

    setErrors(newErrors);

    return Object.keys(newErrors).length === 0;
  };

  const handleChange = <K extends keyof FormData>(field: K, value: FormData[K]) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setErrors(prev => ({ ...prev, [field]: undefined }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validate()) {
      // Currently no backend integration; mock submission success
      setSubmitted(true);
    } else {
      setSubmitted(false);
    }
  };

  return (
    <section aria-labelledby="form-title" className="form-section">
      <h2 id="form-title" tabIndex={-1} className="form-title">Application Form</h2>
      {submitted && (
        <div role="alert" className="submit-success">
          <p>Thank you for your application. We have received your information.</p>
        </div>
      )}
      <form noValidate onSubmit={handleSubmit} aria-describedby="form-instructions">
        <p id="form-instructions" className="form-instructions">
          Please fill out all required fields marked with * and submit your application.
        </p>

        <fieldset>
          <legend>Personal Information</legend>

          <label htmlFor="firstName">
            First Name *
            <input
              type="text"
              id="firstName"
              name="firstName"
              value={formData.firstName}
              onChange={e => handleChange('firstName', e.target.value)}
              aria-invalid={errors.firstName ? 'true' : undefined}
              aria-describedby={errors.firstName ? 'firstName-error' : undefined}
              required
            />
          </label>
          {errors.firstName && <p className="input-error" id="firstName-error">{errors.firstName}</p>}

          <label htmlFor="lastName">
            Last Name *
            <input
              type="text"
              id="lastName"
              name="lastName"
              value={formData.lastName}
              onChange={e => handleChange('lastName', e.target.value)}
              aria-invalid={errors.lastName ? 'true' : undefined}
              aria-describedby={errors.lastName ? 'lastName-error' : undefined}
              required
            />
          </label>
          {errors.lastName && <p className="input-error" id="lastName-error">{errors.lastName}</p>}

          <label htmlFor="email">
            Email *
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={e => handleChange('email', e.target.value)}
              aria-invalid={errors.email ? 'true' : undefined}
              aria-describedby={errors.email ? 'email-error' : undefined}
              required
            />
          </label>
          {errors.email && <p className="input-error" id="email-error">{errors.email}</p>}

          <label htmlFor="phone">
            Phone Number
            <input
              type="tel"
              id="phone"
              name="phone"
              value={formData.phone}
              onChange={e => handleChange('phone', e.target.value)}
              aria-invalid={errors.phone ? 'true' : undefined}
              aria-describedby={errors.phone ? 'phone-error' : undefined}
            />
          </label>
          {errors.phone && <p className="input-error" id="phone-error">{errors.phone}</p>}

          <label htmlFor="dateOfBirth">
            Date of Birth *
            <input
              type="date"
              id="dateOfBirth"
              name="dateOfBirth"
              value={formData.dateOfBirth}
              onChange={e => handleChange('dateOfBirth', e.target.value)}
              aria-invalid={errors.dateOfBirth ? 'true' : undefined}
              aria-describedby={errors.dateOfBirth ? 'dateOfBirth-error' : undefined}
              required
              max={new Date().toISOString().split('T')[0]}
            />
          </label>
          {errors.dateOfBirth && <p className="input-error" id="dateOfBirth-error">{errors.dateOfBirth}</p>}
        </fieldset>

        <fieldset>
          <legend>Address</legend>
          <label htmlFor="address">
            Street Address *
            <input
              type="text"
              id="address"
              name="address"
              value={formData.address}
              onChange={e => handleChange('address', e.target.value)}
              aria-invalid={errors.address ? 'true' : undefined}
              aria-describedby={errors.address ? 'address-error' : undefined}
              required
            />
          </label>
          {errors.address && <p className="input-error" id="address-error">{errors.address}</p>}

          <label htmlFor="city">
            City *
            <input
              type="text"
              id="city"
              name="city"
              value={formData.city}
              onChange={e => handleChange('city', e.target.value)}
              aria-invalid={errors.city ? 'true' : undefined}
              aria-describedby={errors.city ? 'city-error' : undefined}
              required
            />
          </label>
          {errors.city && <p className="input-error" id="city-error">{errors.city}</p>}

          <label htmlFor="state">
            State/Province *
            <input
              type="text"
              id="state"
              name="state"
              value={formData.state}
              onChange={e => handleChange('state', e.target.value)}
              aria-invalid={errors.state ? 'true' : undefined}
              aria-describedby={errors.state ? 'state-error' : undefined}
              required
            />
          </label>
          {errors.state && <p className="input-error" id="state-error">{errors.state}</p>}

          <label htmlFor="zipCode">
            ZIP/Postal Code *
            <input
              type="text"
              id="zipCode"
              name="zipCode"
              value={formData.zipCode}
              onChange={e => handleChange('zipCode', e.target.value)}
              aria-invalid={errors.zipCode ? 'true' : undefined}
              aria-describedby={errors.zipCode ? 'zipCode-error' : undefined}
              required
              pattern="[A-Za-z0-9 -]{3,10}"
              title="Enter a valid ZIP or postal code"
            />
          </label>
          {errors.zipCode && <p className="input-error" id="zipCode-error">{errors.zipCode}</p>}

          <label htmlFor="country">
            Country *
            <select
              id="country"
              name="country"
              value={formData.country}
              onChange={e => handleChange('country', e.target.value)}
              aria-invalid={errors.country ? 'true' : undefined}
              aria-describedby={errors.country ? 'country-error' : undefined}
              required
            >
              <option value="">Select a country</option>
              <option value="United States">United States</option>
              <option value="Canada">Canada</option>
              <option value="United Kingdom">United Kingdom</option>
              <option value="Australia">Australia</option>
              <option value="Other">Other</option>
            </select>
          </label>
          {errors.country && <p className="input-error" id="country-error">{errors.country}</p>}
        </fieldset>

        <fieldset>
          <legend>Education and Employment</legend>

          <label htmlFor="highestEducation">
            Highest Level of Education *
            <select
              id="highestEducation"
              name="highestEducation"
              value={formData.highestEducation}
              onChange={e => handleChange('highestEducation', e.target.value)}
              aria-invalid={errors.highestEducation ? 'true' : undefined}
              aria-describedby={errors.highestEducation ? 'highestEducation-error' : undefined}
              required
            >
              <option value="">Select education level</option>
              <option value="High School">High School</option>
              <option value="Associate Degree">Associate Degree</option>
              <option value="Bachelor's Degree">Bachelor's Degree</option>
              <option value="Master's Degree">Master's Degree</option>
              <option value="Doctorate">Doctorate</option>
              <option value="Other">Other</option>
            </select>
          </label>
          {errors.highestEducation && <p className="input-error" id="highestEducation-error">{errors.highestEducation}</p>}

          <label htmlFor="employmentStatus">
            Current Employment Status *
            <select
              id="employmentStatus"
              name="employmentStatus"
              value={formData.employmentStatus}
              onChange={e => handleChange('employmentStatus', e.target.value)}
              aria-invalid={errors.employmentStatus ? 'true' : undefined}
              aria-describedby={errors.employmentStatus ? 'employmentStatus-error' : undefined}
              required
            >
              <option value="">Select employment status</option>
              <option value="Employed Full-time">Employed Full-time</option>
              <option value="Employed Part-time">Employed Part-time</option>
              <option value="Unemployed">Unemployed</option>
              <option value="Student">Student</option>
              <option value="Self-employed">Self-employed</option>
              <option value="Retired">Retired</option>
            </select>
          </label>
          {errors.employmentStatus && <p className="input-error" id="employmentStatus-error">{errors.employmentStatus}</p>}

          <label htmlFor="resumeLink">
            Resume or Portfolio Link
            <input
              type="url"
              id="resumeLink"
              name="resumeLink"
              value={formData.resumeLink}
              onChange={e => handleChange('resumeLink', e.target.value)}
              placeholder="https://"
              aria-describedby="resumeHelp"
            />
          </label>
          <small id="resumeHelp" className="input-help">
            Optional. Provide a URL to your resume or portfolio.
          </small>
        </fieldset>

        <fieldset>
          <legend>Consent</legend>
          <label htmlFor="agreeToTerms" className="checkbox-label">
            <input
              type="checkbox"
              id="agreeToTerms"
              name="agreeToTerms"
              checked={formData.agreeToTerms}
              onChange={e => handleChange('agreeToTerms', e.target.checked)}
              aria-invalid={errors.agreeToTerms ? 'true' : undefined}
              aria-describedby={errors.agreeToTerms ? 'agreeToTerms-error' : undefined}
              required
            />
            I agree to the terms and conditions *
          </label>
          {errors.agreeToTerms && <p className="input-error" id="agreeToTerms-error">{errors.agreeToTerms}</p>}
        </fieldset>

        <button type="submit" className="submit-button" aria-label="Submit Application Form">
          Submit Application
        </button>
      </form>
    </section>
  );
};

export default ApplicationForm;
