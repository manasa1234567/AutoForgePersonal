import React from 'react';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import {
  TextField,
  Button,
  Grid,
  MenuItem,
  Typography,
  Alert,
  CircularProgress,
  Box
} from '@mui/material';

const educationLevels = [
  { value: 'High School', label: 'High School' },
  { value: 'Associate Degree', label: 'Associate Degree' },
  { value: 'Bachelor’s Degree', label: 'Bachelor’s Degree' },
  { value: 'Master’s Degree', label: 'Master’s Degree' },
  { value: 'Doctorate', label: 'Doctorate' },
  { value: 'Other', label: 'Other' },
];

const yupDateRegex = /^\d{4}-\d{2}-\d{2}$/;

const schema = yup.object({
  first_name: yup.string().trim().required('First Name is required'),
  last_name: yup.string().trim().required('Last Name is required'),
  date_of_birth: yup.string().matches(yupDateRegex, 'Date of Birth must be in YYYY-MM-DD format').required('Date of Birth is required'),
  email: yup.string().email('Invalid email format').required('Email is required'),
  phone_number: yup.string().required('Phone Number is required').min(7, 'Phone Number too short').max(15, 'Phone Number too long'),
  address_line1: yup.string().required('Address Line 1 is required'),
  address_line2: yup.string().notRequired(),
  city: yup.string().required('City is required'),
  state_province: yup.string().required('State/Province is required'),
  postal_code: yup.string().required('Postal Code is required'),
  country: yup.string().required('Country is required'),
  education_level: yup.string().required('Education Level is required'),
  position_applied_for: yup.string().required('Position Applied For is required'),
  cover_letter: yup.string().notRequired(),
}).required();

type FormData = yup.InferType<typeof schema>;

export default function ApplicationForm() {
  const {
    control,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting, isSubmitSuccessful },
  } = useForm<FormData>({
    resolver: yupResolver(schema),
    mode: 'onTouched',
  });

  const [apiError, setApiError] = React.useState<string | null>(null);

  const onSubmit = async (data: FormData) => {
    setApiError(null);
    try {
      const response = await fetch('http://localhost:8000/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errJson = await response.json();
        throw new Error(errJson.detail || 'Failed to submit application');
      }

      reset();
    } catch (e: any) {
      setApiError(e.message || 'Unexpected error');
    }
  };

  return (
    <Box component="form" noValidate onSubmit={handleSubmit(onSubmit)}>
      {apiError && <Alert severity="error" sx={{ mb: 2 }}>{apiError}</Alert>}
      {isSubmitSuccessful && <Alert severity="success" sx={{ mb: 2 }}>Application submitted successfully.</Alert>}
      <Grid container spacing={2}>
        <Grid item xs={12} sm={6}>
          <Controller
            name="first_name"
            control={control}
            defaultValue=""
            render={({ field }) => (
              <TextField
                {...field}
                label="First Name"
                fullWidth
                error={!!errors.first_name}
                helperText={errors.first_name?.message}
                required
              />
            )}
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <Controller
            name="last_name"
            control={control}
            defaultValue=""
            render={({ field }) => (
              <TextField
                {...field}
                label="Last Name"
                fullWidth
                error={!!errors.last_name}
                helperText={errors.last_name?.message}
                required
              />
            )}
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <Controller
            name="date_of_birth"
            control={control}
            defaultValue=""
            render={({ field }) => (
              <TextField
                {...field}
                label="Date of Birth"
                type="date"
                InputLabelProps={{ shrink: true }}
                fullWidth
                error={!!errors.date_of_birth}
                helperText={errors.date_of_birth?.message || 'Format: YYYY-MM-DD'}
                required
              />
            )}
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <Controller
            name="email"
            control={control}
            defaultValue=""
            render={({ field }) => (
              <TextField
                {...field}
                label="Email"
                type="email"
                fullWidth
                error={!!errors.email}
                helperText={errors.email?.message}
                required
              />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <Controller
            name="phone_number"
            control={control}
            defaultValue=""
            render={({ field }) => (
              <TextField
                {...field}
                label="Phone Number"
                fullWidth
                error={!!errors.phone_number}
                helperText={errors.phone_number?.message}
                required
              />
            )}
          />
        </Grid>

        <Grid item xs={12}>
          <Typography variant="h6" gutterBottom>
            Address
          </Typography>
        </Grid>

        <Grid item xs={12}>
          <Controller
            name="address_line1"
            control={control}
            defaultValue=""
            render={({ field }) => (
              <TextField
                {...field}
                label="Address Line 1"
                fullWidth
                error={!!errors.address_line1}
                helperText={errors.address_line1?.message}
                required
              />
            )}
          />
        </Grid>
        <Grid item xs={12}>
          <Controller
            name="address_line2"
            control={control}
            defaultValue=""
            render={({ field }) => (
              <TextField
                {...field}
                label="Address Line 2"
                fullWidth
                error={!!errors.address_line2}
                helperText={errors.address_line2?.message}
              />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <Controller
            name="city"
            control={control}
            defaultValue=""
            render={({ field }) => (
              <TextField
                {...field}
                label="City"
                fullWidth
                error={!!errors.city}
                helperText={errors.city?.message}
                required
              />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <Controller
            name="state_province"
            control={control}
            defaultValue=""
            render={({ field }) => (
              <TextField
                {...field}
                label="State / Province"
                fullWidth
                error={!!errors.state_province}
                helperText={errors.state_province?.message}
                required
              />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <Controller
            name="postal_code"
            control={control}
            defaultValue=""
            render={({ field }) => (
              <TextField
                {...field}
                label="Postal Code"
                fullWidth
                error={!!errors.postal_code}
                helperText={errors.postal_code?.message}
                required
              />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <Controller
            name="country"
            control={control}
            defaultValue=""
            render={({ field }) => (
              <TextField
                {...field}
                label="Country"
                fullWidth
                error={!!errors.country}
                helperText={errors.country?.message}
                required
              />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <Controller
            name="education_level"
            control={control}
            defaultValue=""
            render={({ field }) => (
              <TextField
                select
                label="Education Level"
                fullWidth
                error={!!errors.education_level}
                helperText={errors.education_level?.message}
                required
                {...field}
              >
                {educationLevels.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </TextField>
            )}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <Controller
            name="position_applied_for"
            control={control}
            defaultValue=""
            render={({ field }) => (
              <TextField
                {...field}
                label="Position Applied For"
                fullWidth
                error={!!errors.position_applied_for}
                helperText={errors.position_applied_for?.message}
                required
              />
            )}
          />
        </Grid>

        <Grid item xs={12}>
          <Controller
            name="cover_letter"
            control={control}
            defaultValue=""
            render={({ field }) => (
              <TextField
                {...field}
                label="Cover Letter"
                multiline
                rows={4}
                fullWidth
                error={!!errors.cover_letter}
                helperText={errors.cover_letter?.message}
              />
            )}
          />
        </Grid>

        <Grid item xs={12} sx={{ textAlign: 'center', mt: 2 }}>
          <Button type="submit" variant="contained" color="primary" disabled={isSubmitting}>
            {isSubmitting ? <CircularProgress size={24} /> : 'Submit Application'}
          </Button>
        </Grid>
      </Grid>
    </Box>
  );
}
