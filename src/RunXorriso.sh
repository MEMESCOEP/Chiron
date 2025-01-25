#!/bin/bash
### Chiron XORRISO SCRIPT ###
# By MEMESCOEP
# Last updated 01-14-25
# Running these commands in a bash script instead of in python seems to work infinitely better


cd $1/BuildFiles/Distro/image
sudo xorriso -as mkisofs -iso-level 3 -full-iso9660-filenames -J -J -joliet-long -volid "Chiron" -output "$1/$2" -eltorito-boot isolinux/bios.img -no-emul-boot -boot-load-size 4 -boot-info-table --eltorito-catalog boot.catalog --grub2-boot-info --grub2-mbr $1/BuildFiles/Distro/chroot/usr/lib/grub/i386-pc/boot_hybrid.img -partition_offset 16 --mbr-force-bootable -eltorito-alt-boot -no-emul-boot -e $1/BuildFiles/Distro/image/isolinux/efiboot.img -append_partition 2 28732ac11ff8d211ba4b00a0c93ec93b $1/BuildFiles/Distro/image/isolinux/efiboot.img -appended_part_as_gpt -iso_mbr_part_type a2a0d0ebe5b9334487c068b6b72699c7 -m "$1/BuildFiles/Distro/image/isolinux/efiboot.img" -m "$1/BuildFiles/Distro/image/isolinux/bios.img" -e '--interval:appended_partition_2:::' -exclude $1/BuildFiles/Distro/image/isolinux -graft-points "/EFI/boot/bootx64.efi=$1/BuildFiles/Distro/image/isolinux/bootx64.efi" "/EFI/boot/mmx64.efi=$1/BuildFiles/Distro/image/isolinux/mmx64.efi" "/EFI/boot/grubx64.efi=$1/BuildFiles/Distro/image/isolinux/grubx64.efi" "/EFI/ubuntu/grub.cfg=$1/BuildFiles/Distro/image/isolinux/grub.cfg" "/isolinux/bios.img=$1/BuildFiles/Distro/image/isolinux/bios.img" "/isolinux/efiboot.img=$1/BuildFiles/Distro/image/isolinux/efiboot.img" "."
