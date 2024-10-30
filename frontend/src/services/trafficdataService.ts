// src/services/notificationService.js
import api from '@/api';
import type { TrafficData } from '@/types/trafficdata';
const basePath = '/trafficdata';
import type { ApiResponse } from '@/types/response';


export const list = (params: any) => api.get(basePath, { params });
export const retrieve = (id: string): Promise<ApiResponse<any>> => api.get(`${basePath}/${id}`);
// export statelog
export const statelog = (id: string) => api.get(`${basePath}/${id}/state-log`);
// sale status log
export const salestatuslog = (id: string) => api.get(`${basePath}/${id}/sale-status-log`);

// columns
export const columns = () => api.get(`${basePath}/columns`);
// actions:
//      reinject
//      set test lead
//      duplicate

