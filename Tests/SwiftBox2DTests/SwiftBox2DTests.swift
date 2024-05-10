import XCTest
@testable import SwiftBox2D

final class SwiftBox2DTests: XCTestCase {
    func testWorldStep() throws {
        let step: Float = 1.0 / 60
        let world = B2World()
        
        world.step(step)
    }
}
