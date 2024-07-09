# Miru2

## About the Project

## Build of Materials

* NVIDIA Jetson Orin Nano 8Gb [Developer kit]
* CS2230 M.2 NVMe SSD 500GB
* Logitech BRIO 4k Ultra HD Webcam

## How to setup Jetson Orin Nano for MiruV2

### References

Before reading this part, go over each one of this references by yourself. It will be such a time saver!

[1] [Nvidia Jetson Orin Nano Unboxing and SSD Flash Install With SDK Manager](https://youtu.be/FX2exKW_20E)

### Install SDK manager

To get started, ensure that you have a main-computer that is running Ubuntu 20.04 (Not on a virtual machine). This is crucial because JetPack 5.1.3 has been tested to work optimally with Ubuntu 20.04, and this version also supports Python 3.8, which Miru2 is developed on. The Jetson Nano will be flashed with the main computer's Ubuntu version, making it essential to use Ubuntu 20.04. Next, [install the NVIDIA SDK Manager](https://developer.nvidia.com/sdk-manager) on the main-computer. This tool will be used to download and install the required JetPack version(s) onto the Jetson Orin Nano. To use the SDK Manager, you need to log in with your developer account. If you don't have one, [creating a developer account is straightforward.](https://developer.nvidia.com/login)

**[TODO: IMAGE main computer-jetson orin nano]**

**[TODO: IMAGE SDK manager UI]**

### Mount NVMe

NVMe (Non-Volatile Mmemory) can be considered as a solid state memory unit which is the replacement technology for older hard-drives. Simply mount NVMe to the device.

### Start Jetson in Force Recovery Mode 

There are so called button headers on the side of the device which should not be confused with 40-pin extansion headers. One of the button header is called Force Recovery pin. This should be connected to the ground so that jetson can be boot up in force recovery mode and be flashed by the SDK manager. The steps are simply;

1. **Ensure that the jetson-device is powered off and unplugged.**
2. Disconnect all unnecessary cables and USB adapters from the device.
3. Use a female-to-female jumper wire to connect the Force Recovery pin to the Ground pin on the button headers.
4. Connect the Jetson device to the main computer using a USB cable that supports data transfer.
5. Open the NVIDIA SDK Manager on the main computer and keep it at Step 1.
6. Plug in the power cable and the Jetson device should automatically turn-on (i.e. the green LED should illuminate).
7. The SDK Manager should automatically detect the Jetson device. If multiple Jetson Orin Nano 8GB devices are listed, select the correct developer kit version.
8. Proceed with the flashing process, which will be explained in detail in the upcoming section.

**[TODO: IMAGE button headers- force recovery]**

### Flashing
