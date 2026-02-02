import SwiftBox2D

class RayJointPair {
    var rayTranslation: B2Vec2
    var body: B2Body
    var jointDist: Float = 0.0
    var toleranceDist: Float = 0.4
    var joint: B2DistanceJoint?
    
    init(body: B2Body, rayDirection: B2Vec2) {
        self.body = body
        self.rayTranslation = rayDirection
    }
    
    @discardableResult
    func update(world: B2World, origin: B2Vec2, ignore: [B2Body] = []) -> RayCastResult? {
        let result = rayCast(world: world, origin: origin, ignore: ignore)
        updateJoint(world: world, result: result)
        
        return result
    }
    
    func rayCast(world: B2World, origin: B2Vec2, ignore: [B2Body] = []) -> RayCastResult? {
        var latest: RayCastResult?
        
        world.castRay(origin: origin, translation: rayTranslation, filter: .default()) { shape, point, normal, fraction in
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
        let resultPoint = result?.point ?? (body.getPosition() + rayTranslation)
        
        var recreateJoint = false
        if let joint {
            let pointA = joint.worldPointA()
            let pointB = joint.worldPointB()
            
            if pointA.distance(to: pointB) > jointDist * 1.1 {
                recreateJoint = true
            }
            
            if resultPoint.distance(to: pointB) > toleranceDist {
                recreateJoint = true
            }
        } else {
            recreateJoint = true
        }
        
        if recreateJoint {
            detachJoint()
            
            if let result {
                var jointDef = b2DistanceJointDef.default()
                jointDef.base.bodyIdA = body.id
                jointDef.base.bodyIdB = result.body.id
                jointDef.base.localFrameA = .identity
                jointDef.base.localFrameB = .init(p: result.body.getLocalPoint(result.point), q: .identity)
                jointDef.length = rayTranslation.length * 0.95
                jointDef.maxLength = jointDef.length * 1.2
                jointDef.enableSpring = true
                jointDef.hertz = 2.0
                jointDef.dampingRatio = 0.3
                
                self.joint = world.createJoint(jointDef)
                
                jointDist = rayTranslation.length
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
