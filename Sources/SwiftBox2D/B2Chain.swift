import box2d

public class B2Chain {
    /// Gets the ID of this chain.
    private(set) public var id: b2ChainId

    /// Instantiates a `B2Chain` from a given chain ID.
    public init(id: b2ChainId) {
        self.id = id
    }

    /// Creates a new chain shape on a given body.
    public convenience init(body: B2Body, _ def: b2ChainDef) {
        var def = def
        let id = b2CreateChain(body.id, &def)

        self.init(id: id)
    }

    /// Destroys this chain, removing it from the world.
    public func destroy() {
        b2DestroyChain(id)

        self.id = b2_nullChainId
    }
}
