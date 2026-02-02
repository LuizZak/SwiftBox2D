//
//  KeyMap.swift
//  Sample
//
//  Created by Luiz Fernando Silva on 02/02/26.
//  Copyright © 2026 Luiz Fernando Silva. All rights reserved.
//

class KeyMap {
    var _keys: Set<KeyCode> = []
    
    func setKeyDown(_ key: KeyCode) {
        _keys.insert(key)
    }
    
    func setKeyUp(_ key: KeyCode) {
        _keys.remove(key)
    }
    
    func isKeyDown(_ key: KeyCode) -> Bool {
        return _keys.contains(key)
    }
}
