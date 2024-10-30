// src/services/notificationService.js
import api from '@/api';
import type { SaleStatus } from '@/types/settings';

const basePath = '/settings';

const routes = {
    saleStatuses: '/sale-status',
    affiliate: '/affiliate',
    advertiser: '/advertiser',
};

export interface Option {
    id: number;
    name: string;
}


export const saleStatuses = () => api.get<SaleStatus[]>(`${basePath}${routes.saleStatuses}`);
export const affiliate = (query?: string) => api.get<Option[]>(`${basePath}${routes.affiliate}`, { params: { query } });
export const advertiser = () => api.get<Option[]>(`${basePath}${routes.advertiser}`);


export const options = {
    affiliate: affiliate,
    advertiser: advertiser,
};