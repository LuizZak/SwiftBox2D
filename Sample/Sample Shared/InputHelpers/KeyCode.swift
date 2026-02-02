//
//  KeyCodes.swift
//  Sample
//
//  Created by Luiz Fernando Silva on 02/02/26.
//  Copyright © 2026 Luiz Fernando Silva. All rights reserved.
//

enum KeyCode: UInt16 {
    // Digit
    case d0 = 0x1D
    case d1 = 0x12
    case d2 = 0x13
    case d3 = 0x14
    case d4 = 0x15
    case d5 = 0x17
    case d6 = 0x16
    case d7 = 0x1A
    case d8 = 0x1C
    case d9 = 0x19
    
    // Alphabet
    case a = 0x0
    case b = 0xB
    case c = 0x8
    case d = 0x2
    case e = 0xE
    case f = 0x3
    case g = 0x5
    case h = 0x4
    case i = 0x22
    case j = 0x26
    case k = 0x28
    case l = 0x25
    case m = 0x2E
    case n = 0x2D
    case o = 0x1F
    case p = 0x23
    case q = 0xC
    case r = 0xF
    case s = 0x1
    case t = 0x11
    case u = 0x20
    case v = 0x9
    case w = 0xD
    case x = 0x7
    case y = 0x10
    case z = 0x6
    
    // Signs
    case sectionSign = 0xA
    case grave = 0x32
    case minus = 0x1B
    case equal = 0x18
    case leftBracket = 0x21
    case rightBracket = 0x1E
    case semicolon = 0x29
    case quote = 0x27
    case comma = 0x2B
    case period = 0x2F
    case slash = 0x2C
    case backslash = 0x2A
    
    // Keypad
    case keypad0 = 0x52
    case keypad1 = 0x53
    case keypad2 = 0x54
    case keypad3 = 0x55
    case keypad4 = 0x56
    case keypad5 = 0x57
    case keypad6 = 0x58
    case keypad7 = 0x59
    case keypad8 = 0x5B
    case keypad9 = 0x5C
    case keypadDecimal = 0x41
    case keypadMultiply = 0x43
    case keypadPlus = 0x45
    case keypadDivide = 0x4B
    case keypadMinus = 0x4E
    case keypadEquals = 0x51
    case keypadClear = 0x47
    case keypadEnter = 0x4C
    
    // Special keys
    case space = 0x31
    case returnKey = 0x24
    case tab = 0x30
    case delete = 0x33
    case forwardDelete = 0x75
    case linefeed = 0x34
    case escape = 0x35
    case command = 0x37
    case shift = 0x38
    case capsLock = 0x39
    case option = 0x3A
    case control = 0x3B
    case rightShift = 0x3C
    case rightOption = 0x3D
    case rightControl = 0x3E
    case function = 0x3F
    case volumeUp = 0x48
    case volumeDown = 0x49
    case mute = 0x4A
    case helpOrInsert = 0x72
    
    // F- keys
    case f1 = 0x7A
    case f2 = 0x78
    case f3 = 0x63
    case f4 = 0x76
    case f5 = 0x60
    case f6 = 0x61
    case f7 = 0x62
    case f8 = 0x64
    case f9 = 0x65
    case f10 = 0x6D
    case f11 = 0x67
    case f12 = 0x6F
    case f13 = 0x69
    case f14 = 0x6B
    case f15 = 0x71
    case f16 = 0x6A
    case f17 = 0x40
    case f18 = 0x4F
    case f19 = 0x50
    case f20 = 0x5A
    
    // Navigation
    case home = 0x73
    case end = 0x77
    case pageUp = 0x74
    case pageDown = 0x79
    
    // Arrows
    case leftArrow = 0x7B
    case rightArrow = 0x7C
    case downArrow = 0x7D
    case upArrow = 0x7E
}
