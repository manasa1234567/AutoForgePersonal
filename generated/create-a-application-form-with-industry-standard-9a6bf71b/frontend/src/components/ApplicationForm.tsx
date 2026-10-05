import React from 'react';
import { Formik, Form, FormikHelpers } from 'formik';
import * as Yup from 'yup';
import {
  TextField,
  Checkbox,
  FormControlLabel,
  Button,
  Grid,
  Box,
  MenuItem,
  FormHelperText,
  Alert,
  CircularProgress,
} from '@mui/material';

import axios from 'axios';

interface FormValues {
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  address_line1: string;
  address_line2: string;
  city: string;
  state_province: string;
  postal_code: string;
  country: string;
  date_of_birth: string; // YYYY-MM-DD
  gender: string;
  position_applied: string;
  education_level: string;
  years_of_experience: number | '';
  accept_terms: boolean;
}

const initialValues: FormValues = {
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  address_line1: '',
  address_line2: '',
  city: '',
  state_province: '',
  postal_code: '',
  country: '',
  date_of_birth: '',
  gender: '',
  position_applied: '',
  education_level: '',
  years_of_experience: '',
  accept_terms: false,
};

const genders = [
  { value: 'Male', label: 'Male' },
  { value: 'Female', label: 'Female' },
  { value: 'Other', label: 'Other' },
  { value: 'Prefer not to say', label: 'Prefer not to say' },
];

const educationLevels = [
  { value: 'High School', label: 'High School' },
  { value: 'Associate Degree', label: 'Associate Degree' },
  { value: 'Bachelor’s Degree', label: 'Bachelor’s Degree' },
  { value: 'Master’s Degree', label: 'Master’s Degree' },
  { value: 'Doctorate', label: 'Doctorate' },
];

const positions = [
  { value: 'Developer', label: 'Developer' },
  { value: 'Designer', label: 'Designer' },
  { value: 'Project Manager', label: 'Project Manager' },
  { value: 'Quality Assurance', label: 'Quality Assurance' },
  { value: 'Other', label: 'Other' },
];

// Validation schema
const today = new Date();
const isoToday = today.toISOString().slice(0, 10);

const phoneRegex = /^\+?[0-9\-\s]{7,15}$/;
const postalCodeRegex = /^[\w\s-]{3,10}$/;
const dateRegex = /^\d{4}-\d{2}-\d{2}$/;

const validationSchema = Yup.object().shape({
  first_name: Yup.string().required('First name is required'),
  last_name: Yup.string().required('Last name is required'),
  email: Yup.string().email('Invalid email address').required('Email is required'),
  phone: Yup.string()
    .matches(phoneRegex, 'Invalid phone number format')
    .required('Phone number is required'),
  address_line1: Yup.string().required('Address Line 1 is required'),
  address_line2: Yup.string(),
  city: Yup.string().required('City is required'),
  state_province: Yup.string().required('State/Province is required'),
  postal_code: Yup.string().matches(postalCodeRegex, 'Invalid postal code').required('Postal code is required'),
  country: Yup.string().required('Country is required'),
  date_of_birth: Yup.string()
    .matches(dateRegex, 'Date of birth must be in YYYY-MM-DD format')
    .test('dob', 'Date of birth cannot be in the future', value => {
      if (!value) return false;
      return new Date(value) <= today;
    })
    .required('Date of birth is required'),
  gender: Yup.string().oneOf(genders.map(g => g.value)).required('Gender is required'),
  position_applied: Yup.string().oneOf(positions.map(p => p.value)).required('Position applied is required'),
  education_level: Yup.string().oneOf(educationLevels.map(e => e.value)).required('Education level is required'),
  years_of_experience: Yup.number()
    .typeError('Years of experience must be a number')
    .min(0, 'Years of experience must be zero or more')
    .max(75, 'Years of experience seems unrealistic')
    .required('Years of experience is required'),
  accept_terms: Yup.boolean().oneOf([true], 'You must accept the terms and conditions'),
});

const ApplicationForm: React.FC = () => {
  const [submitError, setSubmitError] = React.useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = React.useState<boolean>(false);

  const handleSubmit = async (
    values: FormValues,
    formikHelpers: FormikHelpers<FormValues>
  ) => {
    setSubmitError(null);
    setSubmitSuccess(false);
    try {
      const res = await axios.post('/submit', {
        ...values,
        years_of_experience: Number(values.years_of_experience),
      });

      if (res.data.status === 'success') {
        setSubmitSuccess(true);
        formikHelpers.resetForm();
      } else {
        setSubmitError('Submission failed, please try again later.');
      }
    } catch (err: any) {
      if (err.response && err.response.data && err.response.data.detail) {
        setSubmitError(err.response.data.detail);
      } else {
        setSubmitError('An unknown error occurred.');
      }
    } finally {
      formikHelpers.setSubmitting(false);
    }
  };

  return (
    <Formik
      initialValues={initialValues}
      validationSchema={validationSchema}
      onSubmit={handleSubmit}
    >
      {({ values, errors, touched, handleChange, isSubmitting, setFieldValue }) => (
        <Form noValidate>
          <Grid container spacing={2}>
            {/* Personal Information */}
            <Grid item xs={12}>
              <strong>Personal Information</strong>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                id="first_name"
                name="first_name"
                label="First Name"
                fullWidth
                value={values.first_name}
                onChange={handleChange}
                error={touched.first_name && Boolean(errors.first_name)}
                helperText={touched.first_name && errors.first_name}
                required
                autoComplete="given-name"
                inputProps={{ 'aria-required': true }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                id="last_name"
                name="last_name"
                label="Last Name"
                fullWidth
                value={values.last_name}
                onChange={handleChange}
                error={touched.last_name && Boolean(errors.last_name)}
                helperText={touched.last_name && errors.last_name}
                required
                autoComplete="family-name"
                inputProps={{ 'aria-required': true }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                id="email"
                name="email"
                label="Email"
                type="email"
                fullWidth
                value={values.email}
                onChange={handleChange}
                error={touched.email && Boolean(errors.email)}
                helperText={touched.email && errors.email}
                required
                autoComplete="email"
                inputProps={{ 'aria-required': true }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                id="phone"
                name="phone"
                label="Phone Number"
                type="tel"
                fullWidth
                value={values.phone}
                onChange={handleChange}
                error={touched.phone && Boolean(errors.phone)}
                helperText={touched.phone && errors.phone}
                required
                autoComplete="tel"
                inputProps={{ 'aria-required': true }}
              />
            </Grid>

            {/* Address */}
            <Grid item xs={12}>
              <strong>Address Information</strong>
            </Grid>
            <Grid item xs={12}>
              <TextField
                id="address_line1"
                name="address_line1"
                label="Address Line 1"
                fullWidth
                value={values.address_line1}
                onChange={handleChange}
                error={touched.address_line1 && Boolean(errors.address_line1)}
                helperText={touched.address_line1 && errors.address_line1}
                required
                autoComplete="address-line1"
                inputProps={{ 'aria-required': true }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                id="address_line2"
                name="address_line2"
                label="Address Line 2"
                fullWidth
                value={values.address_line2}
                onChange={handleChange}
                error={touched.address_line2 && Boolean(errors.address_line2)}
                helperText={touched.address_line2 && errors.address_line2}
                autoComplete="address-line2"
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                id="city"
                name="city"
                label="City"
                fullWidth
                value={values.city}
                onChange={handleChange}
                error={touched.city && Boolean(errors.city)}
                helperText={touched.city && errors.city}
                required
                autoComplete="address-level2"
                inputProps={{ 'aria-required': true }}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                id="state_province"
                name="state_province"
                label="State/Province"
                fullWidth
                value={values.state_province}
                onChange={handleChange}
                error={touched.state_province && Boolean(errors.state_province)}
                helperText={touched.state_province && errors.state_province}
                required
                autoComplete="address-level1"
                inputProps={{ 'aria-required': true }}
              />
            </Grid>
            <Grid item xs={12} sm={2}>
              <TextField
                id="postal_code"
                name="postal_code"
                label="Postal Code"
                fullWidth
                value={values.postal_code}
                onChange={handleChange}
                error={touched.postal_code && Boolean(errors.postal_code)}
                helperText={touched.postal_code && errors.postal_code}
                required
                autoComplete="postal-code"
                inputProps={{ 'aria-required': true }}
              />
            </Grid>
            <Grid item xs={12} sm={2}>
              <TextField
                id="country"
                name="country"
                label="Country"
                fullWidth
                value={values.country}
                onChange={handleChange}
                error={touched.country && Boolean(errors.country)}
                helperText={touched.country && errors.country}
                required
                autoComplete="country-name"
                inputProps={{ 'aria-required': true }}
              />
            </Grid>

            {/* Additional Application Details */}
            <Grid item xs={12}>
              <strong>Additional Details</strong>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                id="date_of_birth"
                name="date_of_birth"
                label="Date of Birth"
                type="date"
                fullWidth
                value={values.date_of_birth}
                onChange={handleChange}
                error={touched.date_of_birth && Boolean(errors.date_of_birth)}
                helperText={touched.date_of_birth && errors.date_of_birth}
                InputLabelProps={{ shrink: true }}
                required
                inputProps={{
                  max: isoToday,
                  'aria-required': true,
                }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                id="gender"
                name="gender"
                label="Gender"
                select
                fullWidth
                value={values.gender}
                onChange={handleChange}
                error={touched.gender && Boolean(errors.gender)}
                helperText={touched.gender && errors.gender}
                required
                inputProps={{ 'aria-required': true }}
              >
                {genders.map(option => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                id="position_applied"
                name="position_applied"
                label="Position Applied For"
                select
                fullWidth
                value={values.position_applied}
                onChange={handleChange}
                error={touched.position_applied && Boolean(errors.position_applied)}
                helperText={touched.position_applied && errors.position_applied}
                required
                inputProps={{ 'aria-required': true }}
              >
                {positions.map(option => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                id="education_level"
                name="education_level"
                label="Highest Education Level"
                select
                fullWidth
                value={values.education_level}
                onChange={handleChange}
                error={touched.education_level && Boolean(errors.education_level)}
                helperText={touched.education_level && errors.education_level}
                required
                inputProps={{ 'aria-required': true }}
              >
                {educationLevels.map(option => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                id="years_of_experience"
                name="years_of_experience"
                label="Years of Experience"
                type="number"
                fullWidth
                value={values.years_of_experience}
                onChange={handleChange}
                error={touched.years_of_experience && Boolean(errors.years_of_experience)}
                helperText={touched.years_of_experience && errors.years_of_experience}
                required
                inputProps={{
                  'aria-required': true,
                  min: 0,
                  max: 75,
                }}
              />
            </Grid>

            {/* Consent */}
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Checkbox
                    id="accept_terms"
                    name="accept_terms"
                    color="primary"
                    checked={values.accept_terms}
                    onChange={e => setFieldValue('accept_terms', e.target.checked)}
                    aria-required="true"
                  />
                }
                label="I accept the terms and conditions"
              />
              {touched.accept_terms && errors.accept_terms && (
                <FormHelperText error>{errors.accept_terms}</FormHelperText>
              )}
            </Grid>

            {/* Submit Button and Status */}
            <Grid item xs={12}>
              {submitError && <Alert severity="error" sx={{ mb: 2 }}>{submitError}</Alert>}
              {submitSuccess && <Alert severity="success" sx={{ mb: 2 }}>Application submitted successfully!</Alert>}
              <Box textAlign="center">
                <Button
                  type="submit"
                  variant="contained"
                  color="primary"
                  disabled={isSubmitting}
                  aria-label="Submit Application Form"
                  size="large"
                >
                  {isSubmitting ? <CircularProgress size={24} /> : 'Submit'}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </Form>
      )}
    </Formik>
  );
};

export default ApplicationForm;
