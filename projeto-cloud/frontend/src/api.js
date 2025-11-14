import axios from 'axios';
export const api = axios.create({ baseURL: 'https://projeto-cloud-b3-fkhpfyhufbd4hbbk.brazilsouth-01.azurewebsites.net/api' });
export const fetchAssets = async (filters) => {
  const res = await api.get('/assets', { params: filters });
  return res.data;
};
