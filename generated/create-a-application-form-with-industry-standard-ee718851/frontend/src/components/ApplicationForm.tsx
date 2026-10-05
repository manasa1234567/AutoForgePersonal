import React, { useState } from 'react';
import {
  Button,
  Grid,
  TextField,
  MenuItem,
  FormControlLabel,
  Checkbox,
  Alert,
  CircularProgress,
  Typography
} from '@mui/material';

interface FormData {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  dateOfBirth: string;
  streetAddress: string;
  city: string;
  state: string;
  postalCode: string;
  country: string;
  positionApplied: string;
  resumeLink: string;
  acceptTerms: boolean;
}

const initialFormData: FormData = {
  firstName: '',
  lastName: '',
  email: '',
  phone: '',
  dateOfBirth: '',
  streetAddress: '',
  city: '',
  state: '',
  postalCode: '',
  country: '',
  positionApplied: '',
  resumeLink: '',
  acceptTerms: false
};

const positions = [
  'Software Engineer',
  'Product Manager',
  'Data Analyst',
  'UX Designer',
  'Sales Associate'
];

const ApplicationForm: React.FC = () => {
  const [formData, setFormData] = useState<FormData>(initialFormData);
  const [errors, setErrors] = useState<Partial<FormData>>({});
  const [submitError, setSubmitError] = useState('');
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const validate = (): boolean => {
    const newErrors: Partial<FormData> = {};
    if (!formData.firstName.trim()) newErrors.firstName = 'First name is required';
    if (!formData.lastName.trim()) newErrors.lastName = 'Last name is required';
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[\w-.]+@[\w-]+\.[a-z]{2,}$/i.test(formData.email)) {
      newErrors.email = 'Invalid email address';
    }
    if (!formData.phone.trim()) {
      newErrors.phone = 'Phone number is required';
    } else if (!/^\+?[0-9\s\-()]{7,15}$/.test(formData.phone)) {
      newErrors.phone = 'Invalid phone number';
    }
    if (!formData.dateOfBirth.trim()) {
      newErrors.dateOfBirth = 'Date of birth is required';
    }
    if (!formData.streetAddress.trim()) newErrors.streetAddress = 'Street address is required';
    if (!formData.city.trim()) newErrors.city = 'City is required';
    if (!formData.state.trim()) newErrors.state = 'State/Province is required';
    if (!formData.postalCode.trim()) newErrors.postalCode = 'Postal/Zip code is required';
    if (!formData.country.trim()) newErrors.country = 'Country is required';
    if (!formData.positionApplied.trim()) newErrors.positionApplied = 'Position applied for is required';
    if (!formData.acceptTerms) newErrors.acceptTerms = 'You must accept the terms';

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = e.target;
    setFormData(prev => ({ ...prev, [name]: checked }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitError('');
    setSubmitSuccess(false);

    if (!validate()) {
      return;
    }

    setLoading(true);

    try {
      const response = await fetch('/api/applications', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        const data = await response.json();
        setSubmitError(data.detail || 'Submission failed. Please try again later.');
      } else {
        setSubmitSuccess(true);
        setFormData(initialFormData);
        setErrors({});
      }
    } catch (error) {
      setSubmitError('Network error. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form noValidate onSubmit={handleSubmit} aria-label="Application form">
      <Grid container spacing={2}>
        <Grid item xs={12} sm={6}>
          <TextField
            name="firstName"
            label="First Name"
            required
            fullWidth
            variant="outlined"
            value={formData.firstName}
            onChange={handleChange}
            error={!!errors.firstName}
            helperText={errors.firstName}
            inputProps={{ 'aria-required': true }}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <TextField
            name="lastName"
            label="Last Name"
            required
            fullWidth
            variant="outlined"
            value={formData.lastName}
            onChange={handleChange}
            error={!!errors.lastName}
            helperText={errors.lastName}
            inputProps={{ 'aria-required': true }}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <TextField
            name="email"
            label="Email Address"
            type="email"
            required
            fullWidth
            variant="outlined"
            value={formData.email}
            onChange={handleChange}
            error={!!errors.email}
            helperText={errors.email}
            inputProps={{ 'aria-required': true }}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <TextField
            name="phone"
            label="Phone Number"
            type="tel"
            required
            fullWidth
            variant="outlined"
            value={formData.phone}
            onChange={handleChange}
            error={!!errors.phone}
            helperText={errors.phone}
            inputProps={{ 'aria-required': true }}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <TextField
            name="dateOfBirth"
            label="Date of Birth"
            type="date"
            required
            fullWidth
            variant="outlined"
            InputLabelProps={{ shrink: true }}
            value={formData.dateOfBirth}
            onChange={handleChange}
            error={!!errors.dateOfBirth}
            helperText={errors.dateOfBirth}
            inputProps={{ 'aria-required': true }}
          />
        </Grid>

        <Grid item xs={12}>
          <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>
            Address
          </Typography>
        </Grid>

        <Grid item xs={12}>
          <TextField
            name="streetAddress"
            label="Street Address"
            required
            fullWidth
            variant="outlined"
            value={formData.streetAddress}
            onChange={handleChange}
            error={!!errors.streetAddress}
            helperText={errors.streetAddress}
            inputProps={{ 'aria-required': true }}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <TextField
            name="city"
            label="City"
            required
            fullWidth
            variant="outlined"
            value={formData.city}
            onChange={handleChange}
            error={!!errors.city}
            helperText={errors.city}
            inputProps={{ 'aria-required': true }}
          />
        </Grid>

        <Grid item xs={12} sm={3}>
          <TextField
            name="state"
            label="State/Province"
            required
            fullWidth
            variant="outlined"
            value={formData.state}
            onChange={handleChange}
            error={!!errors.state}
            helperText={errors.state}
            inputProps={{ 'aria-required': true }}
          />
        </Grid>

        <Grid item xs={12} sm={3}>
          <TextField
            name="postalCode"
            label="Postal/Zip Code"
            required
            fullWidth
            variant="outlined"
            value={formData.postalCode}
            onChange={handleChange}
            error={!!errors.postalCode}
            helperText={errors.postalCode}
            inputProps={{ 'aria-required': true }}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <TextField
            name="country"
            label="Country"
            required
            fullWidth
            variant="outlined"
            value={formData.country}
            onChange={handleChange}
            error={!!errors.country}
            helperText={errors.country}
            inputProps={{ 'aria-required': true }}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <TextField
            select
            name="positionApplied"
            label="Position Applied For"
            required
            fullWidth
            variant="outlined"
            value={formData.positionApplied}
            onChange={handleChange}
            error={!!errors.positionApplied}
            helperText={errors.positionApplied || 'Please select the position you are applying for'}
            inputProps={{ 'aria-required': true }}
          >
            {positions.map((option) => (
              <MenuItem key={option} value={option}>
                {option}
              </MenuItem>
            ))}
          </TextField>
        </Grid>

        <Grid item xs={12}>
          <TextField
            name="resumeLink"
            label="Resume Link (optional)"
            fullWidth
            variant="outlined"
            placeholder="URL to your online resume or portfolio"
            value={formData.resumeLink}
            onChange={handleChange}
            error={!!errors.resumeLink}
            helperText={errors.resumeLink}
            inputProps={{ 'aria-required': false }}
          />
        </Grid>

        <Grid item xs={12}>
          <FormControlLabel
            control={
              <Checkbox
                name="acceptTerms"
                checked={formData.acceptTerms}
                onChange={handleCheckboxChange}
                color="primary"
                inputProps={{ 'aria-required': true }}
              />
            }
            label="I accept the terms and conditions"
          />
          {errors.acceptTerms && (
            <Typography color="error" variant="caption" role="alert">
              {errors.acceptTerms}
            </Typography>
          )}
        </Grid>

        {submitError && (
          <Grid item xs={12}>
            <Alert severity="error" onClose={() => setSubmitError('')}>{submitError}</Alert>
          </Grid>
        )}

        {submitSuccess && (
          <Grid item xs={12}>
            <Alert severity="success" onClose={() => setSubmitSuccess(false)}>
              Application submitted successfully!
            </Alert>
          </Grid>
        )}

        <Grid item xs={12}>
          <Button
            type="submit"
            variant="contained"
            color="primary"
            disabled={loading}
            fullWidth
            aria-label="Submit application form"
          >
            {loading ? <CircularProgress size={24} aria-label="Submitting" /> : 'Submit'}
          </Button>
        </Grid>
      </Grid>
    </form>
  );
};

export default ApplicationForm;
