
export interface AffiliateCreate {
    company_name: string;
    country: string;
    telegram: string;
    skype: string;
    first_name: string;
    last_name: string;
    email: string;
}

export interface Affiliate {
    id: number;
    company_name: string;
    country: string;
    telegram: string;
    skype: string;
    status: boolean;
    user: {
        id: number;
        password: string;
        last_login: string;
        is_superuser: boolean;
        email: string;
        first_name: string;
        last_name: string;
        is_admin: boolean;
        is_active: boolean;
        is_staff: boolean;
        registered_at: string;
        groups: [];
        user_permissions: [];
    }
}