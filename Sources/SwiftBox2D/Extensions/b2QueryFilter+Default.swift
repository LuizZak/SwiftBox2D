import box2d

extension b2QueryFilter {
    /// Use this to initialize your query filter.
    public static var `default`: Self {
        b2DefaultQueryFilter()
    }
}
