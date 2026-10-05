import React, { useState } from 'react';

interface FormData {
  firstName: string;
  lastName: string;
  dateOfBirth: string;
  email: string;
  phone: string;
  address: string;
  city: string;
  stateProvince: string;
  postalCode: string;
  country: string;
  desiredPosition: string;
  startDate: string;
  employmentType: string;
  resume: File | null;
  coverLetter: File | null;
  agreeTerms: boolean;
}

const initialFormData: FormData = {
  firstName: '',
  lastName: '',
  dateOfBirth: '',
  email: '',
  phone: '',
  address: '',
  city: '',
  stateProvince: '',
  postalCode: '',
  country: '',
  desiredPosition: '',
  startDate: '',
  employmentType: '',
  resume: null,
  coverLetter: null,
  agreeTerms: false,
};

const validateEmail = (email: string) => {
  const re = /^[\w-.]+@([\w-]+\.)+[\w-]{2,4}$/;
  return re.test(email);
};

const validatePhone = (phone: string) => {
  const re = /^[+]?[(]?[0-9]{1,4}[)]?[-\s./0-9]*$/;
  return re.test(phone);
};

const ApplicationForm: React.FC = () => {
  const [form, setForm] = useState<FormData>(initialFormData);
  const [errors, setErrors] = useState<Partial<Record<keyof FormData, string>>>({});
  const [submitted, setSubmitted] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));

    setErrors((prev) => ({
      ...prev,
      [name]: undefined,
    }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, files } = e.target;
    if (!files || files.length === 0) return;
    const file = files[0];
    setForm((prev) => ({
      ...prev,
      [name]: file,
    }));
    setErrors((prev) => ({
      ...prev,
      [name]: undefined,
    }));
  };

  const validateForm = () => {
    const newErrors: Partial<Record<keyof FormData, string>> = {};

    if (!form.firstName.trim()) newErrors.firstName = 'First name is required';
    if (!form.lastName.trim()) newErrors.lastName = 'Last name is required';
    if (!form.dateOfBirth) newErrors.dateOfBirth = 'Date of birth is required';
    if (!form.email.trim()) newErrors.email = 'Email is required';
    else if (!validateEmail(form.email)) newErrors.email = 'Enter a valid email address';
    if (!form.phone.trim()) newErrors.phone = 'Phone number is required';
    else if (!validatePhone(form.phone)) newErrors.phone = 'Enter a valid phone number';
    if (!form.address.trim()) newErrors.address = 'Address is required';
    if (!form.city.trim()) newErrors.city = 'City is required';
    if (!form.stateProvince.trim()) newErrors.stateProvince = 'State/Province is required';
    if (!form.postalCode.trim()) newErrors.postalCode = 'Postal/ZIP code is required';
    if (!form.country.trim()) newErrors.country = 'Country is required';
    if (!form.desiredPosition.trim()) newErrors.desiredPosition = 'Desired position is required';
    if (!form.startDate) newErrors.startDate = 'Available start date is required';
    if (!form.employmentType) newErrors.employmentType = 'Employment type is required';
    if (!form.resume) newErrors.resume = 'Please upload your resume';
    if (!form.agreeTerms) newErrors.agreeTerms = 'You must agree to the terms';

    return newErrors;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const formErrors = validateForm();
    setErrors(formErrors);

    if (Object.keys(formErrors).length === 0) {
      setSubmitted(true);
    } else {
      setSubmitted(false);
    }
  };

  if (submitted) {
    return (
      <section className="max-w-4xl mx-auto bg-white p-8 rounded shadow">
        <h2 className="text-2xl font-semibold mb-4">Application Submitted</h2>
        <p>Thank you for your application, {form.firstName} {form.lastName}. We will review your application and contact you soon.</p>
      </section>
    );
  }

  return (
    <form onSubmit={handleSubmit} noValidate className="max-w-4xl mx-auto bg-white p-8 rounded shadow">
      <h2 className="text-2xl font-semibold mb-6">Job Application Form</h2>

      <fieldset className="mb-6 border border-gray-300 p-4 rounded">
        <legend className="text-lg font-medium mb-2">Personal Information</legend>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="firstName" className="block font-medium">
              First Name <span className="text-red-600">*</span>
            </label>
            <input
              type="text"
              id="firstName"
              name="firstName"
              value={form.firstName}
              onChange={handleChange}
              className={`mt-1 block w-full border rounded p-2 ${errors.firstName ? 'border-red-600' : 'border-gray-300'}`}
              aria-invalid={!!errors.firstName}
              aria-describedby={errors.firstName ? 'firstName-error' : undefined}
            />
            {errors.firstName && <p id="firstName-error" className="text-red-600 text-sm mt-1">{errors.firstName}</p>}
          </div>

          <div>
            <label htmlFor="lastName" className="block font-medium">
              Last Name <span className="text-red-600">*</span>
            </label>
            <input
              type="text"
              id="lastName"
              name="lastName"
              value={form.lastName}
              onChange={handleChange}
              className={`mt-1 block w-full border rounded p-2 ${errors.lastName ? 'border-red-600' : 'border-gray-300'}`}
              aria-invalid={!!errors.lastName}
              aria-describedby={errors.lastName ? 'lastName-error' : undefined}
            />
            {errors.lastName && <p id="lastName-error" className="text-red-600 text-sm mt-1">{errors.lastName}</p>}
          </div>

          <div>
            <label htmlFor="dateOfBirth" className="block font-medium">
              Date of Birth <span className="text-red-600">*</span>
            </label>
            <input
              type="date"
              id="dateOfBirth"
              name="dateOfBirth"
              value={form.dateOfBirth}
              onChange={handleChange}
              className={`mt-1 block w-full border rounded p-2 ${errors.dateOfBirth ? 'border-red-600' : 'border-gray-300'}`}
              aria-invalid={!!errors.dateOfBirth}
              aria-describedby={errors.dateOfBirth ? 'dateOfBirth-error' : undefined}
            />
            {errors.dateOfBirth && <p id="dateOfBirth-error" className="text-red-600 text-sm mt-1">{errors.dateOfBirth}</p>}
          </div>
        </div>
      </fieldset>

      <fieldset className="mb-6 border border-gray-300 p-4 rounded">
        <legend className="text-lg font-medium mb-2">Contact Details</legend>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="email" className="block font-medium">
              Email <span className="text-red-600">*</span>
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={form.email}
              onChange={handleChange}
              className={`mt-1 block w-full border rounded p-2 ${errors.email ? 'border-red-600' : 'border-gray-300'}`}
              aria-invalid={!!errors.email}
              aria-describedby={errors.email ? 'email-error' : undefined}
            />
            {errors.email && <p id="email-error" className="text-red-600 text-sm mt-1">{errors.email}</p>}
          </div>
          <div>
            <label htmlFor="phone" className="block font-medium">
              Phone Number <span className="text-red-600">*</span>
            </label>
            <input
              type="tel"
              id="phone"
              name="phone"
              value={form.phone}
              onChange={handleChange}
              className={`mt-1 block w-full border rounded p-2 ${errors.phone ? 'border-red-600' : 'border-gray-300'}`}
              aria-invalid={!!errors.phone}
              aria-describedby={errors.phone ? 'phone-error' : undefined}
            />
            {errors.phone && <p id="phone-error" className="text-red-600 text-sm mt-1">{errors.phone}</p>}
          </div>

          <div className="md:col-span-2">
            <label htmlFor="address" className="block font-medium">
              Address <span className="text-red-600">*</span>
            </label>
            <textarea
              id="address"
              name="address"
              value={form.address}
              onChange={handleChange}
              rows={2}
              className={`mt-1 block w-full border rounded p-2 resize-y ${errors.address ? 'border-red-600' : 'border-gray-300'}`}
              aria-invalid={!!errors.address}
              aria-describedby={errors.address ? 'address-error' : undefined}
            />
            {errors.address && <p id="address-error" className="text-red-600 text-sm mt-1">{errors.address}</p>}
          </div>

          <div>
            <label htmlFor="city" className="block font-medium">
              City <span className="text-red-600">*</span>
            </label>
            <input
              type="text"
              id="city"
              name="city"
              value={form.city}
              onChange={handleChange}
              className={`mt-1 block w-full border rounded p-2 ${errors.city ? 'border-red-600' : 'border-gray-300'}`}
              aria-invalid={!!errors.city}
              aria-describedby={errors.city ? 'city-error' : undefined}
            />
            {errors.city && <p id="city-error" className="text-red-600 text-sm mt-1">{errors.city}</p>}
          </div>

          <div>
            <label htmlFor="stateProvince" className="block font-medium">
              State / Province <span className="text-red-600">*</span>
            </label>
            <input
              type="text"
              id="stateProvince"
              name="stateProvince"
              value={form.stateProvince}
              onChange={handleChange}
              className={`mt-1 block w-full border rounded p-2 ${errors.stateProvince ? 'border-red-600' : 'border-gray-300'}`}
              aria-invalid={!!errors.stateProvince}
              aria-describedby={errors.stateProvince ? 'stateProvince-error' : undefined}
            />
            {errors.stateProvince && <p id="stateProvince-error" className="text-red-600 text-sm mt-1">{errors.stateProvince}</p>}
          </div>

          <div>
            <label htmlFor="postalCode" className="block font-medium">
              Postal / ZIP Code <span className="text-red-600">*</span>
            </label>
            <input
              type="text"
              id="postalCode"
              name="postalCode"
              value={form.postalCode}
              onChange={handleChange}
              className={`mt-1 block w-full border rounded p-2 ${errors.postalCode ? 'border-red-600' : 'border-gray-300'}`}
              aria-invalid={!!errors.postalCode}
              aria-describedby={errors.postalCode ? 'postalCode-error' : undefined}
            />
            {errors.postalCode && <p id="postalCode-error" className="text-red-600 text-sm mt-1">{errors.postalCode}</p>}
          </div>

          <div>
            <label htmlFor="country" className="block font-medium">
              Country <span className="text-red-600">*</span>
            </label>
            <input
              type="text"
              id="country"
              name="country"
              value={form.country}
              onChange={handleChange}
              className={`mt-1 block w-full border rounded p-2 ${errors.country ? 'border-red-600' : 'border-gray-300'}`}
              aria-invalid={!!errors.country}
              aria-describedby={errors.country ? 'country-error' : undefined}
            />
            {errors.country && <p id="country-error" className="text-red-600 text-sm mt-1">{errors.country}</p>}
          </div>
        </div>
      </fieldset>

      <fieldset className="mb-6 border border-gray-300 p-4 rounded">
        <legend className="text-lg font-medium mb-2">Job Details</legend>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="desiredPosition" className="block font-medium">
              Desired Position <span className="text-red-600">*</span>
            </label>
            <input
              type="text"
              id="desiredPosition"
              name="desiredPosition"
              value={form.desiredPosition}
              onChange={handleChange}
              className={`mt-1 block w-full border rounded p-2 ${errors.desiredPosition ? 'border-red-600' : 'border-gray-300'}`}
              aria-invalid={!!errors.desiredPosition}
              aria-describedby={errors.desiredPosition ? 'desiredPosition-error' : undefined}
            />
            {errors.desiredPosition && <p id="desiredPosition-error" className="text-red-600 text-sm mt-1">{errors.desiredPosition}</p>}
          </div>

          <div>
            <label htmlFor="startDate" className="block font-medium">
              Available Start Date <span className="text-red-600">*</span>
            </label>
            <input
              type="date"
              id="startDate"
              name="startDate"
              value={form.startDate}
              onChange={handleChange}
              className={`mt-1 block w-full border rounded p-2 ${errors.startDate ? 'border-red-600' : 'border-gray-300'}`}
              aria-invalid={!!errors.startDate}
              aria-describedby={errors.startDate ? 'startDate-error' : undefined}
            />
            {errors.startDate && <p id="startDate-error" className="text-red-600 text-sm mt-1">{errors.startDate}</p>}
          </div>

          <div>
            <label htmlFor="employmentType" className="block font-medium">
              Employment Type <span className="text-red-600">*</span>
            </label>
            <select
              id="employmentType"
              name="employmentType"
              value={form.employmentType}
              onChange={handleChange}
              className={`mt-1 block w-full border rounded p-2 ${errors.employmentType ? 'border-red-600' : 'border-gray-300'}`}
              aria-invalid={!!errors.employmentType}
              aria-describedby={errors.employmentType ? 'employmentType-error' : undefined}
            >
              <option value="">Select one</option>
              <option value="full-time">Full-Time</option>
              <option value="part-time">Part-Time</option>
              <option value="contract">Contract</option>
              <option value="internship">Internship</option>
            </select>
            {errors.employmentType && <p id="employmentType-error" className="text-red-600 text-sm mt-1">{errors.employmentType}</p>}
          </div>
        </div>
      </fieldset>

      <fieldset className="mb-6 border border-gray-300 p-4 rounded">
        <legend className="text-lg font-medium mb-2">Attachments</legend>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="resume" className="block font-medium">
              Resume (PDF or DOC)<span className="text-red-600">*</span>
            </label>
            <input
              type="file"
              id="resume"
              name="resume"
              accept="application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              onChange={handleFileChange}
              className={`mt-1 block w-full border rounded p-2 ${errors.resume ? 'border-red-600' : 'border-gray-300'}`}
              aria-invalid={!!errors.resume}
              aria-describedby={errors.resume ? 'resume-error' : undefined}
            />
            {errors.resume && <p id="resume-error" className="text-red-600 text-sm mt-1">{errors.resume}</p>}
          </div>

          <div>
            <label htmlFor="coverLetter" className="block font-medium">
              Cover Letter (Optional)
            </label>
            <input
              type="file"
              id="coverLetter"
              name="coverLetter"
              accept="application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              onChange={handleFileChange}
              className="mt-1 block w-full border border-gray-300 rounded p-2"
            />
          </div>
        </div>
      </fieldset>

      <fieldset className="mb-6">
        <label className="inline-flex items-center">
          <input
            type="checkbox"
            name="agreeTerms"
            checked={form.agreeTerms}
            onChange={handleChange}
            className={`form-checkbox h-5 w-5 text-blue-600 ${errors.agreeTerms ? 'border-red-600' : ''}`}
            aria-invalid={!!errors.agreeTerms}
            aria-describedby={errors.agreeTerms ? 'agreeTerms-error' : undefined}
          />
          <span className="ml-2">
            I certify that the information given in this application is true and complete to the best of my knowledge. <span className="text-red-600">*</span>
          </span>
        </label>
        {errors.agreeTerms && <p id="agreeTerms-error" className="text-red-600 text-sm mt-1">{errors.agreeTerms}</p>}
      </fieldset>

      <button
        type="submit"
        className="bg-blue-800 text-white font-semibold py-2 px-6 rounded hover:bg-blue-900 focus:outline-none focus:ring-4 focus:ring-blue-400"
      >
        Submit Application
      </button>
    </form>
  );
};

export default ApplicationForm;
