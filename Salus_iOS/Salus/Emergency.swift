//
//  Emergency.swift
//  Salus
//
//  Created by Jackie Oh on 9/7/19.
//  Copyright © 2019 Jackie Oh. All rights reserved.
//

import Foundation

enum EmergencyType : CustomStringConvertible {
  case Fire, ActiveShooter, Tornado, Hurricane, BombThreat, None
  
  var description : String {
    switch self {
    // Use Internationalization, as appropriate.
    case .Fire: return "Fire"
    case .ActiveShooter: return "Active Shooter"
    case .Tornado: return "Tornado"
    case .Hurricane: return "Hurricane"
    case .BombThreat: return "Bomb Threat"
    case .None: return "No Emergency"
    }
  }
}

class Emergency {
  let type:EmergencyType
  
  init(type: EmergencyType) {
    self.type = type
  }
  
  func emergencyHappening() -> Bool {
    return type != EmergencyType.None
  }
  
  func getEmergencyType() -> EmergencyType {
    return self.type
  }
}

var MainEmergencyInstance = Emergency(type: EmergencyType.None)
