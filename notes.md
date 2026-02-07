# Table of Contents

1. [Introduction](#introduction)
2. [Hardware](#hardware)
3. [Software](#software)
4. [Installation](#installation)
5. [Artifacts](#artifacts)


# Introduction
This repository holds code for a custom camera application. 

# Hardware
Below is a list of hardware components used for this project

- Raspberrypi
- SPI TFT
- Camera module

# Software
- Raspberrypi OS Lite


# Installation


# Artifacts
Below is a list of files created after running the install script

- /etc/systemd/system/camera.service - Camera service for linux
- /



# How it works

## 00-base.sh
upgrades dependencies
disables unused services

## 01-boot.sh

https://raspi.muth.org/framebuffer.html

> A device tree overlay tells Linux “this SPI screen exists and uses this driver,” and that driver creates `/dev/fb1`, which Linux writes pixels to and the driver sends them to the TFT over SPI.

It also adds some extra settings to /boot/firmware/config.txt to tell to load an overlay that enables the driver for the SPI.

[What is config.txt?](https://www.raspberrypi.com/documentation/computers/config_txt.html#dtoverlay)

## 02-services.sh


Creates the camera service. this camera service will run a python script in a daemon. The script is responsible for all application logic for the camera - from taking pictures, to displaying images.

It creates 3 artifacts, a config file, the service file, the app files


/setup/02-services.sh
Creates a service that runs a python script located at /opt/camera/camera_app.py

The service will be a daemon that accepts frames to draw to the screen

Creates the service at /etc/systemd/system/camera.service

The service will run after camera and framebuffer is available

Will restart on failure and on boot

You can check the status of the service with `systemctl status camera.service`

You can check the logs here `journalctl -u camera.service -b`




# Extra

## tft35a-overlay.dtb

you can view the contents at tft35a-overlay.dts

1. modifies the existing SPI controller on the Pi
2. disables generic spidev devices
3. registers two real SPI devices instead - ILI9486 TFT LCD panel and ADS7846 touchscreen conteroller
4. describes GPIO wiring
5. tells linux which kernel drivers to bind
6. results in a frambuffer device (/dev/fbX) and input device (/dev/input/eventX)

This is a Device Tree Overlay (DTO), not a full device tree

### Fragment 0 – Disable default spidev nodes
[What's spidev?](https://linuxvox.com/blog/linux-spidev/)

```
fragment@0 {
    target = <0xdeadbeef>;

    __overlay__ {
        status = "okay";

        spidev@0 { status = "disabled"; };
        spidev@1 { status = "disabled"; };
    };
};
```
What’s going on

target = <0xdeadbeef> → placeholder

later resolved to SPI controller (spi0)

Raspberry Pi normally exposes:

- /dev/spidev0.0

- /dev/spidev0.1

Why disable them?

Because:

spidev is generic

Your TFT needs a real kernel driver, not userspace SPI access

`Linux allows either spidev OR a real driver, not both`

So this frees SPI chip selects for real devices.

### Fragment 1 - GPIO ping configuration (pinctrl)
```
tft35a_pins {
    brcm,pins = <0x11 0x19 0x18>;
    brcm,function = <0x00 0x00 0x00>;
};
```
Translated:
| Hex  | GPIO   | Purpose            |
| ---- | ------ | ------------------ |
| 0x11 | GPIO17 | Touch IRQ          |
| 0x19 | GPIO25 | Reset              |
| 0x18 | GPIO24 | D/C (data/command) |

brcm,function = 0 → GPIO input/output mode

This block is later referenced by the TFT device

This is pure hardware wiring description.

### Fragment 2 – The actual SPI devices

This is the most important fragment.
```
#address-cells = <1>;
#size-cells = <0>;
```

This tells Linux:

- children are SPI devices

- addressed by chip select (reg = <0> or <1>)


TFT LCD device (ILI9486)
```
tft35a@0 {
    compatible = "ilitek,ili9486";
    reg = <0x00>;
```
Meaning

SPI device on CS0

Kernel looks up a driver that matches:
compatible = "ilitek,ili9486"
That driver is in fbtft (or similar framebuffer driver)

If the driver loads successfully → framebuffer appears.



init = < ... >

This is huge but critical.

It’s a power-on initialization script encoded as integers.

Pattern:

0x1XXXXXXX → command
0x2XXXXXXX → delay


Touchscreen device (ADS7846)
tft35a-ts@1 {
    compatible = "ti,ads7846";
    reg = <0x01>;

Touch GPIO + interrupt
interrupt-parent = <&gpio>;
interrupts = <17 2>;
pendown-gpio = <&gpio 17 1>;


GPIO17 used as:

pen-down detect

interrupt source

Driver registers an input device

Result:

/dev/input/eventX



Overrides – dtoverlay=tft35a:rotate=90
__overrides__ {
    rotate = <...>;
    fps = <...>;
    speed = <...>;
}


This lets you do:

dtoverlay=tft35a,rotate=90,fps=30

Fixups – resolving 0xdeadbeef
__fixups__ {
    spi0 = "/fragment@0:target:0";
    gpio = "/fragment@1:target:0";
}


What Linux does at boot (step-by-step)

Bootloader loads overlay

Overlay patches live device tree

SPI controller now has:

ILI9486 @ CS0

ADS7846 @ CS1

Kernel matches compatible strings

Drivers load:

framebuffer driver → /dev/fb1

input driver → /dev/input/eventX

fbcon may attach automatically

Userspace can draw pixels directly


# DONE BUT NOT ADDED TO NOTES


sudo apt install python3-pil
sudo apt-get install python3-rpi.gpio