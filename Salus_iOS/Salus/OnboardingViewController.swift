//
//  OnboardingViewController.swift
//  Salus
//
//  Created by Jackie Oh on 9/7/19.
//  Copyright © 2019 Jackie Oh. All rights reserved.
//

import UIKit

class OnboardingViewController: UIViewController, UITextFieldDelegate {
  
  // MARK: Outlets
  @IBOutlet weak var salusLogo: UIImageView!
  @IBOutlet weak var nameTextField: UITextField!
  @IBOutlet weak var schoolTextField: UITextField!
  @IBOutlet weak var phoneNumberTextField: UITextField!
  
    override func viewDidLoad() {
        super.viewDidLoad()
      
      let screenBounds = self.view.bounds
      self.nameTextField.delegate = self
      self.schoolTextField.delegate = self
      self.phoneNumberTextField.delegate = self
      
      self.salusLogo.center = CGPoint(x: screenBounds.width / 2 - 10, y: screenBounds.height / 4)
      
      let inputTextBoxPadding = screenBounds.width / 20
      let inputTextBoxHeight = self.nameTextField.bounds.height
      let inputTextBoxStart = screenBounds.height * 1.5 / 3
      
      self.nameTextField.center = CGPoint(x: screenBounds.width / 2, y: inputTextBoxStart)
      self.schoolTextField.center = CGPoint(x: screenBounds.width / 2, y: inputTextBoxStart + inputTextBoxPadding + inputTextBoxHeight)
      self.phoneNumberTextField.center = CGPoint(x: screenBounds.width / 2, y: inputTextBoxStart + 2 * inputTextBoxPadding + 2 * inputTextBoxHeight)
    }
    
  @IBAction func enter(_ sender: UIButton) {
    let uuid = UIDevice.current.identifierForVendor?.uuidString
    let school  = schoolTextField.text
    let name = nameTextField.text
    let phoneNumber = phoneNumberTextField.text
    
    addPersonToDb(uuid: uuid!, school: school!, name: name!, phoneNumber: phoneNumber!)
    self.performSegue(withIdentifier: "initialSegue", sender: self)
  }
  
    /*
    // MARK: - Navigation

    // In a storyboard-based application, you will often want to do a little preparation before navigation
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        // Get the new view controller using segue.destination.
        // Pass the selected object to the new view controller.
    }
    */
  
  func addPersonToDb(uuid: String, school: String, name: String, phoneNumber: String) {
    // Save school to user data
    UserDefaults.standard.set(school, forKey: "school")
    
    //create the url with URL
    let url = URL(string: Constants.siteUrl + "person/createPerson?uuid=\(uuid)&school=\(school)&name=\(phoneNumber)")!
    
    //now create the URLRequest object using the url object
    var request = URLRequest(url: url)
    request.httpMethod = "POST" //set http method as POST
    
    let task = URLSession.shared.dataTask(with: request) { (data, response, error) in
      if let error = error {
        print("error: \(error)")
      } else {
        if let response = response as? HTTPURLResponse {
          print("statusCode: \(response.statusCode)")
        }
        if let data = data, let dataString = String(data: data, encoding: .utf8) {
          print("data: \(dataString)")
        }
        do {
          //create json object from data
          if let json = try JSONSerialization.jsonObject(with: data!, options: .mutableContainers) as? [[Any]] {
            UserDefaults.standard.set("\(json[0][0])", forKey: "pid")
          }
        } catch let error {
          print(error.localizedDescription)
        }

      }
    }
    task.resume()
  }
  
  func textFieldShouldReturn(_ textField: UITextField) -> Bool
  {
    textField.resignFirstResponder()
    return true
  }
  
  override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
    view.endEditing(true)
  }
}
