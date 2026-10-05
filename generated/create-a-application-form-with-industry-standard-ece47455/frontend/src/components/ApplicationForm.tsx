import React, { useState } from 'react';
import {
  TextField,
  Button,
  Grid,
  Typography,
  MenuItem,
  FormControlLabel,
  Checkbox,
  Alert,
  CircularProgress,
} from '@mui/material';
import axios from 'axios';

// Form data interface
interface FormData {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  dateOfBirth: string; // yyyy-mm-dd
  address: string;
  city: string;
  state: string;
  zipCode: string;
  country: string;
  gender: string;
  educationLevel: string;
  resumeText: string;
  agreeTerms: boolean;
}

// Validation error messages interface
interface ValidationErrors {
  [key: string]: string;
}

const countries = [
  'United States',
  'Canada',
  'United Kingdom',
  'Australia',
  'Other',
];

const statesUS = [
  'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut',
  'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa',
  'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan',
  'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada',
  'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina',
  'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island',
  'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont',
  'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming',
];

const educationLevels = [
  'High School Diploma',
  'Associate Degree',
  'Bachelor Degree',
  'Master Degree',
  'Doctorate',
];

// Initial form state
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
  country: 'United States',
  gender: '',
  educationLevel: '',
  resumeText: '',
  agreeTerms: false,
};

const ApplicationForm: React.FC = () => {
  const [formData, setFormData] = useState<FormData>({ ...initialFormData });
  const [errors, setErrors] = useState<ValidationErrors>({});
  const [submitting, setSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Validation function
  const validate = (): ValidationErrors => {
    const newErrors: ValidationErrors = {};
    if (!formData.firstName.trim()) newErrors.firstName = 'First name is required';
    if (!formData.lastName.trim()) newErrors.lastName = 'Last name is required';
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^\S+@\S+\.\S+$/.test(formData.email)) {
      newErrors.email = 'Email address is invalid';
    }
    if (!formData.phone.trim()) {
      newErrors.phone = 'Phone number is required';
    } else if (!/^\+?\d{7,15}$/.test(formData.phone)) {
      newErrors.phone = 'Phone number is invalid, digits only, min 7 max 15';
    }
    if (!formData.dateOfBirth) {
      newErrors.dateOfBirth = 'Date of birth is required';
    }
    if (!formData.address.trim()) newErrors.address = 'Address is required';
    if (!formData.city.trim()) newErrors.city = 'City is required';
    if (!formData.state.trim()) newErrors.state = 'State/Province is required';
    if (!formData.zipCode.trim()) newErrors.zipCode = 'ZIP/Postal code is required';
    if (!formData.country.trim()) newErrors.country = 'Country is required';
    if (!formData.gender) newErrors.gender = 'Please select gender';
    if (!formData.educationLevel) newErrors.educationLevel = 'Please select education level';
    if (!formData.resumeText.trim()) newErrors.resumeText = 'Resume text is required';
    if (!formData.agreeTerms) newErrors.agreeTerms = 'You must agree to the terms';
    return newErrors;
  };

  // Handle form changes
  const handleChange = (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value, type, checked } = event.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
    // Clear error for changed field
    setErrors(prev => ({ ...prev, [name]: undefined }));
  };

  // Handle form submit
  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setSubmitSuccess(false);
    setSubmitError(null);

    const validationErrors = validate();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    setSubmitting(true);

    try {
      // Submit to backend API
      await axios.post('/api/applications', formData); // Proxy will route to backend
      setSubmitSuccess(true);
      setFormData({ ...initialFormData });
    } catch (err: any) {
      if (err.response && err.response.data && err.response.data.detail) {
        setSubmitError(err.response.data.detail);
      } else {
        setSubmitError('Failed to submit the application. Please try again later.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  // Render
  return (
    <form onSubmit={handleSubmit} noValidate aria-label="Application Form">
      <Typography variant="h4" component="h2" gutterBottom>
        Complete Application Form
      </Typography>

      {submitError && (
        <Alert severity="error" sx={{ mb: 2 }} role="alert">
          {submitError}
        </Alert>
      )}

      {submitSuccess && (
        <Alert severity="success" sx={{ mb: 2 }} role="alert">
          Application submitted successfully.
        </Alert>
      )}

      <Grid container spacing={2}>
        {/* Name fields */}
        <Grid item xs={12} sm={6}>
          <TextField
            required
            fullWidth
            id="firstName"
            name="firstName"
            label="First Name"
            value={formData.firstName}
            onChange={handleChange}
            error={Boolean(errors.firstName)}
            helperText={errors.firstName}
            autoComplete="given-name"
            inputProps={{ maxLength: 50 }}
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            required
            fullWidth
            id="lastName"
            name="lastName"
            label="Last Name"
            value={formData.lastName}
            onChange={handleChange}
            error={Boolean(errors.lastName)}
            helperText={errors.lastName}
            autoComplete="family-name"
            inputProps={{ maxLength: 50 }}
          />
        </Grid>

        {/* Contact */}
        <Grid item xs={12} sm={6}>
          <TextField
            required
            fullWidth
            id="email"
            name="email"
            label="Email Address"
            type="email"
            value={formData.email}
            onChange={handleChange}
            error={Boolean(errors.email)}
            helperText={errors.email}
            autoComplete="email"
            inputProps={{ maxLength: 254 }}
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            required
            fullWidth
            id="phone"
            name="phone"
            label="Phone Number"
            type="tel"
            value={formData.phone}
            onChange={handleChange}
            error={Boolean(errors.phone)}
            helperText={errors.phone || 'Include country code. e.g. +1234567890'}
            autoComplete="tel"
            inputProps={{ maxLength: 15 }}
          />
        </Grid>

        {/* Date of birth */}
        <Grid item xs={12} sm={6}>
          <TextField
            required
            fullWidth
            id="dateOfBirth"
            name="dateOfBirth"
            label="Date of Birth"
            type="date"
            value={formData.dateOfBirth}
            onChange={handleChange}
            error={Boolean(errors.dateOfBirth)}
            helperText={errors.dateOfBirth}
            InputLabelProps={{ shrink: true }}
          />
        </Grid>

        {/* Gender selection */}
        <Grid item xs={12} sm={6}>
          <TextField
            select
            label="Gender"
            name="gender"
            value={formData.gender}
            onChange={handleChange}
            error={Boolean(errors.gender)}
            helperText={errors.gender}
            required
            fullWidth
          >
            <MenuItem value="">Select</MenuItem>
            <MenuItem value="female">Female</MenuItem>
            <MenuItem value="male">Male</MenuItem>
            <MenuItem value="other">Other</MenuItem>
            <MenuItem value="prefer_not_say">Prefer not to say</MenuItem>
          </TextField>
        </Grid>

        {/* Address fields */}
        <Grid item xs={12}>
          <TextField
            required
            fullWidth
            id="address"
            name="address"
            label="Street Address"
            value={formData.address}
            onChange={handleChange}
            error={Boolean(errors.address)}
            helperText={errors.address}
            autoComplete="address-line1"
            inputProps={{ maxLength: 100 }}
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            required
            fullWidth
            id="city"
            name="city"
            label="City"
            value={formData.city}
            onChange={handleChange}
            error={Boolean(errors.city)}
            helperText={errors.city}
            autoComplete="address-level2"
            inputProps={{ maxLength: 50 }}
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            required
            fullWidth
            id="state"
            name="state"
            label="State / Province"
            value={formData.state}
            onChange={handleChange}
            error={Boolean(errors.state)}
            helperText={errors.state}
            autoComplete="address-level1"
            inputProps={{ maxLength: 50 }}
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            required
            fullWidth
            id="zipCode"
            name="zipCode"
            label="ZIP / Postal Code"
            value={formData.zipCode}
            onChange={handleChange}
            error={Boolean(errors.zipCode)}
            helperText={errors.zipCode}
            autoComplete="postal-code"
            inputProps={{ maxLength: 20 }}
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            select
            required
            fullWidth
            id="country"
            name="country"
            label="Country"
            value={formData.country}
            onChange={handleChange}
            error={Boolean(errors.country)}
            helperText={errors.country}
            autoComplete="country"
          >
            {countries.map((country) => (
              <MenuItem key={country} value={country}>{country}</MenuItem>
            ))}
          </TextField>
        </Grid>

        {/* Education Level */}
        <Grid item xs={12}>
          <TextField
            select
            label="Highest Education Level"
            name="educationLevel"
            value={formData.educationLevel}
            onChange={handleChange}
            error={Boolean(errors.educationLevel)}
            helperText={errors.educationLevel}
            required
            fullWidth
          >
            <MenuItem value="">Select</MenuItem>
            {educationLevels.map((level) => (
              <MenuItem key={level} value={level}>{level}</MenuItem>
            ))}
          </TextField>
        </Grid>

        {/* Resume Text */}
        <Grid item xs={12}>
          <TextField
            required
            fullWidth
            multiline
            minRows={6}
            id="resumeText"
            name="resumeText"
            label="Resume / Experience Summary"
            placeholder="Paste your resume text or experience summary here..."
            value={formData.resumeText}
            onChange={handleChange}
            error={Boolean(errors.resumeText)}
            helperText={errors.resumeText}
            inputProps={{ maxLength: 5000 }}
          />
        </Grid>

        {/* Agree to terms checkbox */}
        <Grid item xs={12}>
          <FormControlLabel
            control={<Checkbox
              name="agreeTerms"
              checked={formData.agreeTerms}
              onChange={handleChange}
              color="primary"
              inputProps={{ 'aria-required': true }}
            />}
            label={
              <>
                I agree to the <a href="/terms" target="_blank" rel="noopener noreferrer">terms and conditions</a>.
              </>
            }
          />
          {errors.agreeTerms && (
            <Typography variant="body2" color="error" role="alert">
              {errors.agreeTerms}
            </Typography>
          )}
        </Grid>

        {/* Submit button */}
        <Grid item xs={12}>
          <Button
            type="submit"
            variant="contained"
            color="primary"
            disabled={submitting}
            fullWidth
            aria-label="Submit Application"
          >
            {submitting ? <CircularProgress size={24} color="inherit" /> : 'Submit Application'}
          </Button>
        </Grid>
      </Grid>
    </form>
  );
};

export default ApplicationForm;
