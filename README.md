# Miru2

sudo apt-get install gstreamer1.0-tools gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly

## About the Project

***TODO: project video**

## History of the Project

## How to run Miru2 on an already configured Jetson-Orin nano

***TODO: video explaining all the steps in english**

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

[5] [NVIDIA - What is L4T?](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/l4t-base)

[] [JETSON ORIN CASE A-Assembly Tutorial, Aluminum Alloy Case For Jetson Orin, With Camera Holder](https://youtu.be/-imhL0oETSQ)

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

2- Should be already satisfied.

3- Should be already satisfied.

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

```
$ sudo apt-get update && sudo apt-get upgrade

```

#### Turn-off battery-saving

Since Miru2 is designed to operate on a 24/7 basis, change the sleep option to "Never."

**[TODO: explain how this setting is turned to never]**

### Install Docker Image

Please refer to [reference [3]](https://youtu.be/HlH3QkS1F5Y) , [reference [4]](https://github.com/dusty-nv/jetson-containers/tree/master) and [reference [5].](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/l4t-base)

#### 1-a) Use L4T:Miru2 image:

**[TODO: upload Miru2-prebuilt image to docker hub and explaint how to install it.]**

#### 1-b) Use L4T:r35.4.1 image:

Step **1-a** should be sufficient. After completing step **1-b**, you will simply end up with the same image as in step **1-a**. This part is explained in case any problems occur during step **1-a.**

##### Verify docker

Check if docker is working;

```
$ sudo docker info
```

##### Change Default Docker Runtime

Open deamon.json file in gedit (i.e text editor).

```
$ sudo gedit /etc/docker/daemon.json
```

Change the content of the file with the following and save.

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

Restart Docker

```
$ sudo systemctl restart docker
```

Then check whether the changes are applied.

```
$ sudo docker info | grep 'Default Runtime'
Default Runtime: nvidia
```

##### Download L4T: 35.4.1 Docker image

*"NVIDIA Linux4Tegra (L4T) package provides the bootloader, kernel, necessary firmwares, NVIDIA drivers for various accelerators present on Jetson modules, flashing utilities and a sample filesystem to be used on Jetson systems. The software packages contained in L4T provide the functionality necessary to run Linux on Jetson modules." [5]*

Pull [`dustynv/l4t-pytorch:r35.4.1`](https://hub.docker.com/r/dustynv/l4t-pytorch/tags) image;

```
$ sudo docker pull dustynv/l4t-pytorch:r35.4.1
```

The image is about 6GB. Which takes a while to download.

Check image is downloaded;

```
$ sudo docker image ls
```

##### Built Miru2 and commit (i.e. save) the final image

*Ensure that webcam and the miru-arduino is connected to the jetson-device.*

```
$ sudo xhost +
```

Run the [`dustynv/l4t-pytorch:r35.4.1`](https://hub.docker.com/r/dustynv/l4t-pytorch/tags) image;

```
$ sudo docker run --runtime nvidia --device /dev/video0:/dev/video0 -it --rm --network=host -e DISPLAY -e QT_X11_NO_MITSHM=1 dustynv/l4t-pytorch:r35.4.1
```

go to home directory

**TODO: add absolute path for the container commands to make it more error prone**

```
$[CONTAINER] cd home
```

Clone the Miru2 repository

```
$[CONTAINER] git clone https://github.com/erdemcanaz/Miru2.git
```

During cloning, you may encounter an EOF error, especially if your network connection is unstable. I have not specifically addressed this issue because one of the trials always succeeded without errors (typically within 5 to 10 attempts). I simply retried until a successful attempt. This error is expected, so if you encounter it, just keep trying until you succeed or you may search for the solution on the web. There are some *[SOLVED]* topics on that.

Go to miru directory.

```
$[CONTAINER] cd Miru2
```

Install Ultralytics without dependencies. This is necessary because cv2 is prebuilt in this container and somehow does not appear in the pip package manager. When installing Ultralytics with dependencies, cv2 (which is also a dependency) gets overwritten, leading to errors.

```
$[CONTAINER] python3.8 -m pip install ultralytics --no-deps
```

The Ultralytics dependencies, excluding cv2, are listed in the ***ultralytics_requirements.txt*** file. Simply install each package listed in that file.

```
$[CONTAINER] python3.8 -m pip install -r ultralytics_requirements.txt
```

Now we can test the setup if all the functionalities workign fine. There is a test script solely written for this purpose. It starts and checks different functionalities one by one and summarizes the succeded/failed functionalities. To start testing,

```
$[CONTAINER] python3.8 testing/test_all.py
```

| Test Name               | Test Purpose                                                                                                                                                                                                                                                                                                                          | Fails When                              |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------- |
| Python Version          | To verify that the Python script is running version 3.8, as Miru has been tested exclusively with this version.                                                                                                                                                                                                                       | If python version is not 3.8            |
| USB-PORT Test (Serial)  | To verify if the script is authorized to perform USB port-related tasks, it checks the number of available ports detected by the script. By default, this test assumes that an Arduino is connected to the Jetson device, so at least one port should be listed.                                                                      | If number of ports available is zero    |
| Show CV2 Frame          | To verify if the script can display an image as a CV2 frame, it ensures that the Docker container is run with the appropriate tags to interact with the display. This test also unintentionally checks the installation of CV2.**Please ensure that the image is displayed. The script will only fail if an exception occurs.** | If any exception occurs during the test |
| Webcam                  | To verify if the script can fetch data from the webcam and display it as a CV2 frame, this test assumes a webcam is connected to the Jetson device by default.**Please ensure that the video stream is displayed. The script will only fail if an exception occurs.**                                                           | If any exception occurs during the test |
| CUDA availability       | To verify if PyTorch is installed and CUDA is available for PyTorch.                                                                                                                                                                                                                                                                  | If CUDA is not available for pytorch    |
| Ultralytics YOLOv8 Pose | To verify if Ultralytics is installed and capable of detecting objects in a test image using the yolo8n-pose.pt model. The detection result should be displayed on the screen, highlighting the person and their joints in the test image.                                                                                            | If any exception occurs during the test |

## Details of the Miru2 software implementation

TODO: explain how code works
