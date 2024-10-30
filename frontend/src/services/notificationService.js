// src/services/notificationService.js
import api from '@/api';

const basePath = '/notification';

export const listNotifications = () => api.get(basePath);
export const retrieveNotification = (id) => api.get(`${basePath}/${id}`);
export const read = (id) => api.put(`${basePath}/${id}/read`);
export const readAll = () => api.put(`${basePath}/read-all`);
