import React, { useState, useEffect } from 'react';
import { Container, AppBar, Toolbar, Typography, Box } from '@mui/material';
import Filters from './components/Filters';
import AssetTable from './components/AssetTable';
import AssetChart from './components/AssetChart';
import { fetchAssets } from './api';

export default function App() {
  const [filters, setFilters] = useState({});
  const [data, setData] = useState([]);

  const load = async () => {
    const res = await fetchAssets(filters);
    // Ordena os dados pela data do pregão antes de atualizar o estado
    const sortedData = (res.content || []).sort((a, b) => new Date(a.dataPregao) - new Date(b.dataPregao));
    setData(sortedData);
  };

  useEffect(() => { load(); }, []);

  return (
    <>
      <AppBar position="static">
        <Toolbar><Typography variant="h6">Dashboard de Ativos</Typography></Toolbar>
      </AppBar>
      <Container sx={{ mt: 3 }}>
        <Filters filters={filters} setFilters={setFilters} onSearch={load} />
        <Box display="grid" gridTemplateColumns={{ xs: '1fr', md: '2fr 1fr' }} gap={2}>
          <AssetTable items={data} />
          <AssetChart data={data} />
        </Box>
      </Container>
    </>
  );
}
