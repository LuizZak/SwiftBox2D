import SwiftBox2D

class RayJointPair {
    var rayDirection: B2Vec2
    var body: B2Body
    var jointDist: Float = 0.0
    var toleranceDist: Float = 0.15
    var joint: B2DistanceJoint?
    
    init(body: B2Body, rayDirection: B2Vec2) {
        self.body = body
        self.rayDirection = rayDirection
    }
    
    @discardableResult
    func update(world: B2World, origin: B2Vec2, ignore: [B2Body] = []) -> RayCastResult? {
        let result = rayCast(world: world, origin: origin, ignore: ignore)
        updateJoint(world: world, result: result)
        
        return result
    }
    
    func rayCast(world: B2World, origin: B2Vec2, ignore: [B2Body] = []) -> RayCastResult? {
        var latest: RayCastResult?
        
        world.castRay(origin: origin, translation: rayDirection, filter: .default) { shape, point, normal, fraction in
            let bodyId = shape.getBody()
            for body in ignore {
                if body.id == bodyId {
                    return .ignore
                }
            }
            
            if let latestResult = latest {
                if fraction < latestResult.fraction {
                    latest = .init(body: B2Body(id: bodyId), origin: origin, point: point, normal: normal, fraction: fraction)
                }
            } else {
                latest = .init(body: B2Body(id: bodyId), origin: origin, point: point, normal: normal, fraction: fraction)
            }
            
            return .clip(fraction: fraction)
        }
        
        return latest
    }
    
    func hasJoint() -> Bool {
        return joint != nil
    }
    
    func detachJoint() {
        joint?.destroy(wakeAttached: true)
        joint = nil
    }
    
    func updateJoint(world: B2World, result: RayCastResult?) {
        var recreateJoint = false
        if let joint {
            let pointA = joint.worldPointA()
            let pointB = joint.worldPointB()
            
            if pointA.distance(to: pointB) > jointDist * 1.1 {
                recreateJoint = true
            }
            
            if let result {
                if result.point.distance(to: pointB) > toleranceDist {
                    recreateJoint = true
                }
            }
        } else {
            recreateJoint = true
        }
        
        if recreateJoint {
            detachJoint()
            
            if let result {
                var jointDef = b2DistanceJointDef.default
                jointDef.base.bodyIdA = body.id
                jointDef.base.bodyIdB = result.body.id
                jointDef.base.localFrameA = .identity
                jointDef.base.localFrameB = .init(p: result.body.getLocalPoint(result.point), q: .identity)
                jointDef.length = rayDirection.length
                jointDef.maxLength = jointDef.length * 1.2
                jointDef.enableSpring = true
                jointDef.hertz = 2.0
                jointDef.dampingRatio = 0.3
                
                self.joint = world.createJoint(jointDef)
                
                jointDist = rayDirection.length
            }
        }
    }
}

struct RayCastResult {
    var body: B2Body
    var origin: B2Vec2
    var point: B2Vec2
    var normal: B2Vec2
    var fraction: Float
    
    var length: Float {
        origin.distance(to: point)
    }
}
