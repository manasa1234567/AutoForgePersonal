import React from 'react';
import { useForm, Controller } from 'react-hook-form';

interface FormData {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  address: string;
  city: string;
  state: string;
  zip: string;
  country: string;
  dateOfBirth: string;
  gender: string;
  resume: FileList | null;
  consent: boolean;
}

const states = ["", "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"];

export default function ApplicationForm() {
  const { register, handleSubmit, watch, control, formState: { errors, isSubmitting, isSubmitSuccessful }, reset } = useForm<FormData>({
    defaultValues: {
      gender: '',
      consent: false
    }
  });

  const onSubmit = async (data: FormData) => {
    // For demo only: log to console
    // Normally would POST to backend API endpoint here
    console.log('Form Submitted Data:', data);
    alert('Application submitted successfully!');
    reset();
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate aria-label="Application form" className="max-w-3xl mx-auto bg-white shadow-md rounded px-8 py-10">
      <h2 className="text-xl font-semibold mb-6 text-gray-900">Personal Information</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label htmlFor="firstName" className="block text-gray-700 font-medium mb-1">First Name <span className="text-red-600">*</span></label>
          <input id="firstName" type="text" {...register('firstName', { required: 'First name is required' })} 
                 className={`w-full border rounded px-3 py-2 ${errors.firstName ? 'border-red-600' : 'border-gray-300'} focus:outline-none focus:ring-2 focus:ring-indigo-500`} />
          {errors.firstName && <p role="alert" className="text-red-600 text-sm mt-1">{errors.firstName.message}</p>}
        </div>

        <div>
          <label htmlFor="lastName" className="block text-gray-700 font-medium mb-1">Last Name <span className="text-red-600">*</span></label>
          <input id="lastName" type="text" {...register('lastName', { required: 'Last name is required' })} 
                 className={`w-full border rounded px-3 py-2 ${errors.lastName ? 'border-red-600' : 'border-gray-300'} focus:outline-none focus:ring-2 focus:ring-indigo-500`} />
          {errors.lastName && <p role="alert" className="text-red-600 text-sm mt-1">{errors.lastName.message}</p>}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
        <div>
          <label htmlFor="email" className="block text-gray-700 font-medium mb-1">Email Address <span className="text-red-600">*</span></label>
          <input id="email" type="email" {...register('email', {
            required: 'Email is required',
            pattern: { value: /^[^@\s]+@[^@\s]+\.[^@\s]+$/, message: 'Invalid email address' }
          })} 
                 className={`w-full border rounded px-3 py-2 ${errors.email ? 'border-red-600' : 'border-gray-300'} focus:outline-none focus:ring-2 focus:ring-indigo-500`} />
          {errors.email && <p role="alert" className="text-red-600 text-sm mt-1">{errors.email.message}</p>}
        </div>

        <div>
          <label htmlFor="phone" className="block text-gray-700 font-medium mb-1">Phone Number</label>
          <input id="phone" type="tel" {...register('phone', {
            pattern: { value: /^(\+?\d{1,4}[-.\s]?)?(\(?\d{3}\)?[-.\s]?){1,2}\d{4}$/, message: 'Invalid phone number' }
          })} 
                 className={`w-full border rounded px-3 py-2 ${errors.phone ? 'border-red-600' : 'border-gray-300'} focus:outline-none focus:ring-2 focus:ring-indigo-500`} 
                 placeholder="Optional" />
          {errors.phone && <p role="alert" className="text-red-600 text-sm mt-1">{errors.phone.message}</p>}
        </div>
      </div>

      <fieldset className="mt-8">
        <legend className="text-xl font-semibold mb-4 text-gray-900">Address</legend>

        <div className="mb-6">
          <label htmlFor="address" className="block text-gray-700 font-medium mb-1">Street Address <span className="text-red-600">*</span></label>
          <input id="address" type="text" {...register('address', { required: 'Street address is required' })} 
                 className={`w-full border rounded px-3 py-2 ${errors.address ? 'border-red-600' : 'border-gray-300'} focus:outline-none focus:ring-2 focus:ring-indigo-500`} />
          {errors.address && <p role="alert" className="text-red-600 text-sm mt-1">{errors.address.message}</p>}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="md:col-span-2">
            <label htmlFor="city" className="block text-gray-700 font-medium mb-1">City <span className="text-red-600">*</span></label>
            <input id="city" type="text" {...register('city', { required: 'City is required' })} 
                   className={`w-full border rounded px-3 py-2 ${errors.city ? 'border-red-600' : 'border-gray-300'} focus:outline-none focus:ring-2 focus:ring-indigo-500`} />
            {errors.city && <p role="alert" className="text-red-600 text-sm mt-1">{errors.city.message}</p>}
          </div>

          <div>
            <label htmlFor="state" className="block text-gray-700 font-medium mb-1">State <span className="text-red-600">*</span></label>
            <select id="state" {...register('state', { required: 'State is required' })} 
                    className={`w-full border rounded px-3 py-2 bg-white ${errors.state ? 'border-red-600' : 'border-gray-300'} focus:outline-none focus:ring-2 focus:ring-indigo-500`}>
              {states.map((st) => (
                <option key={st} value={st}>{st ? st : '-- Select --'}</option>
              ))}
            </select>
            {errors.state && <p role="alert" className="text-red-600 text-sm mt-1">{errors.state.message}</p>}
          </div>

          <div>
            <label htmlFor="zip" className="block text-gray-700 font-medium mb-1">Zip / Postal Code <span className="text-red-600">*</span></label>
            <input id="zip" type="text" {...register('zip', { required: 'Zip code is required', pattern: { value: /^\d{5}(-\d{4})?$/, message: 'Invalid zip code' } })} 
                   className={`w-full border rounded px-3 py-2 ${errors.zip ? 'border-red-600' : 'border-gray-300'} focus:outline-none focus:ring-2 focus:ring-indigo-500`} />
            {errors.zip && <p role="alert" className="text-red-600 text-sm mt-1">{errors.zip.message}</p>}
          </div>

          <div>
            <label htmlFor="country" className="block text-gray-700 font-medium mb-1">Country <span className="text-red-600">*</span></label>
            <input id="country" type="text" {...register('country', { required: 'Country is required' })} 
                   className={`w-full border rounded px-3 py-2 ${errors.country ? 'border-red-600' : 'border-gray-300'} focus:outline-none focus:ring-2 focus:ring-indigo-500`} />
            {errors.country && <p role="alert" className="text-red-600 text-sm mt-1">{errors.country.message}</p>}
          </div>
        </div>
      </fieldset>

      <fieldset className="mt-8">
        <legend className="text-xl font-semibold mb-4 text-gray-900">Additional Information</legend>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label htmlFor="dateOfBirth" className="block text-gray-700 font-medium mb-1">Date of Birth <span className="text-red-600">*</span></label>
            <input id="dateOfBirth" type="date" max={new Date().toISOString().split('T')[0]} {...register('dateOfBirth', { required: 'Date of birth is required' })} 
                   className={`w-full border rounded px-3 py-2 ${errors.dateOfBirth ? 'border-red-600' : 'border-gray-300'} focus:outline-none focus:ring-2 focus:ring-indigo-500`} />
            {errors.dateOfBirth && <p role="alert" className="text-red-600 text-sm mt-1">{errors.dateOfBirth.message}</p>}
          </div>

          <div>
            <label className="block text-gray-700 font-medium mb-1">Gender</label>
            <Controller
              name="gender"
              control={control}
              render={({ field }) => (
                <select {...field} className="w-full border rounded px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
                  <option value="">-- Select --</option>
                  <option value="female">Female</option>
                  <option value="male">Male</option>
                  <option value="other">Other</option>
                  <option value="prefer_not_to_say">Prefer not to say</option>
                </select>
              )}
            />
          </div>
        </div>

        <div className="mt-6">
          <label htmlFor="resume" className="block text-gray-700 font-medium mb-1">Upload Resume (PDF only, max 5MB)</label>
          <input id="resume" type="file" accept="application/pdf" {...register('resume', {
            validate: {
              isLt5MB: (files) => {
                if (!files || files.length === 0) return true; // optional
                return files[0].size <= 5 * 1024 * 1024 || 'File size must be under 5MB';
              },
              isPDF: (files) => {
                if (!files || files.length === 0) return true;
                return files[0].type === 'application/pdf' || 'Only PDF files are allowed';
              }
            }
          })} 
                 className={`w-full border rounded px-3 py-2 ${errors.resume ? 'border-red-600' : 'border-gray-300'} focus:outline-none focus:ring-2 focus:ring-indigo-500`} />
          {errors.resume && <p role="alert" className="text-red-600 text-sm mt-1">{errors.resume.message}</p>}
        </div>
      </fieldset>

      <div className="mt-8">
        <label htmlFor="consent" className="inline-flex items-center">
          <input id="consent" type="checkbox" {...register('consent', { required: 'You must agree to proceed' })} className="form-checkbox h-5 w-5 text-indigo-600" />
          <span className="ml-2 text-gray-700">I agree to the <a href="#" className="text-indigo-600 underline">terms and conditions</a> <span className="text-red-600">*</span></span>
        </label>
        {errors.consent && <p role="alert" className="text-red-600 text-sm mt-1">{errors.consent.message}</p>}
      </div>

      <div className="mt-10 flex justify-end">
        <button
          type="submit"
          disabled={isSubmitting}
          className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold px-6 py-3 rounded focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50"
        >
          {isSubmitting ? 'Submitting...' : 'Submit Application'}
        </button>
      </div>

      {isSubmitSuccessful && <p className="mt-6 text-green-600 font-medium">Thank you for your application.</p>}
    </form>
  );
}
