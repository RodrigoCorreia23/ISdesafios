export interface Warehouse {
    id: number;
    region: string;
    product_line: string;
    latitude: number;
    longitude: number;
}

export interface Warehouses {
    warehouses: Warehouse[];
}

export interface GraphQlWarehouses {
    data: Warehouses;
}