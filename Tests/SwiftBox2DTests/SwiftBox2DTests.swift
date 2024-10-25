import Testing

@testable import SwiftBox2D

@Suite
struct SwiftBox2DTests {
    @Test
    func worldStep() throws {
        let step: Float = 1.0 / 60
        let world = B2World()

        world.step(step)
    }

    @Test
    func visibleSymbols() {
        _=B2AABB()
        _=B2Vec2.zero
    }
}
