// type ColumnType = 'country' | 'state' | 'boolean' | 'link' | 'string' | 'tag';



// export interface Column {
//     name: string;
//     type: ColumnType;
//     label: string;
//     sortable: boolean;
//     filterable: boolean;
//     editable: boolean;
//     width: number;
// }


interface BaseColumn {
    key: string;
    title: string;
    width?: number;
    minWidth?: number;
    maxWidth?: number;
    resizable?: boolean;
}

interface IDFieldColumn extends BaseColumn {
    type: 'IDField';
}

interface CountryFieldColumn extends BaseColumn {
    type: 'CountryField';
}

interface RelatedFieldColumn extends BaseColumn {
    type: 'RelatedField';
}

interface CharFieldColumn extends BaseColumn {
    type: 'CharField';
}

interface TagFieldColumn extends BaseColumn {
    type: 'TagField';
}

interface BooleanFieldColumn extends BaseColumn {
    type: 'BooleanField';
}

interface DateTimeFieldColumn extends BaseColumn {
    type: 'DateTimeField';
}

interface StateFieldColumn extends BaseColumn {
    type: 'StateField';
}


// Union type for all column types
type TableColumn = IDFieldColumn | CountryFieldColumn | RelatedFieldColumn | CharFieldColumn | TagFieldColumn | BooleanFieldColumn | DateTimeFieldColumn | StateFieldColumn;



