import React, { useState } from 'react';
import {
  TextField,
  Button,
  Grid,
  Box,
  Alert,
  CircularProgress
} from '@mui/material';

interface FormData {
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  address_line1: string;
  address_line2: string;
  city: string;
  state: string;
  zip_code: string;
  country: string;
  date_of_birth: string;
  position_applied: string;
  cover_letter: string;
}

interface FormErrors {
  [field: string]: string;
}

const initialFormData: FormData = {
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  address_line1: '',
  address_line2: '',
  city: '',
  state: '',
  zip_code: '',
  country: '',
  date_of_birth: '',
  position_applied: '',
  cover_letter: '',
};

const ApplicationForm: React.FC = () => {
  const [formData, setFormData] = useState<FormData>(initialFormData);
  const [errors, setErrors] = useState<FormErrors>({});
  const [submitting, setSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const validate = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.first_name.trim()) newErrors.first_name = 'First name is required';
    if (!formData.last_name.trim()) newErrors.last_name = 'Last name is required';
    if (!formData.email.trim()) newErrors.email = 'Email is required';
    else {
      // Basic email regex
      const emailRegex = /^[\w-.]+@[\w-]+\.[a-z]{2,}$/i;
      if (!emailRegex.test(formData.email)) newErrors.email = 'Invalid email address';
    }
    if (!formData.phone.trim()) newErrors.phone = 'Phone number is required';
    if (!formData.address_line1.trim()) newErrors.address_line1 = 'Address line 1 is required';
    if (!formData.city.trim()) newErrors.city = 'City is required';
    if (!formData.state.trim()) newErrors.state = 'State/Province is required';
    if (!formData.zip_code.trim()) newErrors.zip_code = 'Zip/Postal code is required';
    if (!formData.country.trim()) newErrors.country = 'Country is required';
    if (!formData.date_of_birth.trim()) newErrors.date_of_birth = 'Date of birth is required';
    else {
      const dobRegex = /^\d{4}-\d{2}-\d{2}$/;
      if (!dobRegex.test(formData.date_of_birth)) newErrors.date_of_birth = 'Date of birth must be YYYY-MM-DD';
    }
    if (!formData.position_applied.trim()) newErrors.position_applied = 'Position applied for is required';

    setErrors(newErrors);

    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setErrors({ ...errors, [e.target.name]: '' });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    setSuccessMessage(null);
    setErrorMessage(null);

    if (!validate()) {
      return;
    }

    setSubmitting(true);

    try {
      const response = await fetch('http://localhost:8000/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Submission failed');
      }

      const result = await response.json();
      setSuccessMessage(result.message);
      setFormData(initialFormData);
    } catch (error: any) {
      setErrorMessage(error.message || 'An unexpected error occurred');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Box component="form" noValidate onSubmit={handleSubmit} sx={{ mt: 1 }}>
      {successMessage && <Alert severity="success" sx={{ mb: 2 }}>{successMessage}</Alert>}
      {errorMessage && <Alert severity="error" sx={{ mb: 2 }}>{errorMessage}</Alert>}
      <Grid container spacing={2}>
        <Grid item xs={12} sm={6}>
          <TextField
            autoComplete="given-name"
            name="first_name"
            required
            fullWidth
            label="First Name"
            value={formData.first_name}
            onChange={handleChange}
            error={Boolean(errors.first_name)}
            helperText={errors.first_name}
            inputProps={{ maxLength: 50 }}
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            autoComplete="family-name"
            name="last_name"
            required
            fullWidth
            label="Last Name"
            value={formData.last_name}
            onChange={handleChange}
            error={Boolean(errors.last_name)}
            helperText={errors.last_name}
            inputProps={{ maxLength: 50 }}
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            autoComplete="email"
            name="email"
            required
            fullWidth
            label="Email Address"
            type="email"
            value={formData.email}
            onChange={handleChange}
            error={Boolean(errors.email)}
            helperText={errors.email}
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            name="phone"
            required
            fullWidth
            label="Phone Number"
            value={formData.phone}
            onChange={handleChange}
            error={Boolean(errors.phone)}
            helperText={errors.phone}
          />
        </Grid>
        <Grid item xs={12}>
          <TextField
            name="address_line1"
            required
            fullWidth
            label="Address Line 1"
            value={formData.address_line1}
            onChange={handleChange}
            error={Boolean(errors.address_line1)}
            helperText={errors.address_line1}
          />
        </Grid>
        <Grid item xs={12}>
          <TextField
            name="address_line2"
            fullWidth
            label="Address Line 2 (optional)"
            value={formData.address_line2}
            onChange={handleChange}
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            name="city"
            required
            fullWidth
            label="City"
            value={formData.city}
            onChange={handleChange}
            error={Boolean(errors.city)}
            helperText={errors.city}
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            name="state"
            required
            fullWidth
            label="State / Province"
            value={formData.state}
            onChange={handleChange}
            error={Boolean(errors.state)}
            helperText={errors.state}
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            name="zip_code"
            required
            fullWidth
            label="Zip / Postal Code"
            value={formData.zip_code}
            onChange={handleChange}
            error={Boolean(errors.zip_code)}
            helperText={errors.zip_code}
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            name="country"
            required
            fullWidth
            label="Country"
            value={formData.country}
            onChange={handleChange}
            error={Boolean(errors.country)}
            helperText={errors.country}
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            name="date_of_birth"
            required
            fullWidth
            label="Date of Birth (YYYY-MM-DD)"
            placeholder="YYYY-MM-DD"
            value={formData.date_of_birth}
            onChange={handleChange}
            error={Boolean(errors.date_of_birth)}
            helperText={errors.date_of_birth}
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            name="position_applied"
            required
            fullWidth
            label="Position Applied For"
            value={formData.position_applied}
            onChange={handleChange}
            error={Boolean(errors.position_applied)}
            helperText={errors.position_applied}
          />
        </Grid>
        <Grid item xs={12}>
          <TextField
            name="cover_letter"
            label="Cover Letter"
            multiline
            minRows={4}
            fullWidth
            value={formData.cover_letter}
            onChange={handleChange}
            inputProps={{ maxLength: 2000 }}
            placeholder="Optional"
          />
        </Grid>
        <Grid item xs={12}>
          <Button
            type="submit"
            fullWidth
            variant="contained"
            color="primary"
            disabled={submitting}
            startIcon={submitting ? <CircularProgress size={20} /> : null}
          >
            {submitting ? 'Submitting...' : 'Submit Application'}
          </Button>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ApplicationForm;
