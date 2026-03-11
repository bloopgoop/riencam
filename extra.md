# DIY Camera (RienCam)

A **minimal, purpose-built digital camera appliance** built on Raspberry Pi hardware.

The goal of this project is to create a **fast, reliable, offline still camera** that behaves like a dedicated device rather than a general-purpose computer.

The system boots directly into a camera service and allows the user to capture images using a physical shutter button. The camera saves JPEG images to disk and displays the result on a small SPI TFT display.

This project intentionally avoids desktop environments, window managers, and complex UI frameworks in order to keep the system deterministic and lightweight.


# Design Philosophy

This camera follows several core principles:

* **Appliance behavior** — power on and the camera is immediately ready.
* **Single responsibility** — one process owns the hardware.
* **Offline first** — no network dependency.
* **Deterministic operation** — minimal background services.
* **Hard power tolerant** — safe against sudden power loss.
* **Minimal UI** — framebuffer rendering instead of GUI stacks.

The system behaves like this:

```
Power On
   ↓
Boot Linux
   ↓
camera.service starts
   ↓
Display shows READY
   ↓
Press shutter
   ↓
Capture JPEG
   ↓
Save to disk
   ↓
Display photo
```


# Software Architecture

The system runs **Raspberry Pi OS Lite** with **no desktop environment**.

There is **one systemd service** that controls the entire camera system.

The application is written in **Python** and communicates directly with:

* the **framebuffer**
* the **camera capture command**
* the **filesystem**


# Boot Process

When the Raspberry Pi boots:

1. Linux loads the TFT overlay.
2. The SPI display registers as `/dev/fb1`.
3. `camera.service` starts automatically.
4. The Python camera application launches.

The service is configured to automatically restart if it crashes.


# Camera Application

The entry point is:

```
app/app.py
```

Startup behavior:

1. Wait for framebuffer device `/dev/fb1`
2. Initialize the camera class
3. Begin capture loop



# Image Capture

Captures are performed using:

```
rpicam-still
```

Command executed:

```
rpicam-still -n -o .capture.tmp
```

Capture workflow:

1. Capture to temporary file
2. Flush file to disk
3. Atomic rename
4. Sync directory metadata
5. Display captured image

Atomic writes ensure the system remains safe against sudden power loss. 

---

# Framebuffer Rendering

The TFT display is controlled directly through the Linux framebuffer:

```
/dev/fb1
```

The framebuffer driver:

```
app/framebuffer.py
```

This module provides:

* clear screen
* draw rectangles
* draw images
* RGB565 conversion

Example:

```python
fb.clear(0x0000)
fb.draw_rect(x, y, w, h, color)
```

Images are converted to **RGB565** and written pixel-by-pixel.

---

# Text Rendering

There is no font library.

Instead the system uses a **tiny built-in bitmap font** defined in:

```
app/font.py
```

Each character is an **8×6 pixel bitmap**.

Example:

```
  ##  
 #  # 
#    #
######
#    #
#    #
```

Text rendering draws rectangles for each pixel.

---

# Configuration

The camera configuration file is:

```
/etc/camera/camera.conf
```

Example:

```
FRAMEBUFFER=/dev/fb1
PHOTO_DIR=/data/photos

SHUTTER_GPIO=17
DEBOUNCE_MS=200
```

This allows hardware configuration without changing code. 


# Systemd Service

The camera runs as a systemd service.

Location:

```
/etc/systemd/system/camera.service
```

Key properties:

```
Restart=always
RestartSec=1
```

If the application crashes, it automatically restarts.


# Display Driver

The SPI TFT display is enabled using a custom device tree overlay:

```
overlays/tft35a-overlay.dtb
```

Configured in:

```
/boot/firmware/config.txt
```

Example entry:

```
dtoverlay=tft35a:rotate=90
```

This registers the display as framebuffer device `/dev/fb1`.


# Setup Scripts

The `setup/` directory contains reproducible installation scripts.

These scripts configure the system in phases.

---

## 00-base.sh

Base system setup:

* installs packages
* disables unnecessary services
* prepares minimal environment

---

## 01-boot.sh

Boot configuration:

* installs TFT overlay
* enables SPI
* configures display rotation

---

## 02-services.sh

Service installation:

* installs application to `/opt/camera`
* installs configuration to `/etc/camera`
* installs systemd service
* enables auto-start

---

# Photo Storage

Images are stored in:

```
/data/photos
```

Filenames use timestamp format:

```
YYYY-MM-DD_HH-MM-SS.jpg
```

Example:

```
2026-02-14_12-03-08.jpg
```

---



# Development Goals

The camera should remain:

* **simple**
* **fast**
* **predictable**
* **maintainable**

This means avoiding:

* desktop stacks
* heavy UI frameworks
* unnecessary dependencies

