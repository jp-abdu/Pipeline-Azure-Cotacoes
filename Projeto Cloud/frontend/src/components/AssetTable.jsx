import React from 'react';
import { Table, TableHead, TableRow, TableCell, TableBody, Paper, TableContainer, Checkbox } from '@mui/material';

export default function AssetTable({ items, selectedAssets, onToggleAsset }) {
  const handleToggle = (assetName) => {
    onToggleAsset(assetName);
  };

  return (
    <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
      <Table stickyHeader>
        <TableHead>
          <TableRow>
            <TableCell padding="checkbox">Gráfico</TableCell>
            <TableCell>Nome</TableCell>
            <TableCell>Data</TableCell>
            <TableCell align="right">Abertura</TableCell>
            <TableCell align="right">Fechamento</TableCell>
            <TableCell align="right">Volume</TableCell>
            <TableCell align="right">Preço Médio</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {items.map(row => {
            const assetName = row.nome || row.ticker_symbol || row.company_name;
            const isSelected = selectedAssets.includes(assetName);

            return (
              <TableRow
                key={row.id}
                hover
                sx={{
                  backgroundColor: isSelected ? 'action.selected' : 'inherit',
                  '&:hover': { backgroundColor: isSelected ? 'action.hover' : 'inherit' }
                }}
              >
                <TableCell padding="checkbox">
                  <Checkbox
                    checked={isSelected}
                    onChange={() => handleToggle(assetName)}
                    color="primary"
                  />
                </TableCell>
                <TableCell><strong>{row.nome}</strong></TableCell>
                <TableCell>{row.dataPregao}</TableCell>
                <TableCell align="right">{row.precoAbertura}</TableCell>
                <TableCell align="right">{row.precoFechamento}</TableCell>
                <TableCell align="right">{row.volumeDiario}</TableCell>
                <TableCell align="right">{row.precoMedio}</TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
