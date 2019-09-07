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
    let parameters = ["uuid":uuid,"school":school]
    
    //create the url with URL
    let url = URL(string: Constants.siteUrl + "person/createPerson")! //change the url
    
    //create the session object
    let session = URLSession.shared
    
    //now create the URLRequest object using the url object
    var request = URLRequest(url: url)
    request.httpMethod = "POST" //set http method as POST
    
    do {
      request.httpBody = try JSONSerialization.data(withJSONObject: parameters, options: .prettyPrinted) // pass dictionary to nsdata object and set it as request body
    } catch let error {
      print(error.localizedDescription)
    }
    
    request.addValue("application/json", forHTTPHeaderField: "Content-Type")
    request.addValue("application/json", forHTTPHeaderField: "Accept")
    
    //create dataTask using the session object to send data to the server
    let task = session.dataTask(with: request as URLRequest, completionHandler: { data, response, error in
      
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

}
