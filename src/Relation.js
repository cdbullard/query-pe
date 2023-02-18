class Relation {
    constructor(name, alias, id) {
        this.id = id;
        this.name = name;
        this.alias = alias;
        this.attributes = [];
        this.projections = [];
        this.joined = false;
    }
}

export default Relation;