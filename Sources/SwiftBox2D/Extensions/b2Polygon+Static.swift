import box2d

extension B2Polygon {
    public static func makeBox(halfWidth: Float, halfHeight: Float) -> B2Polygon {
        return b2MakeBox(halfWidth, halfHeight)
    }
    
    public static func makeBox(halfSize: B2Vec2) -> B2Polygon {
        return b2MakeBox(halfSize.x, halfSize.y)
    }
    
    public static func makeSquare(halfWidth: Float) -> B2Polygon {
        return b2MakeSquare(halfWidth)
    }
}
