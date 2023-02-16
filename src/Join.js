import Relation from './Relation';

class Join {
    constructor(condition) {
        this.condition = condition;
        this.joinType = "";
        this.left = new Relation();
        this.right = new Relation();
    }
}

export default Join;