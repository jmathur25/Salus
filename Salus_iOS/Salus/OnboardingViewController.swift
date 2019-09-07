//
//  OnboardingViewController.swift
//  Salus
//
//  Created by Jackie Oh on 9/7/19.
//  Copyright © 2019 Jackie Oh. All rights reserved.
//

import UIKit

class OnboardingViewController: UIViewController {
  
  // MARK: Outlets
  @IBOutlet weak var schoolTextField: UITextField!
  
    override func viewDidLoad() {
        super.viewDidLoad()

        // Do any additional setup after loading the view.

    }
    
  @IBAction func enter(_ sender: UIButton) {
    let uuid = UIDevice.current.identifierForVendor?.uuidString
    let school  = schoolTextField.text
    
    addPersonToDb(uuid: uuid!, school: school!)
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
  
  func addPersonToDb(uuid: String, school: String) {
    //create the url with URL
    let url = URL(string: Constants.siteUrl + "person/createPerson?uuid=" + uuid + "&school=" + school)!
    
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
            print("ADDED PERSON TO DATABASE")
            print("Person id: \(json[0][0])")
            UserDefaults.standard.set("pid", forKey: "\(json[0][0])")
            // handle json...
          }
        } catch let error {
          print(error.localizedDescription)
        }

      }
    }
    task.resume()
  }

}
