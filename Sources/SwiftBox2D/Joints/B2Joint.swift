import box2d

/// Base class for joint types.
public class B2Joint {
    var id: b2JointId

    init(id: b2JointId) {
        self.id = id
    }
}
