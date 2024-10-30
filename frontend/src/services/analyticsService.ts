// src/services/notificationService.js
import api from '@/api';
const basePath = '/analytics';

export const metrics = (start_date: string, end_date: string) => api.get(`${basePath}/metrics`, { params: { start_date, end_date } });
export const registrationChart = (start_date: string, end_date: string) => api.get(`${basePath}/registration-chart`, { params: { start_date, end_date } });