
export enum FieldType {
    IDField = 'IDField',
    IntegerField = 'IntegerField',
    CountryField = 'CountryField',
    RelatedField = 'RelatedField',
    StateField = 'StateField',
    TagField = 'TagField',
    CharField = 'CharField',
    BooleanField = 'BooleanField',
    DateTimeField = 'DateTimeField',
    StatusField = 'StatusField',
}

export interface Column {
    key: string;
    type: FieldType;
    title: string;
    maxWidth?: number;
    minWidth?: number;
    width?: number;
    resizable?: boolean;
    sortable?: boolean;
}


export interface ApiResponse<T> {
    success?: boolean;
    data?: T;
    columns?: Column[];
}
