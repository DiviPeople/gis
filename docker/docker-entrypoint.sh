#!/bin/sh

cd linux-5.4.0 || exit
ARCH=arm make bcm2835_defconfig
ARCH=arm make menuconfig
