import React from 'react';
import { useForm, SubmitHandler, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import {
  Typography,
  TextField,
  Grid,
  Button,
  Snackbar,
  Alert,
  MenuItem,
  CircularProgress
} from '@mui/material';

interface FormData {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  age: number | undefined;
  address: string;
  city: string;
  state: string;
  postalCode: string;
  country: string;
  educationLevel: string;
  experienceYears: number | undefined;
  positionApplied: string;
  coverLetter: string;
}

const educationOptions = [
  'High School',
  'Associate Degree',
  'Bachelor’s Degree',
  'Master’s Degree',
  'Doctorate',
];

const positions = [
  'Software Engineer',
  'Product Manager',
  'Designer',
  'Sales Representative',
  'Human Resources',
];

const schema = yup.object({
  firstName: yup.string().trim().required('First name is required'),
  lastName: yup.string().trim().required('Last name is required'),
  email: yup.string().email('Invalid email').required('Email is required'),
  phone: yup.string().trim().required('Phone number is required').min(7, 'Phone too short').max(15, 'Phone too long'),
  age: yup.number().typeError('Age must be a number').required('Age is required').min(18, 'Minimum age is 18').max(100, 'Maximum age is 100'),
  address: yup.string().trim().required('Address is required').min(10, 'Address too short'),
  city: yup.string().trim().required('City is required').min(2, 'City too short'),
  state: yup.string().trim().required('State is required').min(2, 'State too short'),
  postalCode: yup.string().trim().required('Postal code is required').min(4, 'Postal code too short').max(10, 'Postal code too long'),
  country: yup.string().trim().required('Country is required').min(2, 'Country too short'),
  educationLevel: yup.string().required('Education level is required'),
  experienceYears: yup.number().typeError('Experience must be a number').required('Experience is required').min(0, 'Cannot be negative').max(50, 'Experience too high'),
  positionApplied: yup.string().required('Position is required'),
  coverLetter: yup.string().max(2000, 'Cover letter too long').optional(),
}).required();

const ApplicationForm: React.FC = () => {
  const {
    control,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<FormData>({
    resolver: yupResolver(schema),
    mode: 'onBlur',
    defaultValues: {
      firstName: '',
      lastName: '',
      email: '',
      phone: '',
      age: undefined,
      address: '',
      city: '',
      state: '',
      postalCode: '',
      country: '',
      educationLevel: '',
      experienceYears: undefined,
      positionApplied: '',
      coverLetter: '',
    },
  });

  const [openSnackbar, setOpenSnackbar] = React.useState(false);
  const [snackbarMsg, setSnackbarMsg] = React.useState('');
  const [snackbarSeverity, setSnackbarSeverity] = React.useState<'success' | 'error'>('success');

  const onSubmit: SubmitHandler<FormData> = async (data) => {
    try {
      const response = await fetch('/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          first_name: data.firstName.trim(),
          last_name: data.lastName.trim(),
          email: data.email.trim(),
          phone: data.phone.trim(),
          age: data.age,
          address: data.address.trim(),
          city: data.city.trim(),
          state: data.state.trim(),
          postal_code: data.postalCode.trim(),
          country: data.country.trim(),
          education_level: data.educationLevel,
          experience_years: data.experienceYears,
          position_applied: data.positionApplied,
          cover_letter: data.coverLetter.trim(),
        }),
      });
      if (response.ok) {
        setSnackbarSeverity('success');
        setSnackbarMsg('Application submitted successfully!');
        setOpenSnackbar(true);
        reset();
      } else {
        const errorData = await response.json();
        setSnackbarSeverity('error');
        setSnackbarMsg(errorData.detail || 'Submission failed.');
        setOpenSnackbar(true);
      }
    } catch (error) {
      setSnackbarSeverity('error');
      setSnackbarMsg('Network or server error. Please try again later.');
      setOpenSnackbar(true);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      <Typography variant="h5" component="h1" gutterBottom sx={{ mb: 3 }}>
        Applicant Information
      </Typography>
      <Grid container spacing={3}>
        {/* Personal Info */}
        <Grid item xs={12} sm={6}>
          <Controller
            name="firstName"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="First Name"
                fullWidth
                required
                error={!!errors.firstName}
                helperText={errors.firstName?.message}
                autoComplete="given-name"
              />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <Controller
            name="lastName"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Last Name"
                fullWidth
                required
                error={!!errors.lastName}
                helperText={errors.lastName?.message}
                autoComplete="family-name"
              />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <Controller
            name="email"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Email"
                type="email"
                fullWidth
                required
                error={!!errors.email}
                helperText={errors.email?.message}
                autoComplete="email"
              />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <Controller
            name="phone"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Phone Number"
                fullWidth
                required
                error={!!errors.phone}
                helperText={errors.phone?.message}
                autoComplete="tel"
                inputProps={{ maxLength: 15 }}
              />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <Controller
            name="age"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Age"
                type="number"
                fullWidth
                required
                error={!!errors.age}
                helperText={errors.age?.message}
                inputProps={{ min: 18, max: 100 }}
              />
            )}
          />
        </Grid>

        {/* Address */}
        <Grid item xs={12}>
          <Controller
            name="address"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Address"
                fullWidth
                required
                error={!!errors.address}
                helperText={errors.address?.message}
                autoComplete="street-address"
              />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={4}>
          <Controller
            name="city"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="City"
                fullWidth
                required
                error={!!errors.city}
                helperText={errors.city?.message}
                autoComplete="address-level2"
              />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={4}>
          <Controller
            name="state"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="State / Province"
                fullWidth
                required
                error={!!errors.state}
                helperText={errors.state?.message}
                autoComplete="address-level1"
              />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={4}>
          <Controller
            name="postalCode"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Postal Code"
                fullWidth
                required
                error={!!errors.postalCode}
                helperText={errors.postalCode?.message}
                autoComplete="postal-code"
              />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <Controller
            name="country"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Country"
                fullWidth
                required
                error={!!errors.country}
                helperText={errors.country?.message}
                autoComplete="country-name"
              />
            )}
          />
        </Grid>

        {/* Education & Experience */}
        <Grid item xs={12} sm={6}>
          <Controller
            name="educationLevel"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                select
                label="Education Level"
                fullWidth
                required
                error={!!errors.educationLevel}
                helperText={errors.educationLevel?.message}
              >
                {educationOptions.map((option) => (
                  <MenuItem key={option} value={option}>
                    {option}
                  </MenuItem>
                ))}
              </TextField>
            )}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <Controller
            name="experienceYears"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Years of Experience"
                type="number"
                fullWidth
                required
                error={!!errors.experienceYears}
                helperText={errors.experienceYears?.message}
                inputProps={{ min: 0, max: 50 }}
              />
            )}
          />
        </Grid>

        {/* Position Applied For */}
        <Grid item xs={12}>
          <Controller
            name="positionApplied"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                select
                label="Position Applied For"
                fullWidth
                required
                error={!!errors.positionApplied}
                helperText={errors.positionApplied?.message}
              >
                {positions.map((position) => (
                  <MenuItem key={position} value={position}>
                    {position}
                  </MenuItem>
                ))}
              </TextField>
            )}
          />
        </Grid>

        {/* Cover Letter */}
        <Grid item xs={12}>
          <Controller
            name="coverLetter"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Cover Letter (optional)"
                fullWidth
                multiline
                rows={5}
                error={!!errors.coverLetter}
                helperText={errors.coverLetter?.message || 'Max 2000 characters'}
              />
            )}
          />
        </Grid>

        <Grid item xs={12} sx={{ textAlign: 'center' }}>
          <Button variant="contained" color="primary" type="submit" disabled={isSubmitting} size="large">
            {isSubmitting ? <CircularProgress size={24} /> : 'Submit Application'}
          </Button>
        </Grid>
      </Grid>

      <Snackbar
        open={openSnackbar}
        autoHideDuration={6000}
        onClose={() => setOpenSnackbar(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={() => setOpenSnackbar(false)} severity={snackbarSeverity} sx={{ width: '100%' }}>
          {snackbarMsg}
        </Alert>
      </Snackbar>
    </form>
  );
};

export default ApplicationForm;
