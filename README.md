#  Gesture Controlled Volume System using distance between thumb and index finger ✋

## 📌 Project Overview
This project implements a touchless system volume controller using hand gestures captured through a webcam.  
By measuring the distance between the thumb and index finger, the system dynamically adjusts the volume of the computer in real time.

---

## 🎯 Objectives
- Detect 21 hand landmarks using mediapipe
- Measure distance between thumb and index finger
- Map calculated distance to system volume
- Display real-time volume feedback on UI

---

## 🛠 Technologies & Libraries Used

| Technology | Purpose |
|----------|--------|
| **Python** | Core programming language |
| **OpenCV** | Webcam access and image processing |
| **MediaPipe Hands** | Hand landmark detection (21 landmarks) |
| **PyCAW** | Windows system volume control |
| **NumPy** | Mathematical mapping and interpolation |
| **Flask** | Web-based UI for camera and graphs |

---

## 🧠 System Architecture
1.OpenCV is used to capture hand through webcam
2. MediaPipe is used to detect 21 landmarks on hand
3. Thumb (landmark 4) and Index finger (landmark 8) are tracked  
4. NumPy is used to Euclidean calculate distance between thumb and index finger 
5. Calculated distance is then mapped to volume percentage  
6. Volume smoothing is applied to avoid jerky changes  
7. System volume is updated using PyCAW  
8. Visual feedback is displayed on UI  

---


## 📊 Volume Smoothing Technique
To prevent sudden volume jumps caused by minor hand movement:
- A **moving average filter** is applied
- Last few volume values are averaged
- This ensures stable and natural volume transitions

---

## 🖥 User Interface Features
- Live camera feed
- Hand landmarks visualization
- Real-time volume percentage display
- Volume bar indicator
- Gesture status feedback
- FPS (performance indicator)

---
