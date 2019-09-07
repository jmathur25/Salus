//
//  ViewController.swift
//  Salus
//
//  Created by Jackie Oh on 9/6/19.
//  Copyright © 2019 Jackie Oh. All rights reserved.
//

import UIKit
import WebKit
import CoreLocation
import CoreMotion

class ViewController: UIViewController, WKUIDelegate, UITextFieldDelegate {
  
  let locationManager = CLLocationManager()
  let altimeter = CMAltimeter()
  
  var relativeAltitude = 0.0
  var pressure = 0.0
  
  // MARK: Outlets
  @IBOutlet weak var webview: WKWebView!
  @IBOutlet weak var messageTextField: UITextField!
  
  override func viewDidLoad() {
    super.viewDidLoad()
    
    messageTextField.delegate = self
    
    NotificationCenter.default.addObserver(self, selector: #selector(keyboardWillShow), name: UIResponder.keyboardWillShowNotification, object: nil)
    NotificationCenter.default.addObserver(self, selector: #selector(keyboardWillHide), name: UIResponder.keyboardWillHideNotification, object: nil)

    
    locationManager.delegate = self
    
    let location = locationManager.location
    
    if location != nil {
      let latitude = location?.coordinate.latitude as! Double
      let longitude = location?.coordinate.longitude as! Double
      
      let urlString = Constants.siteUrl + String(latitude) + "/" + String(longitude)
      // Do any additional setup after loading the view.
      let myURL = URL(string:urlString)
      let myRequest = URLRequest(url: myURL!)
      webview.load(myRequest)
    }
  }
  
  @objc func keyboardWillShow(notification: NSNotification) {
    if let keyboardSize = (notification.userInfo?[UIResponder.keyboardFrameBeginUserInfoKey] as? NSValue)?.cgRectValue {
      if self.view.frame.origin.y == 0 {
        self.view.frame.origin.y -= keyboardSize.height
      }
    }
  }
  
  @objc func keyboardWillHide(notification: NSNotification) {
    if self.view.frame.origin.y != 0 {
      self.view.frame.origin.y = 0
    }
  }
  
  
  func textFieldShouldReturn(_ textField: UITextField) -> Bool {
    print("here")
    textField.resignFirstResponder()
    return true
  }
  
}

extension ViewController: CLLocationManagerDelegate {
  // send location to database
  func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
    if let currentLocation = locations.last {
      print("Current location: \(currentLocation)")
    }
  }
  
  func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
    print(error)
  }
}

