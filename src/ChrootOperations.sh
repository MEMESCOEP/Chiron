#!/bin/bash
### Chiron CHROOT OPERATIONS SCRIPT ###
# By MEMESCOEP
# Last updated 1-05-2025
# Running these commands in a bash script instead of in python seems to work infinitely better


## VARIABLES ##
APT_INST_PACKAGES=()
APT_REM_PACKAGES=()
APT_REPOSITORIES=()
FLATPAK_PACKAGES=()
WGET_FILES=()
CHROOT_DIR="$1"
EXIT_CODE=0


## MAIN CODE ##
echo "Sorting APT packages, WGET files, and <other>..."
shift
while [[ $# -gt 1 ]]; do
    case "$1" in
        --APTInst)
            shift
            while [[ $# -gt 0 && ! "$1" =~ -- ]]; do
                APT_INST_PACKAGES+=("$1")
                shift
            done
            ;;
        --APTRem)
            shift
            while [[ $# -gt 0 && ! "$1" =~ -- ]]; do
                APT_REM_PACKAGES+=("$1")
                shift
            done
            ;;
         --WGET)
            shift
            while [[ $# -gt 0 && ! "$1" =~ -- ]]; do
                WGET_FILES+=("$1")
                shift
            done
            ;;
         --APTRepo)
            shift
            while [[ $# -gt 0 && ! "$1" =~ -- ]]; do
                APT_REPOSITORIES+=("$1")
                shift
            done
            ;;
        --FlatpakInst)
            shift
            while [[ $# -gt 0 && ! "$1" =~ -- ]]; do
                FLATPAK_PACKAGES+=("$1")
                shift
            done
            ;;
         *)
            echo "Unknown option: $1"
            ;;
    esac
done

echo "Flatpak packages to install: ${FLATPAK_PACKAGES[@]}"
echo "APT repositories to add: ${APT_REPOSITORIES[@]}"
echo "APT packages to install: ${APT_INST_PACKAGES[@]}"
echo "APT packages to remove: ${APT_REM_PACKAGES[@]}"
echo "WGET files: ${WGET_FILES[@]}"

echo "Mounting /dev & /run in chroot \"$CHROOT_DIR\"..."
sudo mount --bind /dev "$CHROOT_DIR/dev"
sudo mount --bind /run "$CHROOT_DIR/run"

echo
echo "Entering chroot \"$CHROOT_DIR\"..."
cat << EOFCH | sudo chroot $CHROOT_DIR

echo
echo "Disabling chroot prompt..."
export PS1=""

echo
echo "Mounting devices..."
mount none -t proc /proc
mount none -t sysfs /sys
mount none -t devpts /dev/pts

echo
echo "Exporting variables & hostname..."
export HOME=/root
export LC_ALL=C
echo "chiron" > /etc/hostname
hostnamectl set-hostname chiron
mkdir /Utilities
mkdir -p /image/{casper,isolinux,install}

cat <<EOF > /etc/hosts
127.0.0.1   localhost
127.0.0.1   chiron
::1      localhost ip6-localhost ip6-loopback
ff02::1     ip6-allnodes
ff02::2     ip6-allrouters
EOF

echo
echo "Changing default live session username..."
usermod -l chiron ubuntu
groupmod -n chiron ubuntu
usermod -d /home/chiron -m chiron
#sed -i 's/ubuntu/chiron/g' /etc/passwd

echo
echo "Configuring APT sources list..."
cat <<EOF > /etc/apt/sources.list
deb http://us.archive.ubuntu.com/ubuntu/ noble main restricted universe multiverse
deb-src http://us.archive.ubuntu.com/ubuntu/ noble main restricted universe multiverse

deb http://us.archive.ubuntu.com/ubuntu/ noble-security main restricted universe multiverse
deb-src http://us.archive.ubuntu.com/ubuntu/ noble-security main restricted universe multiverse

deb http://us.archive.ubuntu.com/ubuntu/ noble-updates main restricted universe multiverse
deb-src http://us.archive.ubuntu.com/ubuntu/ noble-updates main restricted universe multiverse
EOF

echo
echo "Updating and installing system packages..."
apt-get update
apt-get install -y libterm-readline-gnu-perl systemd-sysv

echo
echo "Configuring machine ID and diverting..."
dbus-uuidgen > /etc/machine-id
ln -fs /etc/machine-id /var/lib/dbus/machine-id
dpkg-divert --local --rename --add /sbin/initctl
ln -s /bin/true /sbin/initctl

echo
echo "Adding APT repositories..."
add-apt-repository -y ${APT_REPOSITORIES[@]}
apt-get update

echo
echo "Upgrading and installing packages..."
export DEBIAN_FRONTEND=noninteractive
apt-get -y upgrade
apt-get install -y ${APT_INST_PACKAGES[@]}
flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
flatpak install --assumeyes --verbose flathub ${FLATPAK_PACKAGES[@]}

mkdir -p /home/chiron/StressDisk
wget -O StressDisk.tar.gz https://github.com/ncw/stressdisk/releases/download/v1.0.13/stressdisk_linux_x86_64.tar.gz
wget https://phoronix-test-suite.com/releases/repo/pts.debian/files/phoronix-test-suite_10.8.3_all.deb
tar -xvzf StressDisk.tar.gz -C /home/chiron/StressDisk

apt-get install -y --no-install-recommends linux-generic
yes | dpkg -i phoronix*.deb
apt-get install -y -f
yes | dpkg -i phoronix*.deb

echo
echo "Removing extra & unused packages..."
apt-get remove -y ${APT_REM_PACKAGES[@]}

#echo
#echo "Installing firefox..."
#wget -O firefox.tar.bz2 https://download.mozilla.org/?product=firefox-latest&os=linux64&lang=en-US
#tar -xjf firefox.tar.bz2

apt-get autoremove -y

echo
echo "Removing downloaded files..."
rm StressDisk.tar.gz
rm firefox.tar.bz2
rm phoronix*.deb

echo
echo "Configuring locales..."
update-locale "LANG=en_US.UTF-8"
locale-gen --purge "en_US.UTF-8"
dpkg-reconfigure --frontend noninteractive locales

echo
echo "Creating network manager configuration..."
cat <<EOF > /etc/NetworkManager/NetworkManager.conf
[main]
rc-manager=none
plugins=ifupdown,keyfile
dns=systemd-resolved

[ifupdown]
managed=true
EOF

echo
echo "Reconfiguring network manager..."
dpkg-reconfigure network-manager

#sed -i 's/ubuntu/chiron/g' /etc/casper.conf
chown -R nobody:nogroup /home/chiron/.config/xfce4/

echo
echo "Creating image..."
cp /boot/vmlinuz-**-**-generic /image/casper/vmlinuz
cp /boot/initrd.img-**-**-generic /image/casper/initrd
cp /ConfigFiles/grub.cfg /image/isolinux
wget https://memtest.org/download/v7.00/mt86plus_7.00.binaries.zip -O /image/install/memtest86.zip
unzip -p /image/install/memtest86.zip memtest64.bin > /image/install/memtest86+.bin
unzip -p /image/install/memtest86.zip memtest64.efi > /image/install/memtest86+.efi
rm -f /image/install/memtest86.zip
touch /image/ubuntu

echo
echo "Creating package manifest..."
dpkg-query -W --showformat='${Package} ${Version}\n' | tee /image/casper/filesystem.manifest
cp -v /image/casper/filesystem.manifest image/casper/filesystem.manifest-desktop
sed -i '/ubiquity/d' /image/casper/filesystem.manifest-desktop
sed -i '/casper/d' /image/casper/filesystem.manifest-desktop
sed -i '/discover/d' /image/casper/filesystem.manifest-desktop
sed -i '/laptop-detect/d' /image/casper/filesystem.manifest-desktop
sed -i '/os-prober/d' /image/casper/filesystem.manifest-desktop

echo
echo "Creating disk defines..."
cat <<EOF > /image/README.diskdefines
#define DISKNAME  Chiron
#define TYPE  binary
#define TYPEbinary  1
#define ARCH  amd64
#define ARCHamd64  1
#define DISKNUM  1
#define DISKNUM1  1
#define TOTALNUM  0
#define TOTALNUM0  1
EOF

echo
echo "Copying EFI loaders..."
cd /image
cp /usr/lib/shim/shimx64.efi.signed.previous isolinux/bootx64.efi
cp /usr/lib/shim/mmx64.efi isolinux/mmx64.efi
cp /usr/lib/grub/x86_64-efi-signed/grubx64.efi.signed isolinux/grubx64.efi

echo
echo "Creating FAT16 UEFI boot image..."
(
   cd isolinux && \
   dd if=/dev/zero of=efiboot.img bs=1M count=10 && \
   mkfs.vfat -F 16 efiboot.img && \
   LC_CTYPE=C mmd -i efiboot.img efi efi/ubuntu efi/boot && \
   LC_CTYPE=C mcopy -i efiboot.img ./bootx64.efi ::efi/boot/bootx64.efi && \
   LC_CTYPE=C mcopy -i efiboot.img ./mmx64.efi ::efi/boot/mmx64.efi && \
   LC_CTYPE=C mcopy -i efiboot.img ./grubx64.efi ::efi/boot/grubx64.efi && \
   LC_CTYPE=C mcopy -i efiboot.img ./grub.cfg ::efi/ubuntu/grub.cfg
)

echo
echo "Creating grub BIOS image..."
grub-mkstandalone \
   --format=i386-pc \
   --output=isolinux/core.img \
   --install-modules="linux16 linux normal iso9660 biosdisk memdisk search tar ls halt reboot" \
   --modules="linux16 linux normal iso9660 biosdisk search halt reboot" \
   --locales="" \
   --fonts="" \
   "boot/grub/grub.cfg=isolinux/grub.cfg"

echo
echo "Combining grub BIOS image with a cdboot image..."
cat /usr/lib/grub/i386-pc/cdboot.img isolinux/core.img > isolinux/bios.img
/bin/bash -c "(find . -type f -print0 | xargs -0 md5sum | grep -v -e 'isolinux' > md5sum.txt)"

echo
echo "Enabling systemd services..."
systemctl enable AutostartNetworking.service

echo
echo "Rebuilding font cache..."
fc-cache -f -v

echo
echo "Cleaning up..."
truncate -s 0 /etc/machine-id
rm /sbin/initctl
dpkg-divert --rename --remove /sbin/initctl
apt-get clean
rm -rf /tmp/* ~/.bash_history
umount /proc
umount /sys
umount /dev/pts
export HISTSIZE=0

echo
echo "Chroot operations finished."
exit $EXIT_CODE
EOFCH
