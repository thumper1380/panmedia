// src/services/notificationService.js
import api from '@/api';
import type { AffiliateCreate } from '@/types/affiliate';
import type { ApiResponse } from '@/types/response';
const basePath = '/affiliates';

export const list = () => api.get(basePath);
export const retrieve = (id: string): Promise<ApiResponse<any>> => api.get(`${basePath}/${id}`);
export const create = (data: AffiliateCreate) => api.post(basePath, data);
export const update = (id: number, data: AffiliateCreate) => api.put(`${basePath}/${id}`, data);
// actions
export const disable = (id: number | string) => api.put(`${basePath}/${id}/disable`);
export const enable = (id: number | string) => api.put(`${basePath}/${id}/enable`);
