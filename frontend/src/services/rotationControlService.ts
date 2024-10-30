// src/services/notificationService.js
import api from '@/api';
import type { TreeFolder, CreateFolder } from '@/types/tree';
import type { ApiResponse } from '@/types/response';
const basePath = '/rotation-control';

export const list = () => api.get(basePath);
export const retrieve = (id: string): Promise<ApiResponse<any>> => api.get(`${basePath}/${id}`);
export const create = (data: CreateFolder) => api.post(basePath, data);
export const update = (id: number, data: TreeFolder) => api.put(`${basePath}/${id}`, data);
// actions
export const setActive = (id: number | string, is_active: boolean) => api.patch(`${basePath}/${id}/set-active/`, { is_active });
export const remove = (id: number) => api.delete(`${basePath}/${id}`);