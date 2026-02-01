import SwiftBox2D

@usableFromInline
let _identityMatrix = Matrix3x3(diagonal: 1)

// MARK: Matrix-transformation
extension B2Vec2 {

    /// Creates a matrix that when multiplied with a Vector2 object applies the
    /// given set of transformations.
    ///
    /// If all default values are set, an identity matrix is created, which does
    /// not alter a Vector2's coordinates once applied.
    ///
    /// The order of operations are: scaling -> rotation -> translation
    @inlinable
    static public func matrix(
        scalingBy scale: B2Vec2 = B2Vec2(x: 1, y: 1),
        rotatingBy angle: Float = 0,
        translatingBy translate: B2Vec2 = B2Vec2.zero
    ) -> Matrix3x3 {

        var matrix = _identityMatrix

        // Prepare matrices

        // Translation:
        //
        // | 0  0  0 |
        // | 0  0  0 |
        // | dx dy 1 |
        //

        matrix *= .make2DTranslation(translate)

        // Rotation:
        //
        // |  cos(a) sin(a) 0 |
        // | -sin(a) cos(a) 0 |
        // |   0       0    1 |
        //

        if angle != 0 {
            matrix *= .make2DRotation(angle)
        }

        // Scaling:
        //
        // | sx 0  0 |
        // | 0  sy 0 |
        // | 0  0  1 |
        //

        matrix *= .make2DScale(scale)

        return matrix
    }

    // Matrix multiplication
    @inlinable
    static public func * (lhs: B2Vec2, rhs: Matrix3x3) -> B2Vec2 {
        let homogenous = Vector3(lhs, z: 1)

        let transformed = rhs.transformPoint(homogenous)

        return B2Vec2(x: transformed.x, y: transformed.y)
    }
}
