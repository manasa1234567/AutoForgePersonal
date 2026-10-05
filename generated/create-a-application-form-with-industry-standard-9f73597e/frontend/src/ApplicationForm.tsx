import React, { useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import {
  TextField,
  Button,
  Checkbox,
  FormControlLabel,
  MenuItem,
  Alert,
  CircularProgress
} from '@mui/material';

export type FormInputs = {
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  date_of_birth: string;
  address_line1: string;
  address_line2?: string;
  city: string;
  state_province: string;
  postal_code: string;
  country: string;
  education_level: string;
  employment_status: string;
  resume_text?: string;
  agree_to_terms: boolean;
};

const educationOptions = [
  'High School Diploma',
  'Associate Degree',
  'Bachelor’s Degree',
  'Master’s Degree',
  'Doctorate',
  'Other'
];

const employmentOptions = [
  'Unemployed',
  'Part-time',
  'Full-time',
  'Self-employed',
  'Student',
  'Retired',
  'Other'
];

const countries = [
  'United States',
  'Canada',
  'United Kingdom',
  'Australia',
  'Germany',
  'France',
  'Other'
];

const ApplicationForm = () => {
  const {
    control,
    handleSubmit,
    formState: { errors, isSubmitting },
    watch,
  } = useForm<FormInputs>({ mode: 'onTouched' });

  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState<string | null>(null);

  const onSubmit = async (data: FormInputs) => {
    setSubmitError(null);
    setSubmitSuccess(null);
    try {
      const response = await fetch('/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to submit form');
      }

      setSubmitSuccess('Your application has been submitted successfully.');
    } catch (error: any) {
      setSubmitError(error.message);
    }
  };

  return (
    <form noValidate onSubmit={handleSubmit(onSubmit)}>
      {/* First Name */}
      <Controller
        name="first_name"
        control={control}
        rules={{ required: 'First name is required' }}
        render={({ field }) => (
          <TextField
            {...field}
            label="First Name"
            fullWidth
            margin="normal"
            error={!!errors.first_name}
            helperText={errors.first_name?.message}
            required
          />
        )}
      />

      {/* Last Name */}
      <Controller
        name="last_name"
        control={control}
        rules={{ required: 'Last name is required' }}
        render={({ field }) => (
          <TextField
            {...field}
            label="Last Name"
            fullWidth
            margin="normal"
            error={!!errors.last_name}
            helperText={errors.last_name?.message}
            required
          />
        )}
      />

      {/* Email */}
      <Controller
        name="email"
        control={control}
        rules={{
          required: 'Email is required',
          pattern: {
            value: /^[^@\s]+@[^@\s]+\.[^@\s]+$/,
            message: 'Invalid email address'
          }
        }}
        render={({ field }) => (
          <TextField
            {...field}
            type="email"
            label="Email"
            fullWidth
            margin="normal"
            error={!!errors.email}
            helperText={errors.email?.message}
            required
          />
        )}
      />

      {/* Phone */}
      <Controller
        name="phone"
        control={control}
        rules={{
          pattern: {
            value: /^[+\d\s()-]*$/,
            message: 'Invalid phone number'
          }
        }}
        render={({ field }) => (
          <TextField
            {...field}
            label="Phone Number"
            fullWidth
            margin="normal"
            error={!!errors.phone}
            helperText={errors.phone?.message}
          />
        )}
      />

      {/* Date of Birth */}
      <Controller
        name="date_of_birth"
        control={control}
        rules={{ required: 'Date of birth is required' }}
        render={({ field }) => (
          <TextField
            {...field}
            label="Date of Birth"
            type="date"
            fullWidth
            margin="normal"
            error={!!errors.date_of_birth}
            helperText={errors.date_of_birth?.message}
            InputLabelProps={{ shrink: true }}
            required
          />
        )}
      />

      {/* Address Line 1 */}
      <Controller
        name="address_line1"
        control={control}
        rules={{ required: 'Address Line 1 is required' }}
        render={({ field }) => (
          <TextField
            {...field}
            label="Address Line 1"
            fullWidth
            margin="normal"
            error={!!errors.address_line1}
            helperText={errors.address_line1?.message}
            required
          />
        )}
      />

      {/* Address Line 2 */}
      <Controller
        name="address_line2"
        control={control}
        render={({ field }) => (
          <TextField
            {...field}
            label="Address Line 2"
            fullWidth
            margin="normal"
          />
        )}
      />

      {/* City */}
      <Controller
        name="city"
        control={control}
        rules={{ required: 'City is required' }}
        render={({ field }) => (
          <TextField
            {...field}
            label="City"
            fullWidth
            margin="normal"
            error={!!errors.city}
            helperText={errors.city?.message}
            required
          />
        )}
      />

      {/* State/Province */}
      <Controller
        name="state_province"
        control={control}
        rules={{ required: 'State/Province is required' }}
        render={({ field }) => (
          <TextField
            {...field}
            label="State/Province"
            fullWidth
            margin="normal"
            error={!!errors.state_province}
            helperText={errors.state_province?.message}
            required
          />
        )}
      />

      {/* Postal Code */}
      <Controller
        name="postal_code"
        control={control}
        rules={{ required: 'Postal code is required' }}
        render={({ field }) => (
          <TextField
            {...field}
            label="Postal Code"
            fullWidth
            margin="normal"
            error={!!errors.postal_code}
            helperText={errors.postal_code?.message}
            required
          />
        )}
      />

      {/* Country */}
      <Controller
        name="country"
        control={control}
        rules={{ required: 'Country is required' }}
        render={({ field }) => (
          <TextField
            {...field}
            label="Country"
            select
            fullWidth
            margin="normal"
            error={!!errors.country}
            helperText={errors.country?.message}
            required
          >
            {countries.map((option) => (
              <MenuItem key={option} value={option}>
                {option}
              </MenuItem>
            ))}
          </TextField>
        )}
      />

      {/* Education Level */}
      <Controller
        name="education_level"
        control={control}
        rules={{ required: 'Education level is required' }}
        render={({ field }) => (
          <TextField
            {...field}
            label="Highest Education Level"
            select
            fullWidth
            margin="normal"
            error={!!errors.education_level}
            helperText={errors.education_level?.message}
            required
          >
            {educationOptions.map((option) => (
              <MenuItem key={option} value={option}>
                {option}
              </MenuItem>
            ))}
          </TextField>
        )}
      />

      {/* Employment Status */}
      <Controller
        name="employment_status"
        control={control}
        rules={{ required: 'Employment status is required' }}
        render={({ field }) => (
          <TextField
            {...field}
            label="Employment Status"
            select
            fullWidth
            margin="normal"
            error={!!errors.employment_status}
            helperText={errors.employment_status?.message}
            required
          >
            {employmentOptions.map((option) => (
              <MenuItem key={option} value={option}>
                {option}
              </MenuItem>
            ))}
          </TextField>
        )}
      />

      {/* Resume Text */}
      <Controller
        name="resume_text"
        control={control}
        render={({ field }) => (
          <TextField
            {...field}
            label="Resume Text (Optional)"
            multiline
            rows={4}
            fullWidth
            margin="normal"
          />
        )}
      />

      {/* Agreement Checkbox */}
      <Controller
        name="agree_to_terms"
        control={control}
        rules={{ required: 'You must agree to the terms' }}
        render={({ field }) => (
          <FormControlLabel
            control={<Checkbox color="primary" {...field} checked={field.value} />}
            label="I agree to the terms and conditions"
          />
        )}
      />
      {errors.agree_to_terms && (
        <p style={{ color: 'red', marginTop: 0, marginBottom: 8 }}>{errors.agree_to_terms.message}</p>
      )}

      {/* Submission feedback */}
      {submitError && <Alert severity="error" sx={{ mt: 2 }}>{submitError}</Alert>}
      {submitSuccess && <Alert severity="success" sx={{ mt: 2 }}>{submitSuccess}</Alert>}

      {/* Submit button */}
      <Button
        type="submit"
        variant="contained"
        color="primary"
        fullWidth
        disabled={isSubmitting}
        sx={{ mt: 3 }}
        startIcon={isSubmitting ? <CircularProgress size={20} /> : null}
      >
        Submit Application
      </Button>
    </form>
  );
};

export default ApplicationForm;
