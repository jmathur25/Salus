//
//  Emergency.swift
//  Salus
//
//  Created by Jackie Oh on 9/7/19.
//  Copyright © 2019 Jackie Oh. All rights reserved.
//

import Foundation

enum EmergencyType{
  case Fire, ActiveShooter, Tornado, Hurricane, BombThreat, None
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
