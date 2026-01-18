# OS hardening, packages

#!/bin/bash
set -e

echo "[+] Phase 1.2 — Base system setup"

# Ensure running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

# Update system
# COMMENTED OUT FOR NOW TO INCREASE SPEED OF DEV
# apt update
# apt -y upgrade

# Essential packages only
apt install -y \
  git \
  vim \
  fbset \
  evtest \
  i2c-tools \
  gpiod

# Disable services we definitely do not want
systemctl disable --now \
  hciuart.service \
  triggerhappy.service \
  avahi-daemon.service

# ---- OPTIONAL HARDENING (disabled for now) ----
# Wi-Fi disable (leave commented for now)
# systemctl disable --now wpa_supplicant.service

# Audio disable (leave commented for now)
# systemctl disable --now alsa-state.service

# Reduce boot noise
systemctl mask getty@tty1.service

echo "[+] Base system setup complete"

