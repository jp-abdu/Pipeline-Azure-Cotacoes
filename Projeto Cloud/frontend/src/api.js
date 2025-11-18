import axios from 'axios';
export const api = axios.create({ baseURL: 'https://webapp-backend-b3-pipeline.azurewebsites.net/api' });
export const fetchAssets = async (filters) => {
  // Adiciona size para carregar mais dados (ou todos)
  const params = { ...filters, size: 10000 };
  const res = await api.get('/assets', { params });
  return res.data;
};
