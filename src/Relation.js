class Relation {
    constructor(name, alias) {
        this.name = name;
        this.alias = alias;
        this.attributes = [];
        this.projections = [];
        this.joined = false;
    }
}

export default Relation;