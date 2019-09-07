//
//  ViewController.swift
//  Salus
//
//  Created by Jackie Oh on 9/6/19.
//  Copyright © 2019 Jackie Oh. All rights reserved.
//

import UIKit
import CoreLocation
import CoreMotion

class ViewController: UIViewController, CLLocationManagerDelegate {
  
  let locationManager = CLLocationManager()
  let altimeter = CMAltimeter()
  
  var relativeAltitude = 0.0
  var pressure = 0.0
  
  override func viewDidLoad() {
    super.viewDidLoad()
    // Do any additional setup after loading the view.
    
//    getLocation()
//    
//    if CMAltimeter.isRelativeAltitudeAvailable() {
//      altimeter.startRelativeAltitudeUpdates(to: OperationQueue.main) { (data, error) in
//        self.relativeAltitude = data?.relativeAltitude as! Double
//        self.pressure = data?.pressure as! Double
//        
//        print("relative altitude: ", self.relativeAltitude)
//        print("pressure: ", self.pressure)
//      }
//    }
  }
  
  // MARK: Actions
  @IBAction func markSafe(_ sender: UIButton) {
    //  do stuff
  }
  
  @IBAction func markDanger(_ sender: UIButton) {
    // do stuff
  }
  
  func calculateFloor() {
    
  }
  
  func getLocation() {
    // 1
    let status = CLLocationManager.authorizationStatus()
    
    switch status {
      case .notDetermined:
        locationManager.requestAlwaysAuthorization()
        return
      case .denied, .restricted:
        let alert = UIAlertController(title: "Location Services disabled", message: "Please enable Location Services in Settings", preferredStyle: .alert)
        let okAction = UIAlertAction(title: "OK", style: .default, handler: nil)
        alert.addAction(okAction)
        
        present(alert, animated: true, completion: nil)
        return
      case .authorizedAlways, .authorizedWhenInUse:
        break
      
    }
    
    locationManager.delegate = self
    locationManager.startUpdatingLocation()
  }
  
  func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
    if let currentLocation = locations.last {
      print("Current location: \(currentLocation)")
    }
  }
  
  func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
    print(error)
  }

}

