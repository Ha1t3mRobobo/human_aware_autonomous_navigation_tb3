#  Autonomous Human-Aware Robot System (ROS 2)

##  Project Description

This project presents a complete autonomous and intelligent robotic system based on the **TurtleBot3 Waffle Pi** platform equipped with a **Raspberry Pi 4 (8GB)** and developed using **ROS 2 Jazzy Jalisco**.

The system combines classical robotics techniques (SLAM and autonomous navigation) with deep learning-based human action recognition to enable **human-aware robot behavior in real time**.

For mapping and localization, the system uses **Google Cartographer** via the `turtlebot3_cartographer` package, enabling robust SLAM in unknown environments. Autonomous navigation is handled using the **Nav2 framework**, where the global planner is based on **Theta\*** and the local controller uses the **DWB (Dynamic Window Approach)** algorithm for real-time obstacle avoidance and motion control.

On the perception side, a deep learning model based on **YOLOv8 (binary classification)** is integrated to detect human presence and classify behavior into two categories:
- Violent action
- Non-violent action

This enables a higher level of environmental understanding and intelligent decision-making.

---

##  Repository Structure

This repository is organized into multiple ROS 2 packages:

- **`sar_bot`**  
  Core simulation environment in Gazebo, including a demo URDF robot for testing SLAM and navigation. It integrates SLAM Toolbox and Nav2 for simulation-based experiments.

- **`turtlebot3`**  
  Real robot functionality package, including SLAM, navigation, and system integration for deployment on the physical TurtleBot3 platform.

- **`tb3_yolo_vision`**  
  Vision and AI module responsible for running the YOLOv8 model using camera topics for real-time human action recognition.

---

##  System Overview

The system is designed as a modular architecture combining:

- SLAM-based environment mapping  
- Autonomous navigation and path planning  
- Deep learning-based human action recognition  
- ROS 2-based communication between perception and control modules  

---

##  Ongoing Development

Additional components are currently under development, including:

- Foxglove-based visualization interface  
- Dedicated camera workspace (`camera_ws`) for enhanced perception pipeline integration  

---

##  Objective

The main goal of this project is to develop a **human-aware autonomous mobile robot** capable of navigating complex environments while understanding human behavior.  

This makes it suitable for applications such as:
- Surveillance systems  
- Safety monitoring  
- Intelligent assistance robotics  
