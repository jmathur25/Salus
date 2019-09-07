//
//  AppDelegate.swift
//  Salus
//
//  Created by Jackie Oh on 9/6/19.
//  Copyright © 2019 Jackie Oh. All rights reserved.
//

import UIKit
import CoreLocation
import CoreMotion
import UserNotifications

@UIApplicationMain
class AppDelegate: UIResponder, UIApplicationDelegate {

  var window: UIWindow?
  let locationManager = CLLocationManager()
  let center = UNUserNotificationCenter.current()

  func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
    
    if !UserDefaults.standard.bool(forKey: "didSee") {
      UserDefaults.standard.set(true, forKey: "didSee")
      print("here")
      
      let storyboard = UIStoryboard(name: "Main", bundle: nil)
      let viewController = storyboard.instantiateViewController(withIdentifier: "OnboardingController")
      self.window?.rootViewController = viewController
      self.window?.makeKeyAndVisible()
    }
    
    UIApplication.shared.setMinimumBackgroundFetchInterval(10)
    
    // Override point for customization after application launch.
    locationManager.requestAlwaysAuthorization()
    center.requestAuthorization(options: [.alert, .sound]) { granted, error in
    }
        
    locationManager.distanceFilter = 10
    locationManager.allowsBackgroundLocationUpdates = true
    locationManager.delegate = self
    
    return true
  }

  func applicationWillResignActive(_ application: UIApplication) {
    // Sent when the application is about to move from active to inactive state. This can occur for certain types of temporary interruptions (such as an incoming phone call or SMS message) or when the user quits the application and it begins the transition to the background state.
    // Use this method to pause ongoing tasks, disable timers, and invalidate graphics rendering callbacks. Games should use this method to pause the game.
  }
  
  func application(_ application: UIApplication,
                   performFetchWithCompletionHandler completionHandler:
    @escaping (UIBackgroundFetchResult) -> Void) {
    // check to see if emergency is occurring
    if fetchUpdates() {
      // start updating location, sending it to database
      locationManager.startUpdatingLocation()
      locationManager.startMonitoringVisits()
      // start rendering map on user view
    }
  }

  func applicationDidEnterBackground(_ application: UIApplication) {
    // Use this method to release shared resources, save user data, invalidate timers, and store enough application state information to restore your application to its current state in case it is terminated later.
    // If your application supports background execution, this method is called instead of applicationWillTerminate: when the user quits.
  }

  func applicationWillEnterForeground(_ application: UIApplication) {
    // Called as part of the transition from the background to the active state; here you can undo many of the changes made on entering the background.
  }

  func applicationDidBecomeActive(_ application: UIApplication) {
    // Restart any tasks that were paused (or not yet started) while the application was inactive. If the application was previously in the background, optionally refresh the user interface.
  }

  func applicationWillTerminate(_ application: UIApplication) {
    // Called when the application is about to terminate. Save data if appropriate. See also applicationDidEnterBackground:.
  }
  
  func fetchUpdates() -> Bool {
    // get information from himanshu on whether an emergency is occurring or not
    // return true if an emergency is occurring, false otherwise
    return true
  }
  
  func updatePersonLocation(p_id: String, lat: String, long: String) {
    let parameters = ["p_id": p_id, "lat": lat, "long": long]
    
    //create the url with URL
    let url = URL(string: Constants.siteUrl + "person/update_location_person")! //change the url
    
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

extension AppDelegate: CLLocationManagerDelegate {
  // send location to database
  func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
    if let currentLocation = locations.last {
      print("Current location: \(currentLocation)")
      updatePersonLocation(p_id: String(UserDefaults.standard.integer(forKey: "p_id")), lat: String(currentLocation.coordinate.latitude), long: String(currentLocation.coordinate.longitude))
    }
  }
  
  func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
    print(error)
  }
}
