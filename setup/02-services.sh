#!/bin/bash
set -e

echo "[+] Phase 1.4 — Camera service setup"

if [ "$EUID" -ne 0 ]; then
  echo "Run as root"
  exit 1
fi


APP_SRC=../app/*
APP_DEST=/opt/camera/

CONFIG_SRC=../config/camera.conf
CONFIG_DEST=/etc/camera/camera.conf

SERVICE_SRC=../config/camera.service
SERVICE_DEST=/etc/systemd/system/camera.service

# create application directory
mkdir -p /opt/camera
mkdir -p /etc/camera

# copy application files over
cp -rf ../app/* /opt/camera/
chmod +x /opt/camera/*
echo "[+] Camera app files installed"

# copy config config
cp -rf "$CONFIG_SRC" "$CONFIG_DEST"
echo "[+] Camera config installed"

# create systemd service
cp -rf "$SERVICE_SRC" "$SERVICE_DEST"
echo "[+] systemd service created"

# enable service
systemctl stop camera.service
systemctl daemon-reexec
systemctl daemon-reload
systemctl enable camera.service
systemctl start camera.service

echo "[+] Camera service enabled"
echo "[+] Phase 1.4 complete — reboot to activate"
