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

export type EntityWithRenderingState = Entity & {
    x: number;
    y: number;
    layer: number;
    expanded: boolean;
};