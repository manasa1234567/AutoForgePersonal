import React from 'react';
import { useForm, SubmitHandler } from 'react-hook-form';
import './ApplicationForm.css';

interface IFormInput {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  dateOfBirth: string;
  gender: string;
  address: string;
  city: string;
  state: string;
  postalCode: string;
  country: string;
  position: string;
  expectedSalary: number;
  startDate: string;
  resume: FileList;
  coverLetter: string;
  agreeToTerms: boolean;
}

const GENDER_OPTIONS = [
  { value: '', label: 'Select...' },
  { value: 'male', label: 'Male' },
  { value: 'female', label: 'Female' },
  { value: 'other', label: 'Other' },
  { value: 'preferNotSay', label: 'Prefer not to say' },
];

const ApplicationForm: React.FC = () => {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<IFormInput>({ mode: 'onTouched' });

  const onSubmit: SubmitHandler<IFormInput> = async (data) => {
    // For demonstration, just log the form data, including files.
    // Normally, form data would be sent to the backend via fetch or axios.
    const formData = new FormData();
    Object.entries(data).forEach(([key, value]) => {
      if (key === 'resume' && value.length > 0) {
        formData.append(key, value[0]);
      } else {
        formData.append(key, String(value));
      }
    });

    try {
      const res = await fetch('/api/applications', {
        method: 'POST',
        body: formData,
      });
      if (res.ok) {
        alert('Application submitted successfully.');
      } else {
        alert('Failed to submit application. Please try again later.');
      }
    } catch (error) {
      alert('Failed to submit application, an error occurred.');
    }
  };

  return (
    <form className="application-form" onSubmit={handleSubmit(onSubmit)} noValidate>
      <section aria-labelledby="personalInformationTitle" className="form-section">
        <h2 id="personalInformationTitle">Personal Information</h2>

        <div className="form-group">
          <label htmlFor="firstName">First Name *</label>
          <input
            id="firstName"
            type="text"
            {...register('firstName', { required: 'First name is required' })}
            aria-invalid={errors.firstName ? 'true' : 'false'}
          />
          {errors.firstName && <p className="error-message">{errors.firstName.message}</p>}
        </div>

        <div className="form-group">
          <label htmlFor="lastName">Last Name *</label>
          <input
            id="lastName"
            type="text"
            {...register('lastName', { required: 'Last name is required' })}
            aria-invalid={errors.lastName ? 'true' : 'false'}
          />
          {errors.lastName && <p className="error-message">{errors.lastName.message}</p>}
        </div>

        <div className="form-group">
          <label htmlFor="email">Email *</label>
          <input
            id="email"
            type="email"
            {...register('email', {
              required: 'Email is required',
              pattern: {
                value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                message: 'Invalid email address',
              },
            })}
            aria-invalid={errors.email ? 'true' : 'false'}
          />
          {errors.email && <p className="error-message">{errors.email.message}</p>}
        </div>

        <div className="form-group">
          <label htmlFor="phone">Phone *</label>
          <input
            id="phone"
            type="tel"
            {...register('phone', {
              required: 'Phone number is required',
              pattern: {
                value: /^\+?[0-9\-\s]{7,15}$/,
                message: 'Invalid phone number',
              },
            })}
            aria-invalid={errors.phone ? 'true' : 'false'}
            placeholder="e.g. +1234567890"
          />
          {errors.phone && <p className="error-message">{errors.phone.message}</p>}
        </div>

        <div className="form-group">
          <label htmlFor="dateOfBirth">Date of Birth *</label>
          <input
            id="dateOfBirth"
            type="date"
            {...register('dateOfBirth', { required: 'Date of birth is required' })}
            aria-invalid={errors.dateOfBirth ? 'true' : 'false'}
          />
          {errors.dateOfBirth && <p className="error-message">{errors.dateOfBirth.message}</p>}
        </div>

        <div className="form-group">
          <label htmlFor="gender">Gender *</label>
          <select
            id="gender"
            {...register('gender', { required: 'Gender selection is required' })}
            aria-invalid={errors.gender ? 'true' : 'false'}
          >
            {GENDER_OPTIONS.map(({ value, label }) => (
              <option key={value} value={value} disabled={value === ''}>
                {label}
              </option>
            ))}
          </select>
          {errors.gender && <p className="error-message">{errors.gender.message}</p>}
        </div>
      </section>

      <section aria-labelledby="addressInformationTitle" className="form-section">
        <h2 id="addressInformationTitle">Address Information</h2>

        <div className="form-group">
          <label htmlFor="address">Street Address *</label>
          <input
            id="address"
            type="text"
            {...register('address', { required: 'Address is required' })}
            aria-invalid={errors.address ? 'true' : 'false'}
          />
          {errors.address && <p className="error-message">{errors.address.message}</p>}
        </div>

        <div className="form-group">
          <label htmlFor="city">City *</label>
          <input
            id="city"
            type="text"
            {...register('city', { required: 'City is required' })}
            aria-invalid={errors.city ? 'true' : 'false'}
          />
          {errors.city && <p className="error-message">{errors.city.message}</p>}
        </div>

        <div className="form-group">
          <label htmlFor="state">State/Province *</label>
          <input
            id="state"
            type="text"
            {...register('state', { required: 'State/Province is required' })}
            aria-invalid={errors.state ? 'true' : 'false'}
          />
          {errors.state && <p className="error-message">{errors.state.message}</p>}
        </div>

        <div className="form-group">
          <label htmlFor="postalCode">Postal Code *</label>
          <input
            id="postalCode"
            type="text"
            {...register('postalCode', { required: 'Postal Code is required' })}
            aria-invalid={errors.postalCode ? 'true' : 'false'}
          />
          {errors.postalCode && <p className="error-message">{errors.postalCode.message}</p>}
        </div>

        <div className="form-group">
          <label htmlFor="country">Country *</label>
          <input
            id="country"
            type="text"
            {...register('country', { required: 'Country is required' })}
            aria-invalid={errors.country ? 'true' : 'false'}
          />
          {errors.country && <p className="error-message">{errors.country.message}</p>}
        </div>
      </section>

      <section aria-labelledby="jobInformationTitle" className="form-section">
        <h2 id="jobInformationTitle">Job Information</h2>

        <div className="form-group">
          <label htmlFor="position">Position Applied For *</label>
          <input
            id="position"
            type="text"
            {...register('position', { required: 'Position applied for is required' })}
            aria-invalid={errors.position ? 'true' : 'false'}
          />
          {errors.position && <p className="error-message">{errors.position.message}</p>}
        </div>

        <div className="form-group">
          <label htmlFor="expectedSalary">Expected Salary ($) *</label>
          <input
            id="expectedSalary"
            type="number"
            step="0.01"
            {...register('expectedSalary', {
              required: 'Expected salary is required',
              min: { value: 0, message: 'Expected salary must be positive' },
            })}
            aria-invalid={errors.expectedSalary ? 'true' : 'false'}
          />
          {errors.expectedSalary && <p className="error-message">{errors.expectedSalary.message}</p>}
        </div>

        <div className="form-group">
          <label htmlFor="startDate">Available Start Date *</label>
          <input
            id="startDate"
            type="date"
            {...register('startDate', { required: 'Available start date is required' })}
            aria-invalid={errors.startDate ? 'true' : 'false'}
          />
          {errors.startDate && <p className="error-message">{errors.startDate.message}</p>}
        </div>
      </section>

      <section aria-labelledby="documentsTitle" className="form-section">
        <h2 id="documentsTitle">Supporting Documents</h2>

        <div className="form-group">
          <label htmlFor="resume">Resume (PDF, DOC, DOCX) *</label>
          <input
            id="resume"
            type="file"
            accept="application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            {...register('resume', { required: 'Resume upload is required' })}
            aria-invalid={errors.resume ? 'true' : 'false'}
          />
          {errors.resume && <p className="error-message">{errors.resume.message}</p>}
        </div>

        <div className="form-group">
          <label htmlFor="coverLetter">Cover Letter</label>
          <textarea id="coverLetter" {...register('coverLetter')} rows={5} />
        </div>
      </section>

      <section className="form-section agreement-section">
        <div className="form-group checkbox-group">
          <input
            id="agreeToTerms"
            type="checkbox"
            {...register('agreeToTerms', { required: 'You must agree to the terms' })}
            aria-invalid={errors.agreeToTerms ? 'true' : 'false'}
          />
          <label htmlFor="agreeToTerms">
            I agree to the <a href="#" target="_blank" rel="noopener noreferrer">terms and conditions</a> *</label>
        </div>
        {errors.agreeToTerms && <p className="error-message">{errors.agreeToTerms.message}</p>}
      </section>

      <button type="submit" disabled={isSubmitting} className="submit-button">
        {isSubmitting ? 'Submitting...' : 'Submit Application'}
      </button>
    </form>
  );
};

export default ApplicationForm;
