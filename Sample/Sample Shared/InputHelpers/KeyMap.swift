//
//  KeyMap.swift
//  Sample
//
//  Created by Luiz Fernando Silva on 02/02/26.
//  Copyright © 2026 Luiz Fernando Silva. All rights reserved.
//

class KeyMap {
    var _keys: Dictionary<KeyCode, Double> = [:]
    
    func update(deltaTime: Double) {
        _keys = _keys.mapValues { t in
            if t >= 0.0 {
                return t + deltaTime
            }
            
            return t
        }
    }
    
    func setKeyDown(_ key: KeyCode) {
        guard _keys[key] == nil else {
            return
        }
        
        _keys[key] = 0.0
    }
    
    func setKeyUp(_ key: KeyCode) {
        _keys.removeValue(forKey: key)
    }
    
    func isKeyDown(_ key: KeyCode) -> Bool {
        if let time = _keys[key] {
            return time >= 0.0
        }
        
        return false
    }
    
    func keyHeldTime(_ key: KeyCode) -> Double? {
        return _keys[key]
    }
}
