import React, { useState, ChangeEvent, FormEvent } from 'react';
import {
  Box,
  Button,
  Checkbox,
  FormControl,
  FormControlLabel,
  FormHelperText,
  InputLabel,
  MenuItem,
  Radio,
  RadioGroup,
  Select,
  TextField,
  Typography,
  Grid,
  Paper
} from '@mui/material';

interface FormData {
  firstName: string;
  lastName: string;
  dateOfBirth: string; // ISO date
  gender: string;
  email: string;
  phone: string;
  address: string;
  city: string;
  state: string;
  postalCode: string;
  country: string;
  highestEducation: string;
  experienceYears: number | '';
  resumeConsent: boolean;
  termsAgree: boolean;
}

const initialFormData: FormData = {
  firstName: '',
  lastName: '',
  dateOfBirth: '',
  gender: '',
  email: '',
  phone: '',
  address: '',
  city: '',
  state: '',
  postalCode: '',
  country: '',
  highestEducation: '',
  experienceYears: '',
  resumeConsent: false,
  termsAgree: false
};

const countries = [
  'United States',
  'Canada',
  'United Kingdom',
  'Australia',
  'Other'
];

const educations = [
  'High School',
  'Associate Degree',
  'Bachelor’s Degree',
  'Master’s Degree',
  'Doctorate'
];

const genders = [
  { value: 'male', label: 'Male' },
  { value: 'female', label: 'Female' },
  { value: 'other', label: 'Other' },
  { value: 'preferNotToSay', label: 'Prefer not to say' }
];

const ApplicationForm: React.FC = () => {
  const [formData, setFormData] = useState<FormData>(initialFormData);
  const [formErrors, setFormErrors] = useState<Partial<Record<keyof FormData, string>>>({});
  const [submitted, setSubmitted] = useState(false);

  const validateEmail = (email: string) => {
    // simple email regex
    const re = /^\S+@\S+\.\S+$/;
    return re.test(email);
  };

  const validatePhone = (phone: string) => {
    // simplification: digits, spaces, dashes, () allowed, min 7 digits
    const digits = phone.replace(/[^0-9]/g, '');
    return digits.length >= 7;
  };

  const validatePostalCode = (code: string) => {
    // general: alphanumeric between 3 and 10 chars
    return /^[a-zA-Z0-9 \-]{3,10}$/.test(code);
  };

  const validateForm = (): boolean => {
    const errors: Partial<Record<keyof FormData, string>> = {};
    if (!formData.firstName.trim()) errors.firstName = 'First name is required';
    if (!formData.lastName.trim()) errors.lastName = 'Last name is required';
    if (!formData.dateOfBirth) errors.dateOfBirth = 'Date of birth is required';
    if (!formData.gender) errors.gender = 'Gender is required';
    if (!formData.email.trim()) errors.email = 'Email is required';
    else if (!validateEmail(formData.email)) errors.email = 'Email is invalid';
    if (!formData.phone.trim()) errors.phone = 'Phone number is required';
    else if (!validatePhone(formData.phone)) errors.phone = 'Phone number is invalid';
    if (!formData.address.trim()) errors.address = 'Address is required';
    if (!formData.city.trim()) errors.city = 'City is required';
    if (!formData.state.trim()) errors.state = 'State/Province is required';
    if (!formData.postalCode.trim()) errors.postalCode = 'Postal code is required';
    else if (!validatePostalCode(formData.postalCode)) errors.postalCode = 'Postal code is invalid';
    if (!formData.country) errors.country = 'Country is required';
    if (!formData.highestEducation) errors.highestEducation = 'Highest education is required';
    if (formData.experienceYears === '') errors.experienceYears = 'Experience (years) is required';
    else if(typeof formData.experienceYears === 'number' && (formData.experienceYears < 0 || formData.experienceYears > 80)) 
      errors.experienceYears = 'Experience must be between 0 and 80 years';
    if (!formData.termsAgree) errors.termsAgree = 'You must agree to the terms and conditions';

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleChange = <K extends keyof FormData>(
    event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement> | ChangeEvent<{ name?: string; value: unknown; }>,
  ) => {
    const { name, value, type } = event.target as HTMLInputElement;

    setFormData(prev => {
      const newVal = type === 'checkbox' ? (event.target as HTMLInputElement).checked : value;

      return {
        ...prev,
        [name as K]: newVal,
      };
    });

    if (formErrors[name as K]) {
      setFormErrors(prevErrors => ({ ...prevErrors, [name]: undefined }));
    }
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (validateForm()) {
      setSubmitted(true);
      // For now we do not submit to backend, just show success
    } else {
      setSubmitted(false);
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 3, mb: 3 }} component="main" aria-label="Application Form">
      <Typography component="h2" variant="h5" mb={3}>
        Complete Application Form
      </Typography>
      {submitted && (
        <Box mb={2} sx={{ color: 'success.main' }} role="alert">
          Your application has been submitted successfully.
        </Box>
      )}
      <Box component="form" noValidate onSubmit={handleSubmit}>
        <Grid container spacing={3}>
          <Grid item xs={12} sm={6}>
            <TextField
              required
              fullWidth
              id="firstName"
              name="firstName"
              label="First Name"
              value={formData.firstName}
              onChange={handleChange}
              error={!!formErrors.firstName}
              helperText={formErrors.firstName}
              inputProps={{ maxLength: 50 }}
              autoComplete="given-name"
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
              error={!!formErrors.lastName}
              helperText={formErrors.lastName}
              inputProps={{ maxLength: 50 }}
              autoComplete="family-name"
            />
          </Grid>

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
              InputLabelProps={{ shrink: true }}
              error={!!formErrors.dateOfBirth}
              helperText={formErrors.dateOfBirth}
              inputProps={{ max: new Date().toISOString().split('T')[0] }}
              autoComplete="bday"
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <FormControl component="fieldset" fullWidth error={!!formErrors.gender} required>
              <Typography component="legend" sx={{ mb: 1 }}>
                Gender
              </Typography>
              <RadioGroup
                aria-label="gender"
                name="gender"
                value={formData.gender}
                onChange={handleChange}
                row
              >
                {genders.map((g) => (
                  <FormControlLabel key={g.value} value={g.value} control={<Radio />} label={g.label} />
                ))}
              </RadioGroup>
              {!!formErrors.gender && <FormHelperText>{formErrors.gender}</FormHelperText>}
            </FormControl>
          </Grid>

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
              error={!!formErrors.email}
              helperText={formErrors.email}
              autoComplete="email"
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
              error={!!formErrors.phone}
              helperText={formErrors.phone}
              inputProps={{ maxLength: 20 }}
              autoComplete="tel"
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              required
              fullWidth
              id="address"
              name="address"
              label="Address"
              value={formData.address}
              onChange={handleChange}
              error={!!formErrors.address}
              helperText={formErrors.address}
              inputProps={{ maxLength: 100 }}
              autoComplete="street-address"
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
              error={!!formErrors.city}
              helperText={formErrors.city}
              inputProps={{ maxLength: 50 }}
              autoComplete="address-level2"
            />
          </Grid>
          <Grid item xs={12} sm={3}>
            <TextField
              required
              fullWidth
              id="state"
              name="state"
              label="State / Province"
              value={formData.state}
              onChange={handleChange}
              error={!!formErrors.state}
              helperText={formErrors.state}
              inputProps={{ maxLength: 50 }}
              autoComplete="address-level1"
            />
          </Grid>
          <Grid item xs={12} sm={3}>
            <TextField
              required
              fullWidth
              id="postalCode"
              name="postalCode"
              label="Postal Code"
              value={formData.postalCode}
              onChange={handleChange}
              error={!!formErrors.postalCode}
              helperText={formErrors.postalCode}
              inputProps={{ maxLength: 10 }}
              autoComplete="postal-code"
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <FormControl fullWidth required error={!!formErrors.country}>
              <InputLabel id="country-label">Country</InputLabel>
              <Select
                labelId="country-label"
                id="country"
                name="country"
                value={formData.country}
                label="Country"
                onChange={handleChange}
              >
                {countries.map((c) => (
                  <MenuItem key={c} value={c}>
                    {c}
                  </MenuItem>
                ))}
              </Select>
              {formErrors.country && <FormHelperText>{formErrors.country}</FormHelperText>}
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={6}>
            <FormControl fullWidth required error={!!formErrors.highestEducation}>
              <InputLabel id="education-label">Highest Level of Education</InputLabel>
              <Select
                labelId="education-label"
                id="highestEducation"
                name="highestEducation"
                value={formData.highestEducation}
                label="Highest Level of Education"
                onChange={handleChange}
              >
                {educations.map((e) => (
                  <MenuItem key={e} value={e}>
                    {e}
                  </MenuItem>
                ))}
              </Select>
              {!!formErrors.highestEducation && <FormHelperText>{formErrors.highestEducation}</FormHelperText>}
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              required
              fullWidth
              id="experienceYears"
              name="experienceYears"
              label="Years of Relevant Experience"
              type="number"
              inputProps={{ min: 0, max: 80 }}
              value={formData.experienceYears}
              onChange={handleChange}
              error={!!formErrors.experienceYears}
              helperText={formErrors.experienceYears || 'Enter number of years, e.g. 0 or 3'}
            />
          </Grid>

          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Checkbox
                  name="resumeConsent"
                  checked={formData.resumeConsent}
                  onChange={handleChange}
                />
              }
              label="I consent to submit my resume and personal data"
            />
          </Grid>

          <Grid item xs={12}>
            <FormControl required error={!!formErrors.termsAgree} component="fieldset">
              <FormControlLabel
                control={<Checkbox name="termsAgree" checked={formData.termsAgree} onChange={handleChange} />}
                label={<>I agree to the <a href="#" target="_blank" rel="noopener noreferrer">terms and conditions</a></>}
              />
              {!!formErrors.termsAgree && <FormHelperText>{formErrors.termsAgree}</FormHelperText>}
            </FormControl>
          </Grid>

          <Grid item xs={12}>
            <Button type="submit" variant="contained" color="primary" fullWidth>
              Submit Application
            </Button>
          </Grid>
        </Grid>
      </Box>
    </Paper>
  );
};

export default ApplicationForm;
