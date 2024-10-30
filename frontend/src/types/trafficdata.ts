export interface TrafficData {
    id: number;
    country: string;
    region: string;
    city: string;
    language: string;
    state: string;
    afm_state: string;
    afm_status: string;
    advertiser_external_id: string;
    thank_you_url: string | null;
    aff_sub_1: string | null;
    aff_sub_2: string | null;
    aff_sub_3: string | null;
    aff_sub_4: string | null;
    aff_sub_5: string | null;
    aff_sub_6: string | null;
    aff_sub_7: string | null;
    aff_sub_8: string | null;
    aff_sub_9: string | null;
    aff_sub_10: string | null;
    aff_sub_11: string | null;
    aff_sub_12: string | null;
    aff_sub_13: string | null;
    aff_sub_14: string | null;
    aff_sub_15: string | null;
    aff_sub_16: string | null;
    aff_sub_17: string | null;
    aff_sub_18: string | null;
    aff_sub_19: string | null;
    aff_sub_20: string | null;
    adv_sub_1: string;
    adv_sub_2: string;
    adv_sub_3: string;
    adv_sub_4: string;
    adv_sub_5: string;
    device_type: string | null;
    user_agent: string | null;
    os: string | null;
    os_version: string | null;
    browser: string | null;
    browser_version: string | null;
    device_model: string | null;
    ip_address: string;
    bot: boolean;
    connection_type: string;
    mobile_operator: string;
    x_requested_with: string | null;
    isp: string;
    latitude: number | null;
    longitude: number | null;
    proxy: boolean;
    is_unique: boolean | null;
    retry_count: number;
    referrer: string | null;
    score: number | null;
    click_created_at: string;
    click_landed_created_at: string | null;
    lead_created_at: string;
    lead_pushed_created_at: string;
    sale_created_at: string | null;
    updated_at: string;
    created_at: string;
    is_risky: boolean;
    affiliate: number;
    funnel: number;
    advertiser: number;
    auto_login: number;
    source: number;
}


export enum TrafficDataState {
    CLICK = "click",
    CLICK_LANDED = "click_landed",
    LEAD = "lead",
    LEAD_PUSHED = "lead_pushed",
    SALE = "sale"
}



import type { TagColor } from 'naive-ui/es/tag/src/common-props';

export type BaseLog = {
    id: number;
    trafficdata: number; // Assuming this is a number, change as per your actual data type
    color: TagColor;
    created_at: string;
};

export type StateSwitchedLog = BaseLog & {
    type: 'StateSwitchedLog';
    source_state: string;
    target_state: string;
};

export type StateInitiatedLog = BaseLog & {
    type: 'StateInitiatedLog';
    initial_state: string;
};

export type PushingErrorLog = BaseLog & {
    type: 'PushingErrorLog';
    message: string;
};

export type PushingAttemptLog = BaseLog & {
    type: 'PushingAttemptLog';
    message: string;
};

export type StateLog = StateSwitchedLog | StateInitiatedLog | PushingErrorLog | PushingAttemptLog;


export type SaleStatusLog = {
    status: string;
    created_at: string;
};