export type Attribute = {
    name: string;
    datatype: string;
    primary_key?: boolean;
    foreign_key?: { entity: string; attribute: string };
};

export type Entity = {
    name: string;
    attributes: Array<Attribute>;
};