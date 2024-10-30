// src/services/notificationService.js
import api from '@/api';
import type { Advertiser } from '@/types/advertiser';
import type { ApiResponse } from '@/types/response';
const basePath = '/advertisers';

export const list = () => api.get(basePath);
export const retrieve = (id: string): Promise<ApiResponse<any>> => api.get(`${basePath}/${id}`);
export const create = (data: Advertiser) => api.post(basePath, data);
export const update = (id: number, data: Advertiser) => api.put(`${basePath}/${id}`, data);
// actions
export const disable = (id: number | string) => api.put(`${basePath}/${id}/disable`);
