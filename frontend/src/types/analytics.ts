// enum for the different types of metrics



export enum MetricType {
    Currency = 'MONEY',
    Percentage = 'PERCENTAGE',
    Number = 'NUMBER',
}
export interface MetricData {
    title: string;
    value: number;
    series: { data: Array<[number, number]> }[];
    icon: string;
    type: MetricType;
}


