import box2d

public class B2Chain {
    var id: b2ChainId

    init(id: b2ChainId) {
        self.id = id
    }

    /// Creates a new chain shape on a given body.
    public convenience init(body: B2Body, _ def: b2ChainDef) {
        var def = def
        let id = b2CreateChain(body.id, &def)

        self.init(id: id)
    }
}
