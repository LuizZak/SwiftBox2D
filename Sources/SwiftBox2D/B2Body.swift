import box2d

public class B2Body {
    var id: b2BodyId

    init(id: b2BodyId) {
        self.id = id
    }

    deinit {
        b2DestroyBody(id)
    }
}
