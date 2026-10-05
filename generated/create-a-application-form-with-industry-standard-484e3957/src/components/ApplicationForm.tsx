import React from 'react';
import { useForm, Controller } from 'react-hook-form';
import {
  TextField,
  Grid,
  Box,
  Button,
  MenuItem,
  Typography,
  FormControlLabel,
  Checkbox
} from '@mui/material';

export interface ApplicationFormData {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  streetAddress: string;
  city: string;
  state: string;
  postalCode: string;
  country: string;
  dateOfBirth: string;
  gender: string;
  resumeLink: string;
  coverLetter: string;
  agreeToTerms: boolean;
}

const states = [
  'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI',
  'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN',
  'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH',
  'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA',
  'WV', 'WI', 'WY'
];

const countries = ['United States', 'Canada', 'Mexico', 'United Kingdom', 'Australia', 'Other'];

const genders = ['Male', 'Female', 'Other', 'Prefer not to say'];

const ApplicationForm: React.FC = () => {
  const {
    handleSubmit,
    control,
    formState: { errors, isSubmitting, isSubmitSuccessful },
    reset
  } = useForm<ApplicationFormData>({
    mode: 'onBlur',
    defaultValues: {
      firstName: '',
      lastName: '',
      email: '',
      phone: '',
      streetAddress: '',
      city: '',
      state: '',
      postalCode: '',
      country: 'United States',
      dateOfBirth: '',
      gender: '',
      resumeLink: '',
      coverLetter: '',
      agreeToTerms: false
    }
  });

  const onSubmit = (data: ApplicationFormData) => {
    alert('Form submitted successfully. (No backend integration implemented)\n\n' + JSON.stringify(data, null, 2));
    reset();
  };

  return (
    <Box component="form" noValidate onSubmit={handleSubmit(onSubmit)} aria-label="Application form">
      <Typography component="h2" variant="h5" sx={{ mb: 3 }}>
        Please fill out the application form
      </Typography>
      <Grid container spacing={3}>
        {/* Name fields */}
        <Grid item xs={12} sm={6}>
          <Controller
            name="firstName"
            control={control}
            rules={{ required: 'First name is required' }}
            render={({ field }) => (
              <TextField
                {...field}
                id="firstName"
                label="First Name"
                fullWidth
                autoComplete="given-name"
                error={Boolean(errors.firstName)}
                helperText={errors.firstName?.message}
                required
              />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <Controller
            name="lastName"
            control={control}
            rules={{ required: 'Last name is required' }}
            render={({ field }) => (
              <TextField
                {...field}
                id="lastName"
                label="Last Name"
                fullWidth
                autoComplete="family-name"
                error={Boolean(errors.lastName)}
                helperText={errors.lastName?.message}
                required
              />
            )}
          />
        </Grid>

        {/* Email and Phone */}
        <Grid item xs={12} sm={6}>
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
                id="email"
                label="Email"
                fullWidth
                autoComplete="email"
                error={Boolean(errors.email)}
                helperText={errors.email?.message}
                required
              />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <Controller
            name="phone"
            control={control}
            rules={{
              required: 'Phone number is required',
              pattern: {
                value: /^[+]?[(]?[0-9]{1,4}[)]?[-\s./0-9]*$/,
                message: 'Invalid phone number'
              }
            }}
            render={({ field }) => (
              <TextField
                {...field}
                type="tel"
                id="phone"
                label="Phone Number"
                fullWidth
                autoComplete="tel"
                error={Boolean(errors.phone)}
                helperText={errors.phone?.message}
                required
              />
            )}
          />
        </Grid>

        {/* Address Fields */}
        <Grid item xs={12}>
          <Controller
            name="streetAddress"
            control={control}
            rules={{ required: 'Street address is required' }}
            render={({ field }) => (
              <TextField
                {...field}
                id="streetAddress"
                label="Street Address"
                fullWidth
                autoComplete="street-address"
                error={Boolean(errors.streetAddress)}
                helperText={errors.streetAddress?.message}
                required
              />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <Controller
            name="city"
            control={control}
            rules={{ required: 'City is required' }}
            render={({ field }) => (
              <TextField
                {...field}
                id="city"
                label="City"
                fullWidth
                autoComplete="address-level2"
                error={Boolean(errors.city)}
                helperText={errors.city?.message}
                required
              />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={3}>
          <Controller
            name="state"
            control={control}
            rules={{ required: 'State/Province is required' }}
            render={({ field }) => (
              <TextField
                {...field}
                id="state"
                label="State/Province"
                select
                fullWidth
                autoComplete="address-level1"
                error={Boolean(errors.state)}
                helperText={errors.state?.message}
                required
              >
                {states.map((option) => (
                  <MenuItem key={option} value={option}>
                    {option}
                  </MenuItem>
                ))}
              </TextField>
            )}
          />
        </Grid>

        <Grid item xs={12} sm={3}>
          <Controller
            name="postalCode"
            control={control}
            rules={{ required: 'Postal code is required' }}
            render={({ field }) => (
              <TextField
                {...field}
                id="postalCode"
                label="Postal / ZIP Code"
                fullWidth
                autoComplete="postal-code"
                error={Boolean(errors.postalCode)}
                helperText={errors.postalCode?.message}
                required
              />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <Controller
            name="country"
            control={control}
            rules={{ required: 'Country is required' }}
            render={({ field }) => (
              <TextField
                {...field}
                id="country"
                label="Country"
                select
                fullWidth
                autoComplete="country"
                error={Boolean(errors.country)}
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
        </Grid>

        {/* Date of Birth and Gender */}
        <Grid item xs={12} sm={6}>
          <Controller
            name="dateOfBirth"
            control={control}
            rules={{
              required: 'Date of birth is required',
              validate: (value) => {
                if (!value) {
                  return 'Date of birth is required';
                }
                const dob = new Date(value);
                const today = new Date();
                if (dob >= today) {
                  return 'Date of birth cannot be in the future';
                }
                return true;
              }
            }}
            render={({ field }) => (
              <TextField
                {...field}
                id="dateOfBirth"
                label="Date of Birth"
                type="date"
                fullWidth
                InputLabelProps={{ shrink: true }}
                error={Boolean(errors.dateOfBirth)}
                helperText={errors.dateOfBirth?.message}
                required
              />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <Controller
            name="gender"
            control={control}
            rules={{ required: 'Gender is required' }}
            render={({ field }) => (
              <TextField
                {...field}
                id="gender"
                label="Gender"
                select
                fullWidth
                error={Boolean(errors.gender)}
                helperText={errors.gender?.message}
                required
              >
                {genders.map((option) => (
                  <MenuItem key={option} value={option}>
                    {option}
                  </MenuItem>
                ))}
              </TextField>
            )}
          />
        </Grid>

        {/* Resume Link and Cover Letter */}
        <Grid item xs={12}>
          <Controller
            name="resumeLink"
            control={control}
            rules={{
              required: 'Resume link is required',
              pattern: {
                value: /^(https?:\/\/)?([\w.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/i,
                message: 'Please enter a valid URL'
              }
            }}
            render={({ field }) => (
              <TextField
                {...field}
                id="resumeLink"
                label="Resume URL"
                type="url"
                fullWidth
                error={Boolean(errors.resumeLink)}
                helperText={errors.resumeLink?.message || 'Link to your hosted resume, e.g., Google Drive, Dropbox'}
                required
              />
            )}
          />
        </Grid>

        <Grid item xs={12}>
          <Controller
            name="coverLetter"
            control={control}
            rules={{ required: 'Cover letter is required', minLength: { value: 50, message: 'Min 50 characters' } }}
            render={({ field }) => (
              <TextField
                {...field}
                id="coverLetter"
                label="Cover Letter"
                fullWidth
                multiline
                minRows={5}
                error={Boolean(errors.coverLetter)}
                helperText={errors.coverLetter?.message}
                required
              />
            )}
          />
        </Grid>

        {/* Agreement checkbox */}
        <Grid item xs={12}>
          <Controller
            name="agreeToTerms"
            control={control}
            rules={{ required: 'You must agree to the terms and conditions' }}
            render={({ field }) => (
              <FormControlLabel
                control={<Checkbox {...field} checked={field.value} color="primary" />}
                label="I agree to the terms and conditions"
              />
            )}
          />
          {errors.agreeToTerms && (
            <Typography variant="body2" color="error" sx={{ ml: 1 }}>
              {errors.agreeToTerms.message}
            </Typography>
          )}
        </Grid>

        {/* Submission */}
        <Grid item xs={12}>
          <Button
            type="submit"
            variant="contained"
            color="primary"
            disabled={isSubmitting}
            fullWidth
            aria-label="Submit application form"
          >
            Submit Application
          </Button>
          {isSubmitSuccessful && (
            <Typography sx={{ mt: 2 }} color="success.main" role="alert">
              Thank you! Your application has been submitted.
            </Typography>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default ApplicationForm;
