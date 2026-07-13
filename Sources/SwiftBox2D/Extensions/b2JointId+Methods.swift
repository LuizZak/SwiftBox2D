import box2d

extension b2JointId {
    public var isNull: Bool {
        return index1 == 0
    }
}
