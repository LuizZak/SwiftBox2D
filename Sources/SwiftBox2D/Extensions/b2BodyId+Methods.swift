import box2d

extension b2BodyId {
    public var isNull: Bool {
        return index1 == 0
    }
}
