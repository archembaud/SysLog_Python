# SysLog_Python

## Dr. Matthew Smith, Swinburne University of Technology

A simple system monitor / logging tool using PSUtil with Nvidia-smi parsing.

## Introduction

A simple python script which uses the PSUtil module and Nvidia-smi to check the system temperatures, CPU loadings and GPU temperatures. While running,
it shows CPU usage, maximum temperatures and GPU temperatures. It's not a complicated script - but it doesn't need much to work and ought to work out of the box.

## Usage

After cloning it, just call it with Python (python system.py <enter>). It will loop indefinitely until CTRL+C is pressed, and log the resulting system usage data
to a file together with time stamp information. 

## Requirements
The code uses the PSUtil module in python. Another section of the code opens a pipe to the system and parses output produced by nvidia-smi - so if this is not installed,
you're gonna have a bad day. Just comment this section out if you're not interested GPU temperature loadings.
