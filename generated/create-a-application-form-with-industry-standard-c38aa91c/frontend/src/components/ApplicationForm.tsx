import React, { useState } from 'react';
import { Box, TextField, Button, Grid, MenuItem, Typography, Paper, IconButton } from '@mui/material';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import RemoveCircleOutlineIcon from '@mui/icons-material/RemoveCircleOutline';

export interface EmploymentHistoryEntry {
  company_name: string;
  position: string;
  start_date: string;
  end_date?: string;
}

interface FormData {
  first_name: string;
  last_name: string;
  email: string;
  phone_number: string;
  address: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  date_of_birth: string;
  education_level: string;
  employment_history: EmploymentHistoryEntry[];
  skills: string[];
  additional_info: string;
}

interface FormErrors {
  first_name?: string;
  last_name?: string;
  email?: string;
  phone_number?: string;
  address?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country?: string;
  date_of_birth?: string;
  education_level?: string;
  employment_history?: Record<number, Record<string, string>>;
  skills?: string;
}

const educationLevels = [
  'High School',
  'Associate Degree',
  'Bachelor’s Degree',
  'Master’s Degree',
  'Doctorate',
  'Other',
];

// Utility to validate email format
const isValidEmail = (email: string) => {
  const re = /^[\w-.]+@([\w-]+\.)+[\w-]{2,4}$/;
  return re.test(email);
};

const ApplicationForm: React.FC = () => {
  const [formData, setFormData] = useState<FormData>({
    first_name: '',
    last_name: '',
    email: '',
    phone_number: '',
    address: '',
    city: '',
    state: '',
    postal_code: '',
    country: '',
    date_of_birth: '',
    education_level: '',
    employment_history: [{
      company_name: '',
      position: '',
      start_date: '',
      end_date: '',
    }],
    skills: [''],
    additional_info: '',
  });

  const [errors, setErrors] = useState<FormErrors>({});
  const [submitting, setSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const handleInputChange = (field: keyof FormData, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleEmploymentChange = (index: number, field: keyof EmploymentHistoryEntry, value: string) => {
    const newEmployment = [...formData.employment_history];
    newEmployment[index] = { ...newEmployment[index], [field]: value };
    setFormData((prev) => ({ ...prev, employment_history: newEmployment }));
  };

  const addEmploymentEntry = () => {
    setFormData((prev) => ({
      ...prev,
      employment_history: [...prev.employment_history, {
        company_name: '',
        position: '',
        start_date: '',
        end_date: '',
      }],
    }));
  };

  const removeEmploymentEntry = (index: number) => {
    const newEmployment = formData.employment_history.filter((_, i) => i !== index);
    setFormData((prev) => ({ ...prev, employment_history: newEmployment }));
  };

  const handleSkillChange = (index: number, value: string) => {
    const newSkills = [...formData.skills];
    newSkills[index] = value;
    setFormData((prev) => ({ ...prev, skills: newSkills }));
  };

  const addSkill = () => {
    setFormData((prev) => ({ ...prev, skills: [...prev.skills, ''] }));
  };

  const removeSkill = (index: number) => {
    const newSkills = formData.skills.filter((_, i) => i !== index);
    setFormData((prev) => ({ ...prev, skills: newSkills }));
  };

  const validateForm = () => {
    const newErrors: FormErrors = {};

    if (!formData.first_name.trim()) newErrors.first_name = 'First name is required';
    if (!formData.last_name.trim()) newErrors.last_name = 'Last name is required';

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!isValidEmail(formData.email.trim())) {
      newErrors.email = 'Invalid email format';
    }

    if (!formData.phone_number.trim()) newErrors.phone_number = 'Phone number is required';
    if (!formData.address.trim()) newErrors.address = 'Address is required';
    if (!formData.city.trim()) newErrors.city = 'City is required';
    if (!formData.state.trim()) newErrors.state = 'State/Province is required';
    if (!formData.postal_code.trim()) newErrors.postal_code = 'Postal code is required';
    if (!formData.country.trim()) newErrors.country = 'Country is required';

    if (!formData.date_of_birth.trim()) {
      newErrors.date_of_birth = 'Date of birth is required';
    } else {
      // Validate format YYYY-MM-DD
      if (!/^\d{4}-\d{2}-\d{2}$/.test(formData.date_of_birth))
        newErrors.date_of_birth = 'Date of birth must be YYYY-MM-DD';
    }

    if (!formData.education_level.trim()) newErrors.education_level = 'Education level is required';

    // Validate employment history entries
    const employmentErrors: Record<number, Record<string, string>> = {};
    formData.employment_history.forEach((entry, i) => {
      const entryErrors: Record<string, string> = {};
      if (!entry.company_name.trim()) entryErrors.company_name = 'Company name is required';
      if (!entry.position.trim()) entryErrors.position = 'Position is required';
      if (!entry.start_date.trim()) {
        entryErrors.start_date = 'Start date is required';
      } else if (!/^\d{4}-\d{2}-\d{2}$/.test(entry.start_date)) {
        entryErrors.start_date = 'Start date must be YYYY-MM-DD';
      }
      if (entry.end_date && entry.end_date.trim() !== '' && !/^\d{4}-\d{2}-\d{2}$/.test(entry.end_date)) {
        entryErrors.end_date = 'End date must be YYYY-MM-DD if provided';
      }
      if (Object.keys(entryErrors).length > 0) employmentErrors[i] = entryErrors;
    });
    if (Object.keys(employmentErrors).length > 0) newErrors.employment_history = employmentErrors;

    // Validate skills
    if (formData.skills.length === 0 || formData.skills.every(s => s.trim() === '')) {
      newErrors.skills = 'At least one skill is required';
    }

    setErrors(newErrors);

    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitSuccess(null);
    setSubmitError(null);
    if (!validateForm()) return;

    setSubmitting(true);
    try {
      const res = await fetch('http://localhost:8000/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      if (!res.ok) {
        throw new Error(`Server error: ${res.statusText}`);
      }
      const data = await res.json();
      setSubmitSuccess(data.message || 'Application submitted successfully');
      setFormData({
        first_name: '',
        last_name: '',
        email: '',
        phone_number: '',
        address: '',
        city: '',
        state: '',
        postal_code: '',
        country: '',
        date_of_birth: '',
        education_level: '',
        employment_history: [{company_name: '', position: '', start_date: '', end_date: ''}],
        skills: [''],
        additional_info: '',
      });
      setErrors({});
    } catch (error: any) {
      setSubmitError(error.message || 'Submission failed');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{maxWidth: 900, mx: 'auto', p: 2}} noValidate>
      <Typography variant="h4" gutterBottom sx={{textAlign: 'center', fontWeight: 'bold'}}>
        Application Form
      </Typography>

      {/* Personal Information Section */}
      <Typography variant="h6" gutterBottom sx={{mt: 3}}>
        Personal Information
      </Typography>

      <Grid container spacing={2}>
        <Grid item xs={12} sm={6}>
          <TextField
            label="First Name"
            value={formData.first_name}
            onChange={(e) => handleInputChange('first_name', e.target.value)}
            error={!!errors.first_name}
            helperText={errors.first_name}
            fullWidth
            required
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <TextField
            label="Last Name"
            value={formData.last_name}
            onChange={(e) => handleInputChange('last_name', e.target.value)}
            error={!!errors.last_name}
            helperText={errors.last_name}
            fullWidth
            required
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <TextField
            label="Email"
            type="email"
            value={formData.email}
            onChange={(e) => handleInputChange('email', e.target.value)}
            error={!!errors.email}
            helperText={errors.email}
            fullWidth
            required
            autoComplete="email"
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <TextField
            label="Phone Number"
            value={formData.phone_number}
            onChange={(e) => handleInputChange('phone_number', e.target.value)}
            error={!!errors.phone_number}
            helperText={errors.phone_number}
            fullWidth
            required
            autoComplete="tel"
          />
        </Grid>

        <Grid item xs={12}>
          <TextField
            label="Address"
            value={formData.address}
            onChange={(e) => handleInputChange('address', e.target.value)}
            error={!!errors.address}
            helperText={errors.address}
            fullWidth
            required
            autoComplete="street-address"
          />
        </Grid>

        <Grid item xs={12} sm={4}>
          <TextField
            label="City"
            value={formData.city}
            onChange={(e) => handleInputChange('city', e.target.value)}
            error={!!errors.city}
            helperText={errors.city}
            fullWidth
            required
            autoComplete="address-level2"
          />
        </Grid>

        <Grid item xs={12} sm={4}>
          <TextField
            label="State/Province"
            value={formData.state}
            onChange={(e) => handleInputChange('state', e.target.value)}
            error={!!errors.state}
            helperText={errors.state}
            fullWidth
            required
            autoComplete="address-level1"
          />
        </Grid>

        <Grid item xs={12} sm={4}>
          <TextField
            label="Postal Code"
            value={formData.postal_code}
            onChange={(e) => handleInputChange('postal_code', e.target.value)}
            error={!!errors.postal_code}
            helperText={errors.postal_code}
            fullWidth
            required
            autoComplete="postal-code"
          />
        </Grid>

        <Grid item xs={12}>
          <TextField
            label="Country"
            value={formData.country}
            onChange={(e) => handleInputChange('country', e.target.value)}
            error={!!errors.country}
            helperText={errors.country}
            fullWidth
            required
            autoComplete="country-name"
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <TextField
            label="Date of Birth"
            type="date"
            value={formData.date_of_birth}
            onChange={(e) => handleInputChange('date_of_birth', e.target.value)}
            error={!!errors.date_of_birth}
            helperText={errors.date_of_birth}
            fullWidth
            required
            InputLabelProps={{ shrink: true }}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <TextField
            select
            label="Highest Education Level"
            value={formData.education_level}
            onChange={(e) => handleInputChange('education_level', e.target.value)}
            error={!!errors.education_level}
            helperText={errors.education_level}
            fullWidth
            required
          >
            {educationLevels.map((level) => (
              <MenuItem key={level} value={level}>
                {level}
              </MenuItem>
            ))}
          </TextField>
        </Grid>
      </Grid>

      {/* Employment History Section */}
      <Typography variant="h6" gutterBottom sx={{mt: 4}}>
        Employment History
      </Typography>

      {formData.employment_history.map((entry, index) => {
        const entryErrors = errors.employment_history?.[index] || {};
        return (
          <Paper key={index} sx={{ mb: 2, p: 2, position: 'relative' }} elevation={2}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={5}>
                <TextField
                  label="Company Name"
                  value={entry.company_name}
                  onChange={(e) => handleEmploymentChange(index, 'company_name', e.target.value)}
                  error={!!entryErrors.company_name}
                  helperText={entryErrors.company_name}
                  fullWidth
                  required
                />
              </Grid>

              <Grid item xs={12} sm={5}>
                <TextField
                  label="Position"
                  value={entry.position}
                  onChange={(e) => handleEmploymentChange(index, 'position', e.target.value)}
                  error={!!entryErrors.position}
                  helperText={entryErrors.position}
                  fullWidth
                  required
                />
              </Grid>

              <Grid item xs={6} sm={1.5}>
                <TextField
                  label="Start Date"
                  type="date"
                  value={entry.start_date}
                  onChange={(e) => handleEmploymentChange(index, 'start_date', e.target.value)}
                  error={!!entryErrors.start_date}
                  helperText={entryErrors.start_date}
                  InputLabelProps={{ shrink: true }}
                  fullWidth
                  required
                />
              </Grid>

              <Grid item xs={6} sm={1.5}>
                <TextField
                  label="End Date"
                  type="date"
                  value={entry.end_date || ''}
                  onChange={(e) => handleEmploymentChange(index, 'end_date', e.target.value)}
                  error={!!entryErrors.end_date}
                  helperText={entryErrors.end_date}
                  InputLabelProps={{ shrink: true }}
                  fullWidth
                />
              </Grid>
            </Grid>

            <IconButton
              aria-label="Remove Employment Entry"
              onClick={() => removeEmploymentEntry(index)}
              sx={{ position: 'absolute', top: 4, right: 4 }}
              disabled={formData.employment_history.length === 1}
            >
              <RemoveCircleOutlineIcon color={formData.employment_history.length === 1 ? 'disabled' : 'error'} />
            </IconButton>
          </Paper>
        );
      })}

      <Button
        variant="outlined"
        startIcon={<AddCircleOutlineIcon />}
        onClick={addEmploymentEntry}
        sx={{ mt: 1, mb: 3 }}
      >
        Add Employment
      </Button>

      {/* Skills Section */}
      <Typography variant="h6" gutterBottom sx={{mb: 1}}>
        Skills
      </Typography>
      {formData.skills.map((skill, idx) => (
        <Box key={idx} sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <TextField
            label={`Skill #${idx + 1}`}
            value={skill}
            onChange={(e) => handleSkillChange(idx, e.target.value)}
            error={!!(errors.skills && skill.trim() === '')}
            helperText={idx === 0 && errors.skills ? errors.skills : ''}
            fullWidth
            required
          />
          <IconButton
            aria-label="Remove Skill"
            onClick={() => removeSkill(idx)}
            disabled={formData.skills.length === 1}
            sx={{ ml: 1 }}
          >
            <RemoveCircleOutlineIcon color={formData.skills.length === 1 ? 'disabled' : 'error'} />
          </IconButton>
        </Box>
      ))}
      <Button variant="outlined" startIcon={<AddCircleOutlineIcon />} onClick={addSkill} sx={{ mb: 3 }}>
        Add Skill
      </Button>

      {/* Additional Info */}
      <TextField
        label="Additional Information"
        value={formData.additional_info}
        onChange={(e) => handleInputChange('additional_info', e.target.value)}
        multiline
        rows={4}
        fullWidth
      />

      {/* Submission Feedback */}
      {submitSuccess && (
        <Typography color="success.main" sx={{ mt: 2, mb: 2 }} role="alert">
          {submitSuccess}
        </Typography>
      )}
      {submitError && (
        <Typography color="error.main" sx={{ mt: 2, mb: 2 }} role="alert">
          {submitError}
        </Typography>
      )}

      {/* Submit Button */}
      <Box sx={{ textAlign: 'center', mt: 2 }}>
        <Button variant="contained" type="submit" disabled={submitting} size="large">
          {submitting ? 'Submitting...' : 'Submit Application'}
        </Button>
      </Box>
    </Box>
  );
};

export default ApplicationForm;
