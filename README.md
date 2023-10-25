 ## Preview
![ezgif com-optimize](https://github.com/ali-rzb/Heart-Border-Detector/assets/63366614/6e84384d-9f70-4800-86bb-e13e7ec52238)

# Cardiac Motion Tracking in Medical Imaging
## Problem Statement

This project addresses the critical challenge of tracking cardiac motion in medical imaging during cardiac interventions. While performing heart procedures, issues such as heart wall perforation can occur, often indicated by a decrease in heart motion. Timely detection of this motion reduction is crucial for the patient's safety and successful outcomes. This project aims to develop an algorithm for the automated or semi-automated tracking of a specific region of the heart wall over time in a series of medical imaging frames.

## Data

The project uses a dataset consisting of four short films, each capturing different individuals undergoing cardiac interventions. Each film contains 23 to 28 frames, with a resolution of 512x512 pixels. These films serve as both the training and testing data. A sample frame can be seen below : 

![5](https://github.com/ali-rzb/Heart-Border-Detector/assets/63366614/565da269-0627-4cb7-a6eb-c7cb10f4977d)

## Solution
In this project, we employed the first two films, each comprising 48 frames, to train a neural network. The "labeling-init.py" file displays these 48 frames sequentially, allowing the user to define boundaries on them. Subsequently, these frames are saved as 16x16 tiles with two classes, "Non-Border" and "Border" (C0 and C1), using another program.

## Training:
In the "train_2D.ipynb" file, we balance the number of border and non-border tiles and create a neural network with specific configurations:
![0](https://github.com/ali-rzb/Heart-Border-Detector/assets/63366614/62523d17-787c-42ec-8536-d8c5b1849efd)

Through trial and error, we achieved an accuracy of approximately 95% by adjusting the number of layers, batch size, and epochs. We save the model in a file with an "h5" extension.

## User Interface
We designed a graphical user interface using the Tkinter library. After selecting the relevant film file, it first partitions the first frame into tiles and feeds them into the neural model obtained in the previous step. The neural network then makes predictions and provides output as zeros and ones. We use morphological operations to separate distinct shapes, consider those with insufficient area as noise, and filter them.
