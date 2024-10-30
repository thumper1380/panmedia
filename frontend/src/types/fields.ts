
export enum FieldType {
    CharField = "CharField",
    EmailField = "EmailField",
    IntegerField = "IntegerField",
    RelatedField = "RelatedField",
    CountryField = "CountryField",
    StateField = "StateField",
    SelectField = "SelectField",
    DateTimeField = "DateTimeField",
    DecimalField = "DecimalField",
    BooleanField = "BooleanField",
    JSONField = "JSONField",
    IPAddressField = "IPAddressField",
    SlugField = "SlugField",
    URLField = "URLField",
}


export interface Field {
    key: string;
    type: FieldType;
    title: string;
    read_only: boolean;
}