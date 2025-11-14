import axios from 'axios';
export const api = axios.create({ baseURL: 'https://webapp-backend-b3-pipeline.azurewebsites.net/api' });
export const fetchAssets = async (filters) => {
  const res = await api.get('/assets', { params: filters });
  return res.data;
};
