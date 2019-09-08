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
//import CoreMotion

class ViewController: UIViewController, WKUIDelegate, UITextFieldDelegate {
  
  let locationManager = CLLocationManager()
//  let altimeter = CMAltimeter()
//
//  var relativeAltitude = 0.0
//  var pressure = 0.0
  
  // MARK: Outlets
  @IBOutlet weak var webview: WKWebView!
  @IBOutlet weak var messageTextField: UITextField!
  @IBOutlet weak var topBanner: UIView!
  @IBOutlet weak var statusLabel: UILabel!
  
  override func viewDidLoad() {
    super.viewDidLoad()
    
    let screenBounds = self.view.bounds
    
    messageTextField.delegate = self
    
    NotificationCenter.default.addObserver(self, selector: #selector(keyboardWillShow), name: UIResponder.keyboardWillShowNotification, object: nil)
    NotificationCenter.default.addObserver(self, selector: #selector(keyboardWillHide), name: UIResponder.keyboardWillHideNotification, object: nil)
    
    var emergencyType =  MainEmergencyInstance.getEmergencyType()
    statusLabel.text = "Status: \(emergencyType)"

    if emergencyType != EmergencyType.None {
      topBanner.backgroundColor = UIColor.red
    }
    
    // do ui stuff
//    self.topBanner.bounds = CGRect(x: 0, y: 0, width: screenBounds.width, height: screenBounds.height / 6)
//    self.webview.bounds = CGRect(x: 0, y: screenBounds.height / 6, width: screenBounds.width, height: screenBounds.height *  4 / 6)
    
    locationManager.delegate = self
    let location = locationManager.location
    
    if location != nil {
      let latitude = location?.coordinate.latitude as! Double
      let longitude = location?.coordinate.longitude as! Double
      
      let urlString = Constants.siteUrl + "15/" + String(latitude) + "/" + String(longitude)
      // Do any additional setup after loading the view.
      print(urlString)
      let myURL = URL(string:urlString)
      let myRequest = URLRequest(url: myURL!)
      webview.load(myRequest)
    }
  }
  
  // MARK: Actions
  @IBAction func sendMessage(_ sender: UIButton) {
    if messageTextField.canResignFirstResponder {
      messageTextField.resignFirstResponder
    }
    
    let message = messageTextField.text
    
    let pid = UserDefaults.standard.string(forKey: "pid")
    let school = UserDefaults.standard.string(forKey: "school")
    
    let parameters = ["pid" : pid!, "school" : school!, "message" : message!]
    
    let webUrl = Constants.siteUrl + "message/send"
    print(webUrl)

    let url = URL(string: webUrl)
    
    //now create the URLRequest object using the url object
    var request = URLRequest(url: url!)
    request.httpMethod = "POST" //set http method as POST
    
    do {
      request.httpBody = try JSONSerialization.data(withJSONObject: parameters, options: .prettyPrinted) // pass dictionary to nsdata object and set it as request body
    } catch let error {
      print(error.localizedDescription)
    }
    
    request.addValue("application/json", forHTTPHeaderField: "Content-Type")
    request.addValue("application/json", forHTTPHeaderField: "Accept")
    
    //create dataTask using the session object to send data to the server
    let task = URLSession.shared.dataTask(with: request as URLRequest, completionHandler: { data, response, error in
      
      guard error == nil else {
        return
      }
      
      guard let data = data else {
        return
      }
      
      do {
        //create json object from data
        if let json = try JSONSerialization.jsonObject(with: data, options: .mutableContainers) as? [String: Any] {
          print(json)
          // handle json...
        }
      } catch let error {
        print(error.localizedDescription)
      }
    })
    task.resume()
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
  
  override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
    view.endEditing(true)
  }
}

