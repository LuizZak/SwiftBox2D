import Foundation
import CoreGraphics
import SwiftBox2D
import simd

var renderingScale: B2Vec2 = B2Vec2(x: 1, y: 1)
var renderingOffset: B2Vec2 = B2Vec2(x: 0, y: 0)

extension B2Vec2 {
    typealias NativeMatrixType = Matrix3x3
    
    /// Helper post-fix alias for global function `toWorldCoords(self)`
    var inWorldCoords: B2Vec2 {
        return self
    }

    /// Helper post-fix alias for global function `toScreenCoords(self)`
    var inScreenCoords: B2Vec2 {
        return self
    }
}

protocol DemoSceneDelegate: AnyObject {
    func didUpdatePhysicsTimer(intervalCount: Int,
                               timeMilliRounded: TimeInterval,
                               fps: TimeInterval,
                               avgMilliRounded: TimeInterval)
    func didUpdateRenderTimer(timeMilliRounded: TimeInterval, fps: TimeInterval)
}

class DemoScene {
    weak var delegate: DemoSceneDelegate?
    
    var boundsSize: CGSize
    
    /// Main OpenGL VAO in which all bodies will be rendered on
    var vertexBuffer: VertexBuffer
    
    var updateLabelStopwatch = Stopwatch(startTime: 0)
    var renderLabelStopwatch = Stopwatch(startTime: 0)
    var intervals: [CFAbsoluteTime] = []
    
    var viewportMatrix = B2Vec2.matrix(scalingBy: 1.0 / (renderingScale / 2), translatingBy: renderingOffset)
    let baseRenderingScale = B2Vec2(x: 25.8, y: 25.8)
    
    let labelUpdateInterval = 0.5
    
    var inputMode = InputMode.dragBody
    
    // The location of the user's finger, in physics world coordinates
    var pointerLocation = B2Vec2.zero
    
    /// Whether to perform a detailed render of the scene. Detailed rendering
    /// renders, along with the body shape, the body's normals, global shape and
    /// axis, and collision normals
    var useDetailedRender = true
    
    init(boundsSize: CGSize, delegate: DemoSceneDelegate?) {
        self.boundsSize = boundsSize
        self.delegate = delegate
        vertexBuffer = VertexBuffer()
        renderingOffset = B2Vec2(x: 300, y: 384)
        renderingScale = baseRenderingScale
    }
    
    func update(timeSinceLastFrame: TimeInterval) {
        let sw = Stopwatch()
        
        updateWithTimeSinceLastUpdate(timeSinceLastFrame)
        
        let time = sw.stop() * 1000
        
        intervals.append(time)
        if intervals.count > 200 {
            intervals = Array(intervals.dropFirst(intervals.count - 200))
        }
        
        if let duration = updateLabelStopwatch.duration, duration > labelUpdateInterval {
            updateLabelStopwatch.reset()
            
            let timeMilli = time
            let timeMilliRounded = round(timeMilli * 100) / 100
            let fps = 1000 / timeMilliRounded
            
            let avgMilli = intervals.reduce(0, +) / CFAbsoluteTime(intervals.count)
            let avgMilliRounded = round(avgMilli * 100) / 100
            
            DispatchQueue.main.async {
                self.delegate?.didUpdatePhysicsTimer(intervalCount: self.intervals.count,
                                                     timeMilliRounded: timeMilliRounded,
                                                     fps: fps,
                                                     avgMilliRounded: avgMilliRounded)
            }
        }
    }
    
    func renderToVaoBuffer() {
        vertexBuffer.clearVertices()
        
        let sw = Stopwatch.startNew()
        
        if useDetailedRender {
            
        }
        
        // Adjust viewport by the aspect ratio
        let viewportMatrix = matrixForOrthoProjection(width: Float(boundsSize.width), height: Float(boundsSize.height))
        
        // Matrix to transform JelloSwift's coordinates into proper coordinates
        // for OpenGL
        let mat = B2Vec2.matrix(scalingBy: renderingScale, rotatingBy: 0, translatingBy: renderingOffset)
        
        // Convert point to screen coordinates
        vertexBuffer.applyTransformation((mat * viewportMatrix).matrix4x4())
        
        if let duration = renderLabelStopwatch.duration, duration > labelUpdateInterval {
            renderLabelStopwatch.reset()
            
            let time = round(sw.stop() * 1000 * 20) / 20
            let fps = 1000 / time
            
            delegate?.didUpdateRenderTimer(timeMilliRounded: time, fps: fps)
        }
    }
    
    func updateWithTimeSinceLastUpdate(_ timeSinceLast: CFTimeInterval) {
        // Update the physics world
        for _ in 0..<5 {
            
        }
    }
    
    /// Enum used to modify the input mode of the test simulation
    enum InputMode: Int {
        /// Creates a jiggly ball under the finger on tap
        case createBall
        /// Allows dragging bodies around
        case dragBody
    }
}

// MARK: - Input
extension DemoScene {
    func touchDown(at screenPoint: B2Vec2) {
        let worldPoint = screenPoint.inWorldCoords
        
//        /* Called when a touch begins */
//        if inputMode == .createBall {
//            createBouncyBall(worldPoint)
//        } else if inputMode == .dragBody {
//            // Select the closest point-mass to drag
//            pointerLocation = worldPoint
//            
//            draggingPoint = world.closestPointMass(to: pointerLocation)
//        }
    }
    
    func touchMoved(at screenPoint: B2Vec2) {
        let worldPoint = screenPoint.inWorldCoords
        
        pointerLocation = worldPoint
    }
    
    func touchEnded(at screenPoint: B2Vec2) {
        // Reset dragging point
        
    }
}

extension DemoScene {
    func initializeLevel() {
        
    }
}

// MARK: - Rendering
extension DemoScene {
    ///                                               1
    /// Returns a 3x3 matrix for projecting onto a -1 0 1 -style space such that
    ///                                              -1
    /// a [0, 0] vector projects into the top-left (1, -1), and [width, height]
    /// projects into the bottom-right (-1, 1).
    ///
    func matrixForOrthoProjection(width: Float, height: Float) -> B2Vec2.NativeMatrixType {
        let size = B2Vec2(x: width, y: height)
        let scaledSize = B2Vec2(x: 1 / width, y: 1 / height) * 2
        
        let matrix = B2Vec2.matrix(translatingBy: -size / 2)
        return matrix * B2Vec2.matrix(scalingBy: scaledSize)
    }
    
#if false
    
    func drawLine(from start: B2Vec2, to end: B2Vec2, color: UInt = 0xFFFFFFFF, width: Float = 0.5) {
        
        let normal = ((start - end).normalized.perpendicular() / 15) * width
        
        let i0 = vertexBuffer.addVertex(start + normal, color: color)
        let i1 = vertexBuffer.addVertex(end + normal, color: color)
        let i2 = vertexBuffer.addVertex(end - normal, color: color)
        let i3 = vertexBuffer.addVertex(start - normal, color: color)
        
        vertexBuffer.addTriangleWithIndices(i0, i1, i2)
        vertexBuffer.addTriangleWithIndices(i2, i3, i0)
        
        // Draw a pointy line to make the line look less squared
        let p0 = vertexBuffer.addVertex(start - normal.perpendicular(), color: color)
        let p1 = vertexBuffer.addVertex(end + normal.perpendicular(), color: color)
        
        vertexBuffer.addTriangleWithIndices(i0, p0, i1)
        vertexBuffer.addTriangleWithIndices(i2, p1, i3)
    }
    
    func drawCircle(center point: B2Vec2, radius: Float, sides: Int = 10, color: UInt = 0xFFFFFFFF) {
        let prevColor = vertexBuffer.currentColor
        vertexBuffer.currentColor = color
        defer {
            vertexBuffer.currentColor = prevColor
        }
        
        let shape =
            ClosedShape
                .circle(ofRadius: radius, pointCount: sides)
                .transformedBy(translatingBy: point)
        
        // Add triangles that connect the edges to a center vertex to form the
        // circle
        let center = vertexBuffer.addVertex(point)
        
        for vert in shape.localVertices {
            vertexBuffer.addVertex(x: vert.x, y: vert.y)
        }
        
        for vert in 0..<shape.localVertices.count {
            let next = (vert + 1) % shape.localVertices.count
            
            vertexBuffer.addTriangleWithIndices(center + UInt32(vert) + 1,
                                                center + UInt32(next) + 1,
                                                center)
        }
    }
    
    func drawPolyOutline(_ points: [B2Vec2], color: UInt = 0xFFFFFFFF, width: Float = 0.5) {
        guard var last = points.last else {
            return
        }
        
        for point in points {
            drawLine(from: point, to: last, color: color, width: width)
            last = point
        }
    }
    
    /// Renders the dragging shape line
    func drawDrag() {
        // Dragging point
        guard let (body, index) = draggingPoint, inputMode == InputMode.dragBody else {
            return
        }
        
        // Create the path to draw
        let lineStart = body.pointMasses[index].position
        let lineEnd = pointerLocation
        
        drawLine(from: lineStart, to: lineEnd, color: 0xFF00DD00)
    }
    
    func drawJoint(_ joint: BodyJoint) {
        let start = joint.bodyLink1.position
        let end = joint.bodyLink2.position
        
        var color: UInt = joint.enabled ? 0xFFEEEEEE : 0xFFCCCCCC
        
        // Color joint a different shade depending on how far from rest shape
        // its bodies are (from gray at 0% off to light-red at >100% off)
        let distance = start.distance(to: end)
        if !joint.restDistance.inRange(value: distance) {
            let clamped = joint.restDistance.clamp(value: distance)
            
            if clamped > 0 {
                var overhead: Float
                
                if distance < clamped {
                    overhead = distance / clamped
                } else {
                    overhead = clamped / distance
                }
                
                // Normalize to 0 - 1
                overhead = max(0, min(1, overhead))
                // Now shift range to be 0.5 - 1 (this decreases strong red shades)
                overhead = overhead / 2 + 0.5
                
                let resVector =
                    Color4.fromUIntARGB(color).vector * Color4(r: 1, g: overhead, b: overhead, a: 1).vector
                
                color = Color4(vector: resVector).toUIntARGB()
            }
        }
        
        if !useDetailedRender && joint.restDistance.minimumDistance > 0.2 {
            let springWidth = 0.2
            let segmentCount = Int((joint.restDistance.minimumDistance / 0.1).rounded(.up))
            
            func positionForSegment(_ offset: Int) -> B2Vec2 {
                if offset == 0 {
                    return start
                }
                if offset == segmentCount {
                    return end
                }
                
                let segPosition = start.ratio(Float(offset) / Float(segmentCount), to: end)
                let segPerp = (end - start).perpendicular().normalized() * Float(springWidth)
                
                let segmentPosition: B2Vec2
                
                if offset.isMultiple(of: 2) {
                    segmentPosition = segPosition + segPerp
                } else {
                    segmentPosition = segPosition - segPerp
                }
                
                return segmentPosition
            }
            
            for seg in 1...segmentCount {
                let start = positionForSegment(seg - 1)
                let end = positionForSegment(seg)
                
                drawLine(from: start, to: end, color: color)
            }
        } else {
            if joint.bodyLink1.linkType == .edge {
                drawCircle(center: start, radius: 0.15, color: color)
            }
            if joint.bodyLink2.linkType == .edge {
                drawCircle(center: end, radius: 0.15, color: color)
            }
            
            // Draw active range for joint
            switch joint.restDistance {
            case .fixed:
                drawLine(from: start, to: end, color: color)
                
            case let .ranged(min, max):
                let length: Float = 0.3
                let dir = (end - start).normalized()
                var startRange = start + dir * min
                var endRange = start + dir * max
                
                if start.distanceSquared(to: end) < (min * min) {
                    startRange = end
                }
                if start.distanceSquared(to: end) > (max * max) {
                    endRange = end
                }
                
                let perp = dir.perpendicular()
                
                drawLine(from: startRange + perp * -length,
                         to: startRange + perp * length,
                         color: color)
                
                drawLine(from: endRange + perp * -length,
                         to: endRange + perp * length,
                         color: color)
                
                drawLine(from: start, to: end, color: color)
                drawLine(from: startRange, to: endRange, color: color)
            }
        }
    }
    
    func drawBody(_ body: Body) {
        var bodyColor: UInt = 0x7DFFFFFF
        if let color = body.objectTag as? UInt {
            bodyColor = color
        } else if let color = body.objectTag as? Color4 {
            bodyColor = color.toUIntARGB()
        } else if let color = body.objectTag as? Color {
            bodyColor = Color4.fromUIColor(color).toUIntARGB()
        }
        
        // Helper lazy body fill drawing inner function
        func drawBodyFill() {
            // Triangulate body's polygon
            guard let (vertices, indices) = LibTessTriangulate.process(polygon: body.vertices) else {
                return
            }
            
            let start = UInt32(vertexBuffer.vertices.count)
            
            let prev = vertexBuffer.currentColor
            vertexBuffer.currentColor = bodyColor
            
            for vert in vertices {
                vertexBuffer.addVertex(x: vert.x, y: vert.y)
            }
            
            vertexBuffer.currentColor = prev
            
            // Add vertex index triplets
            for i in 0..<indices.count / 3 {
                vertexBuffer.addTriangleWithIndices(start + UInt32(indices[i * 3]),
                                                    start + UInt32(indices[i * 3 + 1]),
                                                    start + UInt32(indices[i * 3 + 2]))
            }
        }
        
        let shapePoints = body.vertices
        
        if !useDetailedRender {
            // Don't do any other rendering other than the body's buffer
            drawBodyFill()
            let lineColorVec = (Color4.fromUIntARGB(bodyColor).vector * Color4(r: 0.7, g: 0.6, b: 0.8, a: 1).vector)
            drawPolyOutline(shapePoints, color: Color4(vector: lineColorVec).toUIntARGB(), width: 1)
            return
        }
        
        // Draw normals, for pressure bodies
        if body.component(ofType: PressureComponent.self) != nil {
            for point in body.pointMasses {
                drawLine(from: point.position, to: point.position + point.normal / 3, color: 0xFFEC33EC)
            }
        }
        
        // Draw the body's global shape
        drawPolyOutline(body.globalShape, color: 0xFF777777)
        
        // Draw lines going from the body's outer points to the global shape indices
        for (globalShape, p) in zip(body.globalShape, body.pointMasses) {
            let start = p.position
            let end = globalShape
            
            drawLine(from: start, to: end, color: 0xFF449944)
        }
        
        // Draw the body now
        drawBodyFill()
        drawPolyOutline(shapePoints, color: 0xFF000000)
        
        // Draw the body axis
        let axisUp    = [body.derivedPos, body.derivedPos + B2Vec2(x: 0, y: 0.6).rotated(by: body.derivedAngle)]
        let axisRight = [body.derivedPos, body.derivedPos + B2Vec2(x: 0.6, y: 0).rotated(by: body.derivedAngle)]
        
        // Rep Up vector
        drawLine(from: axisUp[0], to: axisUp[1], color: 0xFFED0000)
        // Green Right vector
        drawLine(from: axisRight[0], to: axisRight[1], color: 0xFF00ED00)
    }
    
#endif // false
}

extension B2Vec2.NativeMatrixType {
    
    /// Returns a 4x4 floating-point transformation matrix for this matrix
    /// object
    func matrix4x4() -> float4x4 {
        var matrix = float4x4(diagonal: [1, 1, 1, 1])
        
        matrix[0] = .init(x: Float(self[0, 0]), y: Float(self[0, 1]), z: 0, w: Float(self[0, 2]))
        matrix[1] = .init(x: Float(self[1, 0]), y: Float(self[1, 1]), z: 0, w: Float(self[1, 2]))
        matrix[2] = .init(x: Float(self[2, 0]), y: Float(self[2, 1]), z: 1, w: Float(self[2, 2]))
        matrix[3] = .init(x: 0, y: 0, z: 0, w: 1)
        
        return matrix
    }
}
