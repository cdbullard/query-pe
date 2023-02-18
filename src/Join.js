import Relation from './Relation';

class Join {
    constructor(id, condition, symbol) {
        this.id = id;
        this.condition = condition;
        this.symbol = symbol;
        this.joinType = "";
        this.left = new Relation();
        this.right = new Relation();
    }
}

export default Join;