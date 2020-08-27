# PlatformIO for Mediatek MT6261
**Arduino** & Baremetal ( **no GSM** ) development platform version 1.0.0

The project is based on reverse engineering

**MT6261 & MT250x**
* SoC ARM7EJ-S @ 260 MHz
* RAM: 4M
* FLASH: 4M
* GPIO [56]
* ADC
* PWM
* UART [3]
* SPI
* I2C
* RTC
* LCD
* Bluetooth
* SD Card
* Audio 32 tones ( Mediatek did not want to help for more )

( note: baremetal C/CPP builder is not ready yet )

![mt6261](https://raw.githubusercontent.com/Wiz-IO/LIB/master/images/mt6261.jpg) 

## Install Platform
* PlatformIO Home > Platforms > Advanced Installation
* paste https://github.com/Wiz-IO/wizio-mtk

![linkit](https://raw.githubusercontent.com/Wiz-IO/LIB/master/images/linkit.jpg) 

## [Bootloaders](https://github.com/Wiz-IO/framework-wizio-mtk/tree/master/bootloaders)
* for Linkit ONE use FirmwareUpdater.exe
* for Quectel M66 use QFlash_Vx.x.exe
* Restore - just reflash with original firmwares

## INI
```ini
[env:mtk-m66]
platform = wizio-mtk
board = mtk-m66
framework = arduino
upload_port = COM13
monitor_port = COM13
monitor_speed = 115200
;build_flags = -DLINKIT
```

## Tested with
* [LinkIt ONE](https://www.seeedstudio.com/LinkIt-ONE-p-2017.html)
* [Quectel M66](https://www.quectel.com/product/m66.htm)
* **Can work with ALL GSM modules based of MT6261 MT250x**

![m66](https://raw.githubusercontent.com/Wiz-IO/LIB/master/images/m66.jpg) 

## Links
* [MediatekInfo DZ09](https://github.com/MediatekInfo/DZ09)
* [OsmocomBB Fernvale](https://osmocom.org/projects/baseband/wiki/Fernvale)

![dzvero](https://raw.githubusercontent.com/Wiz-IO/LIB/master/images/dzvero.jpg) 
