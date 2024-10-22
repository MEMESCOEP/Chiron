# System Requirements

> [!NOTE]
> This document contains information about Chiron's system requirements. Reference the following list if you're ever unsure what a particular icon means.<br/><br/>
> ✅ - Working, and supported<br/>
> 🔍 - Untested, tests pending<br/>
> 🚧 - Tested and partially working, but not yet supported<br/>
> 🛠️ - Tested and not working; not yet supported<br/>
> ⛔ - Unsupported

<br/>

### Firmware
| Firmware  | Supported |
| --------- | --------- |
| BIOS      | ✅        |
| UEFI      | 🛠️        |

<br/>

### CPU
| Process   | Minimum CPU speed + model  | Recommended CPU speed + model  |
| --------- | -------------------------- | ------------------------------ |
| Booting   | 🔍                         | 🔍                              |
| Terminal  | 🔍                         | 🔍                              |
| X11 (GUI) | 🔍                         | 🔍                              |

<br/>

### RAM
| Process   | Minimum RAM  | Recommended RAM  |
| --------- | ------------ | ---------------- |
| Booting   | 1024MB (1GB) | 2048MB (2GB)     |
| Terminal  | 64MB         | 128MB            |
| X11 (GUI) | 256MB        | 384MB            |

<br/>

### Graphics & Video
| Graphics processor / Video standard     | Supported (terminal) | Supported (X11 / GUI)                         |
| --------------------------------------- | -------------------- | --------------------------------------------- |
| AMD                                     | 🔍                   | 🔍                                             |
| ATI                                     | 🔍                   | 🔍                                             |
| Bochs VBE / VGA Adapter                 | ✅                   | 🚧 (So slow you can see the background update. |
| Cirrus                                  | ✅                   | ✅                                             |
| Nvidia (Official driver)                | ⛔ (Not open source) | ⛔ (Not open source)                           |
| Nvidia (Nouveau)                        | 🔍                   | 🔍                                             |
| Qemu STD                                | ✅                   | ✅                                             |
| QXL VGA                                 | 🔍                   | 🔍                                             |
| QXL                                     | ✅                   | ✅                                             |
| SVGA                                    | ✅                   | ✅                                             |
| VMWare SVGA                             | ✅                   | ✅                                             |
| Virtio VGA                              | ✅                   | ✅                                             |
| Virtio PCI                              | 🔍                   | 🔍                                             |
| VboxSVGA                                | ✅                   | ✅                                             |
| VboxVGA                                 | ✅                   | ✅                                             |
| VMSVGA (Virtualbox port of VMWare SVGA) | ✅                   | ✅                                             |
| VESA                                    | ✅                   | ✅                                             |
| VGA 16 Color                            | ✅                   | ✅                                             |
