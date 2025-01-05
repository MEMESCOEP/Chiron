# Chiron
Chiron is a lightweight GUI Linux distribution for x86_64 devices. It's built for system rescue, diagnostics, and stress testing.

<br/>

> [!NOTE]  
> If you're using Ventoy, you may need to load the ISO image in [Memdisk](https://www.ventoy.net/en/doc_memdisk.html) or [Grub2](https://www.ventoy.net/en/doc_grub2boot.html) mode. You should only need to do this if you get a kernel panic related to VFS mounting or a non-working init file.

Chiron can be booted from removable media such as USB storage devices and CDs, just write the ISO image to your selected media. Using tools like `ventoy` can be useful, as they let you boot multiple ISOs from the same USB storage device.

---

<br/>

### Getting Started
See the [Getting Started](https://github.com/MEMESCOEP/Chiron/blob/main/Docs/GettingStarted.md) guide to begin.

---

<br/>

### Included software
> [!NOTE]  
> More tools will be added as development progresses.

A full list of installed packages can be found [here](https://github.com/MEMESCOEP/Chiron/blob/main/Docs/Packages.md).

<details>
<summary>Disk utilities</summary>

* Photorec
* Ext4Magic
* Testdisk
* Cfdisk
* Fdisk
* GParted
* Parted
* Bonnie++
* Rsync
* Thunar
* Clonezilla
* Sysfsutils
* Gnome Disks
* SmartMonTools
* DDRescue
</details>
<details>
<summary>Stress testing</summary>

* StressDisk
* Stress
* Stress-ng
* S-Tui
</details>
<details>
<summary>Diagnostics</summary>

* Memtest86
* Htop
* IFtop
* Sysdiag
* Sysbench
* Smartctl
* HwInfo
</details>
<details>
<summary>Networking</summary>

* Speedtest-cli
* NetworkManager
* FileZilla
* Firefox
</details>
<details>
<summary>Scripting</summary>

* Python 3.12
</details>
<details>
<summary>Other utilities</summary>

* Nano
</details>

---

<br/>
