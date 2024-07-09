# Miru2

## About the Project

***TODO: project video**

## How to run Miru2 on an already configured Jetson-Orin nano

## Build of Materials

* **NVIDIA Jetson Orin Nano 8Gb [Developer kit].**
* **CS2230 M.2 NVMe SSD 500GB.**
* **Logitech BRIO 4k Ultra HD Webcam.**
* **USB Mouse and Keyboard.**
* **A display**
* Arduino Uno & 5V controlled relay (Optional - Required for turnstile control feature).
* *Waveshare Orin Nano/NX Metal Case (Optional).*
* *HDMI-to-DISPLAY PORT adaptor (Optional).*

## How to setup Jetson Orin Nano for Miru2

***TODO: video explaining all the steps in english**

### References

Before reading this part, go over each one of this references by yourself. It will be such a time saver!

[1] [Nvidia Jetson Orin Nano Unboxing and SSD Flash Install With SDK Manager](https://youtu.be/FX2exKW_20E)

[2] [Install Jetson Software with SDK Manager](https://docs.nvidia.com/sdk-manager/install-with-sdkm-jetson/index.html)

[3] [Use These! Jetson Docker Containers Tutorial](https://youtu.be/HlH3QkS1F5Y)

[4] [Github- Jetson Containers](https://github.com/dusty-nv/jetson-containers/tree/master)

[5] [JETSON ORIN CASE A-Assembly Tutorial, Aluminum Alloy Case For Jetson Orin, With Camera Holder](https://youtu.be/-imhL0oETSQ)

### 1) Install SDK manager

To get started, ensure that you have a main-computer that is running Ubuntu 20.04 (Not on a virtual machine). This is crucial because JetPack 5.1.3 has been tested to work optimally with Ubuntu 20.04, and this version of ubuntu also supports Python 3.8, which Miru2 is developed on. The Jetson Nano will be flashed with the main computer's Ubuntu version, making it essential to use Ubuntu 20.04. Next, [install the NVIDIA SDK Manager](https://developer.nvidia.com/sdk-manager) on the main-computer. This tool will be used to download and install the required JetPack version(s) onto the Jetson Orin Nano. To use the SDK Manager, you need to log in with your developer account. If you don't have one, [creating a developer account is straightforward.](https://developer.nvidia.com/login)

**[TODO: IMAGE main computer-jetson orin nano]**

**[TODO: IMAGE SDK manager UI]**

### 2) Mount NVMe

Please refer to [reference [1].](https://youtu.be/FX2exKW_20E)

NVMe (Non-Volatile Memory) can be considered as a solid state memory unit which is the replacement technology for older hard-drives. Simply mount NVMe to the jetson-device.

### 3) Start Jetson in Force Recovery Mode

Please refer to [reference [1].](https://youtu.be/FX2exKW_20E)

On the side of the jetson-device, there are ***button headers*** that should not be confused with the ***40-pin expansion headers***. One of these button headers is called the **Force Recovery pin.** To boot the Jetson into force recovery mode and allow it to be flashed by the SDK Manager, you need to connect the Force Recovery pin to the ground. The steps to follow are as simple as:

1. **Ensure that the jetson-device is powered off and unplugged.**
2. Disconnect all unnecessary cables and USB adapters from the device.
3. Use a female-to-female jumper wire to connect the Force Recovery pin to the Ground pin on the button headers.
4. Connect the Jetson device to the main computer using a USB cable that supports data transfer.
5. Open the NVIDIA SDK Manager on the main computer and keep it at Step 1.
6. Plug in the power cable and the Jetson device should automatically turn-on (i.e. the green LED should illuminate).
7. The SDK Manager should automatically detect the Jetson device. If multiple Jetson Orin Nano 8GB devices are listed, select the correct developer kit version.
8. You can remove female-to-female jumper wire carefully since it is not longer needed. Do not remove USB cable!
9. Proceed with the flashing process, which will be explained in detail in the upcoming section.

**[TODO: IMAGE button headers- force recovery connection]**

### 4) Flashing with SDK manager

*For official documentation, please refer to [reference [1]](https://youtu.be/FX2exKW_20E) and [reference [2].](https://docs.nvidia.com/sdk-manager/install-with-sdkm-jetson/index.html)*

Please note that these configurations might change slightly with updates to the SDK Manager. However, similar options should be available regardless of any changes. Flashing consists of four steps listed in the SDK Manager. The configuration for each step is as follows:

#### SDK-manager Step 1:

PRODUCT CATEGORY                                 :  Jetson

HARDWARE CONFUGURATION                  :  Host Machine

TARGET HARDWARE                                   :  Jetson Orin Nano [8GB developer kit version]

TARGET OPERATING SYSTEM                     :  Linux (JetPack 5.1.3)

ADDITIONAL SDKS                                     :  (Honestly I always keep it as it is)

#### SDK-manager Step 2:

During this step, the required components will be downloaded. If you have already performed this step before, the components will be checked, and any new versions will be downloaded if necessary. Accept the terms and conditions, and continue with the next step.

#### SDK-manager Step 3:

The SDK manager will ask you to enter your ***sudo password***. After you enter the password, the Jetson device will be flashed shortly. This process can take between half an hour to an hour. You might see error messages indicating that it is taking longer than expected. If this occurs, simply continue with the flashing process. Be patient throughout the flashing process. During a part of the process, the manager will ask you some configuration choices for your jetson-device. You can continue with

1-Choose **Automatic Setup**

2- Already satisfied

3- Already satisfied

4- Choose an **username** and **password** for your jetson-device's ubuntu.

5- Choose **NVMe** option.

#### SDK-manager Step 4:

This step is just the summary. The flashing process is complete and your Jetson device is now a standalone computer and no longer needs the main computer. You can safely remove the USB cable.

### 5) Jetson-device first things to do.

#### Display and log-in

After successfully completing this step, you can take a deep breath and relax. Your Jetson device is now ready to use!

1. Unplug the power cable.
2. Connect the Jetson device to the display using either a DisplayPort or an HDMI-to-DisplayPort adapter.
3. Ensure that a keyboard is connected to the Jetson device.
4. Plug in the power cable. Jetson device should automatically turn-on (i.e. the green LED should illuminate).
5. Press the "Enter" key repeatedly until you see the Ubuntu login screen.
6. Log in to your Jetson device using the password you set during step 3 of the flashing process.

#### Connect to internet

This step is required since we will be installing packages. Additionally, once the internet connection is established, the device will update its date and time using NTP (Network Time Protocol).

#### Get updates

Open terminal and run the following;

```
sudo apt-get update && sudo apt-get upgrade

```

#### Turn-off battery-saving

Since Miru2 is designed to operate on a 24/7 basis, change the sleep option to "Never."

**[TODO: explain how this setting is turned to never]**

### Install Docker Image

please refer to [reference [3]](https://youtu.be/HlH3QkS1F5Y) and [reference [4].](https://github.com/dusty-nv/jetson-containers/tree/master)

#### 1-a) Use Miru2-prebuilt image:

**[TODO: upload Miru2-prebuilt image to docker hub and explaint how to install it.]**

#### 1-b) From ground up:

Step **1-a** should be sufficient. After completing step **1-b**, you will simply end up with the same image as in step **1-a**. This part is explained in case any problems occur during step **1-a.**

##### Verify docker

Open terminal and run the following to check if docker is working;

```
sudo docker info
```

##### Change Default Docker Runtime

Open terminal and run the following code to open deamon.json file in gedit (i.e text editor).

```
sudo gedit /etc/docker/daemon.json
```

Change the content of the file with the following json and save.

```
{
    "runtimes": {
        "nvidia": {
            "path": "nvidia-container-runtime",
            "runtimeArgs": []
        }
    },

    "default-runtime": "nvidia"
}
```

Restart the docker

```
sudo systemctl restart docker
```

Then check whether changes are applied.

```
$ sudo docker info | grep 'Default Runtime'
Default Runtime: nvidia
```

##### Download L4T: 35.4.1 Docker image


## Details of the Miru2 software implementation

TODO: explain how code works
