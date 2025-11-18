import React, { useState, useEffect } from 'react';
import { Container, AppBar, Toolbar, Typography, Box } from '@mui/material';
import Filters from './components/Filters';
import AssetTable from './components/AssetTable';
import AssetChart from './components/AssetChart';
import { fetchAssets } from './api';

export default function App() {
  const [filters, setFilters] = useState({});
  const [data, setData] = useState([]);
  const [selectedAssets, setSelectedAssets] = useState([]);

  const load = async () => {
    const res = await fetchAssets(filters);
    // Ordena os dados pela data do pregão antes de atualizar o estado
    const sortedData = (res.content || []).sort((a, b) => new Date(a.dataPregao) - new Date(b.dataPregao));
    setData(sortedData);

    // Inicializa com os primeiros 3 ativos únicos selecionados apenas se não houver seleção
    if (sortedData.length > 0 && selectedAssets.length === 0) {
      const uniqueAssets = [...new Set(sortedData.map(item => item.nome || item.ticker_symbol || item.company_name))];
      setSelectedAssets(uniqueAssets.filter(Boolean).slice(0, 3));
    }
  };

  const handleToggleAsset = (assetName) => {
    setSelectedAssets(prev => {
      if (prev.includes(assetName)) {
        return prev.filter(name => name !== assetName);
      } else {
        return [...prev, assetName];
      }
    });
  };

  useEffect(() => { load(); }, []);

  return (
    <>
      <AppBar position="static">
        <Toolbar><Typography variant="h6">Dashboard de Ativos</Typography></Toolbar>
      </AppBar>
      <Container maxWidth="xl" sx={{ mt: 3 }}>
        <Filters filters={filters} setFilters={setFilters} onSearch={load} />
        <Box display="grid" gridTemplateColumns={{ xs: '1fr', lg: '1fr 1fr' }} gap={2}>
          <AssetTable items={data} selectedAssets={selectedAssets} onToggleAsset={handleToggleAsset} />
          <AssetChart data={data} selectedAssets={selectedAssets} />
        </Box>
      </Container>
    </>
  );
}
