# Shopping with Face and Object Recognition

This project is a graduation project that demonstrates an AI-powered shopping system based on face recognition and object recognition technologies.  
The system is designed to simulate a cashier-less shopping experience similar to modern smart retail solutions.

## Project Overview

The main goal of this project is to identify customers using face recognition, detect the products they purchase using object recognition, and automatically manage payment transactions through a local database.

The system works in a closed environment and focuses on accuracy, performance, and modular software design.

## Key Features

- Face recognition–based customer identification
- New customer registration with facial data
- Object recognition for detecting purchased products
- Automatic price deduction from customer balance
- Local SQLite database for customer and product data
- Desktop application interface
- Privacy-oriented design (no personal images stored in repository)

## Technologies Used

- Python
- OpenCV
- face_recognition
- TensorFlow
- SQLite
- PyQt5
- COCO Dataset (for object recognition)
- Visual Studio Code

## System Architecture

1. The system captures video input from a camera.
2. Detected faces are matched with registered customers.
3. If the customer is new, a registration interface is displayed.
4. Objects held by the customer are detected using a trained model.
5. Detected products are matched with a price table.
6. The total amount is deducted from the customer’s balance.
7. All transactions are stored in a local database.

## Motivation

This project was developed to gain hands-on experience in:
- Computer vision
- Artificial intelligence
- Real-time image processing
- Database-driven desktop applications

It also aims to demonstrate how AI technologies can be integrated into real-world retail scenarios.

## Privacy and Security

- Personal face images are not included in the repository.
- All sensitive data is handled locally.
- The repository contains only source code and configuration files.

## Future Improvements

- Improving object recognition accuracy
- Supporting multiple products simultaneously
- Enhancing UI/UX design
- Optimizing performance for real-time usage
- Extending database and reporting features

## Author

Doruktan Karakurt  
Computer Engineering  
Graduation Project
