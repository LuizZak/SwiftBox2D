@inlinable
public func calculateTorsionSpringTorque(
    angle: Float, angularMomentum: Float,
    targetAngle: Float,
    targetAngularMomentum: Float,
    springK: Float,
    springD: Float
) -> Float {
    let diff = calculateAngleDifference(angle, targetAngle)
    let diffMoment = angularMomentum - targetAngularMomentum

    return diff * springK - diffMoment * springD
}

/// Returns a value between -pi and pi, relating the difference between two angles.
@inlinable
func calculateAngleDifference<F: FloatingPoint>(_ angle1: F, _ angle2: F) -> F {
    var difference = angle2 - angle1

    difference = (difference + .pi).truncatingRemainder(dividingBy: 2 * .pi)
    while difference < 0 {
        difference += 2 * .pi
    }
    while difference > .pi {
        difference -= 2 * .pi
    }

    return difference
}
