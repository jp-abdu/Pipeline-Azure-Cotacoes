import React from 'react';
import { TextField, Button, Box } from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import dayjs from 'dayjs';

export default function Filters({ filters, setFilters, onSearch }) {
  const handleFromChange = (value) => {
    if (value && value.isValid && value.isValid()) {
      setFilters({ ...filters, from: value.format('YYYY-MM-DD') });
    } else if (value === null) {
      setFilters({ ...filters, from: null });
    }
  };

  const handleToChange = (value) => {
    if (value && value.isValid && value.isValid()) {
      setFilters({ ...filters, to: value.format('YYYY-MM-DD') });
    } else if (value === null) {
      setFilters({ ...filters, to: null });
    }
  };

  return (
    <Box display="flex" gap={2} alignItems="center" mb={2}>
      <TextField
        label="Buscar ativo"
        value={filters.q || ''}
        onChange={e => setFilters({ ...filters, q: e.target.value })}
      />
      <DatePicker
        label="De"
        value={filters.from ? dayjs(filters.from) : null}
        onChange={handleFromChange}
        format="DD/MM/YYYY"
        slotProps={{ textField: { size: 'medium' } }}
      />
      <DatePicker
        label="Até"
        value={filters.to ? dayjs(filters.to) : null}
        onChange={handleToChange}
        format="DD/MM/YYYY"
        slotProps={{ textField: { size: 'medium' } }}
      />
      <Button variant="contained" onClick={onSearch}>Filtrar</Button>
    </Box>
  );
}
