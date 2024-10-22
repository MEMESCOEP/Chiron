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
| UEFI      | 🚧        |

<br/>

### CPU
| Process   | Minimum CPU speed + model  | Recommended CPU speed + model  |
| --------- | -------------------------- | ------------------------------ |
| Booting   | 🔍                         | 🔍                              |
| Terminal  | 🔍                         | 🔍                              |
| X11 (GUI) | 🔍                         | 🔍                              |

<br/>

### RAM
| Process   | Minimum RAM | Recommended RAM  |
| --------- | ----------- | ---------------- |
| Booting   | 768MB       | 1024MB (1GB)     |
| Terminal  | 64MB        | 128MB            |
| X11 (GUI) | 256MB       | 384MB            |

<br/>

### Graphics & Video
| Graphics processor / Video standard     | Supported (terminal) | Supported (X11 / GUI)                       |
| --------------------------------------- | -------------------- | ------------------------------------------- |
| AMD                                     | 🔍                   | 🔍                                           |
| ATI                                     | ✅ (No UEFI support) | ✅ (No UEFI support)                         |
| Bochs VBE / VGA Adapter                 | ✅                   | 🚧 (Terribly slow on some devices)           |
| Cirrus                                  | ✅                   | 🛠️ (Fatal server errors, AddScreen failures) |
| Nvidia (Official driver)                | ⛔ (Not open source) | ⛔ (Not open source)                         |
| Nvidia (Nouveau)                        | 🔍                   | 🔍                                           |
| Qemu STD                                | ✅                   | ✅                                           |
| QXL VGA                                 | ✅                   | 🚧 (Mouse cursor disappears)                 |
| QXL                                     | 🛠️ (Boot failures)   | 🛠️ (Boot failures)                           |
| SVGA                                    | ✅                   | ✅                                           |
| VMWare SVGA                             | ✅                   | ✅                                           |
| Virtio VGA                              | ✅                   | 🚧 (Mouse cursor disappears)                 |
| Virtio PCI                              | 🛠️ (Boot failures)   | 🛠️ (Boot failures)                           |
| VboxSVGA                                | ✅                   | ✅                                           |
| VboxVGA                                 | ✅                   | ✅                                           |
| VMSVGA (Virtualbox port of VMWare SVGA) | ✅                   | ✅                                           |
| VESA                                    | ✅                   | ✅                                           |
| VGA 16 Color                            | ✅                   | ✅                                           |
