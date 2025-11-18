import React, { useState, useMemo } from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from 'recharts';
import { Paper, FormControl, InputLabel, Select, MenuItem, Box, Chip, OutlinedInput } from '@mui/material';

const PRICE_OPTIONS = [
  { value: 'precoFechamento', label: 'Preço Fechamento' },
  { value: 'precoMedio', label: 'Preço Médio' },
  { value: 'precoAbertura', label: 'Preço Abertura' },
];

const COLORS = ['#1976d2', '#dc004e', '#f57c00', '#388e3c', '#7b1fa2', '#c2185b', '#0097a7', '#303f9f'];

export default function AssetChart({ data, selectedAssets }) {
  const [priceField, setPriceField] = useState('precoFechamento');



  // Agrupa dados por data e ativo
  const chartData = useMemo(() => {
    if (selectedAssets.length === 0) return [];

    const grouped = {};

    data.forEach(item => {
      const assetName = item.nome || item.ticker_symbol || item.company_name;
      if (!selectedAssets.includes(assetName)) return;

      const date = item.dataPregao || item.trading_date || item.data_pregao;
      if (!date) return;

      // Formata a data para exibição
      const formattedDate = date.split('T')[0]; // Pega apenas YYYY-MM-DD

      if (!grouped[formattedDate]) {
        grouped[formattedDate] = { date: formattedDate };
      }

      const price = item[priceField];
      if (price !== null && price !== undefined) {
        grouped[formattedDate][assetName] = parseFloat(price);
      }
    });

    return Object.values(grouped).sort((a, b) => new Date(a.date) - new Date(b.date));
  }, [data, selectedAssets, priceField]);

  return (
    <Paper sx={{ p: 2, height: 440 }}>
      <Box sx={{ mb: 2 }}>
        <FormControl size="small" sx={{ minWidth: 200 }}>
          <InputLabel>Tipo de Preço</InputLabel>
          <Select
            value={priceField}
            label="Tipo de Preço"
            onChange={(e) => setPriceField(e.target.value)}
          >
            {PRICE_OPTIONS.map(opt => (
              <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 12 }}
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis />
          <Tooltip />
          <Legend />
          {selectedAssets.map((asset, index) => (
            <Line
              key={asset}
              type="monotone"
              dataKey={asset}
              stroke={COLORS[index % COLORS.length]}
              strokeWidth={2}
              dot={{ r: 4 }}
              connectNulls={true}
              name={asset}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </Paper>
  );
}
