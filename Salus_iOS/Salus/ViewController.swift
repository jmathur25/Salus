//
//  ViewController.swift
//  Salus
//
//  Created by Jackie Oh on 9/6/19.
//  Copyright © 2019 Jackie Oh. All rights reserved.
//

import UIKit
import CoreLocation

class ViewController: UIViewController, CLLocationManagerDelegate {

  override func viewDidLoad() {
    super.viewDidLoad()
    // Do any additional setup after loading the view.
    let locationManager = CLLocationManager()
  }
  
  // MARK: Actions
  @IBAction func markSafe(_ sender: UIButton) {
  }
  @IBAction func markDanger(_ sender: UIButton) {
  }
  
  func updateLocation() {
    
  }
  
  @IBAction func getLocation(_ sender: Any) {
    // 1
    let status = CLLocationManager.authorizationStatus()
    
    switch status {
    // 1
    case .notDetermined:
      locationManager.requestWhenInUseAuthorization()
      return
      
    // 2
    case .denied, .restricted:
      let alert = UIAlertController(title: "Location Services disabled", message: "Please enable Location Services in Settings", preferredStyle: .alert)
      let okAction = UIAlertAction(title: "OK", style: .default, handler: nil)
      alert.addAction(okAction)
      
      present(alert, animated: true, completion: nil)
      return
    case .authorizedAlways, .authorizedWhenInUse:
      break
      
    }
    
    // 4
    locationManager.delegate = self
    locationManager.startUpdatingLocation()
  }
  
  func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
    if let currentLocation = locations.last {
      print("Current location: \(currentLocation)")
    }
  }
  
  // 2
  func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
    print(error)
  }

}

