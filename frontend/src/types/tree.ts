import { type TreeOption } from "naive-ui";
import type { VNode } from "vue";

export enum TreeFolderType {
    RotationControlCountryFolder = 'RotationControlCountryFolder',
    RotationControlCountrySplitFolder = 'RotationControlCountrySplitFolder',
    RotationControlAdvertiserFolder = 'RotationControlAdvertiserFolder',
    RotationControlAdvertiserSplit = 'RotationControlAdvertiserSplit',
    RotationControlAffiliateFolder = 'RotationControlAffiliateFolder',
    RotationControlAffiliateSplit = 'RotationControlAffiliateSplit',
    RotationContolAffiliateFolder = 'RotationContolAffiliateFolder',
    CapFolder = 'CapFolder',
}


export enum CreateTreeFolderType {
    CountryFolder = 'CountryFolder',
    CountrySplitFolder = 'CountrySplitFolder',
    AdvertiserFolder = 'AdvertiserFolder',
    AdvertiserSplit = 'AdvertiserSplit',
    AffiliateFolder = 'AffiliateFolder',
    AffiliateSplit = 'AffiliateSplit',
    ContolAffiliateFolder = 'ContolAffiliateFolder',
    CapFolder = 'CapFolder',
}





export interface BaseFolder extends TreeOption {
    id: number;
    name: string;
    disabled: boolean;
    children: TreeFolder[] | undefined;
    type: TreeFolderType;
    prefix: () => VNode;
}

interface CountryFolder extends BaseFolder {
    countries: string[];
}

interface AdvertiserFolder extends BaseFolder {
    advertiser: {
        id: number;
        name: string;
    };
}

interface CapFolder extends BaseFolder {
    cap_amount: number;
    current_amount: number;
    cap_type: string;
}

interface AffiliateFolder extends BaseFolder {
    affiliate: {
        id: number;
        name: string;
    };
}

export type TreeFolder = CountryFolder | AdvertiserFolder | CapFolder | AffiliateFolder;



export interface CreateFolder {
    name: string;
    parent: number | null;
    type: CreateTreeFolderType;
    // can be any other fields countries, affilaite id, advertiser id, cap amount, cap type
    [key: string]: any;
}


export interface CreateCountryFolder extends CreateFolder {
    countries: string[];
}

export interface CreateAdvertiserFolder extends CreateFolder {
    advertiser_id: number;
}

export interface CreateCapFolder extends CreateFolder {
    cap_amount: number;
    cap_type: string;
}

export interface CreateAffiliateFolder extends CreateFolder {
    affiliate_id: number;
}