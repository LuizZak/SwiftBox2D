import box2d

public class B2Chain {
    var id: b2ChainId

    init(id: b2ChainId) {
        self.id = id
    }

    deinit {
        b2DestroyChain(id)
    }
}
