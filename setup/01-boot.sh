#!/bin/bash
set -e

echo "[+] Phase 1.3 — Boot & Display Configuration"

# Ensure root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

BOOT_CONFIG=/boot/firmware/config.txt
OVERLAY_SRC=../overlays/tft35a-overlay.dtb
OVERLAY_DEST=/boot/overlays/


# copy overlay
yes | cp -rf $OVERLAY_SRC $OVERLAY_DEST
yes | cp -rf $OVERLAY_SRC $OVERLAY_DEST/tft35a.dtbo
echo "[+] Overlay copied to /boot/overlays/"

# ensure SPI enabled
if ! grep -q "^dtparam=spi=on" "$BOOT_CONFIG"; then
  echo "dtparam=spi=on" >> "$BOOT_CONFIG"
  echo "[+] SPI enabled"
else
  echo "[*] SPI already enabled"
fi

# enable TFT overlay
if ! grep -q "^dtoverlay=tft35a:rotate=90" "$BOOT_CONFIG"; then
  echo "dtoverlay=tft35a:rotate=90" >> "$BOOT_CONFIG"
  echo "[+] TFT overlay enabled"
else
  echo "[*] TFT overlay already enabled"
fi

# disable HDMI for power saving
# if ! grep -q "^hdmi_blanking=2" "$BOOT_CONFIG"; then
#   echo "hdmi_blanking=2" >> "$BOOT_CONFIG"
#   echo "[*] HDMI disabled"
# fi

echo "[+] Phase 1.3 complete — reboot required for changes"
