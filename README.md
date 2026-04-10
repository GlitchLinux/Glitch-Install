# Glitch Installer v1.0

<img width="904" height="656" alt="image" src="https://github.com/user-attachments/assets/767f3350-d44d-42ad-810b-d7cc3c5cc69a" />

### Removed
- ❌ `efi-runtimes` (optional, not essential)

### Added (LUKS/Encryption Support)
- ✅ `cryptsetup` - Core LUKS encryption tool
- ✅ `cryptsetup-initramfs` - Cryptsetup hooks for initramfs
- ✅ `lvm2` - LVM support (for encrypted volume management)
- ✅ `dmsetup` - Device mapper tools

## Why These Are Required

The Glitch Installer script has extensive LUKS encryption support:

### LUKS Encryption (lines 866-901)
```python
def _setup_luks(self, cfg):
    # Formats partition with LUKS1 encryption
    cryptsetup luksFormat --type luks1 --batch-mode {data_part}
    # Opens encrypted partition
    cryptsetup luksOpen {data_part} {self.luks_mapper}
    # Formats as ext4 on encrypted volume
    mkfs.ext4 -F -L ROOT {self.luks_device}
```

### Crypttab Configuration (lines 1136-1162)
```python
# Writes to /etc/crypttab for automatic unlock
crypttab_entry = f"{self.luks_mapper} UUID={luks_uuid} none luks,discard,initramfs"
```

### Initramfs Integration (lines 1157-1170)
```bash
# Installs LUKS support into initramfs
apt-get install -y cryptsetup cryptsetup-initramfs

# Ensures cryptsetup is included in initramfs build
echo "CRYPTSETUP=y" >> /etc/cryptsetup-initramfs/conf-hook

# Adds kernel modules needed for decryption
echo "dm-crypt" >> /etc/initramfs-tools/modules
echo "dm-mod" >> /etc/initramfs-tools/modules
```

## Updated Dependency List

**Before:**
```
python3, python3-tk, util-linux, e2fsprogs, parted, grub-pc, 
dosfstools, mtools, efibootmgr, efi-runtimes
```

**After (Updated):**
```
python3, python3-tk, util-linux, e2fsprogs, parted, grub-pc, 
dosfstools, mtools, efibootmgr, cryptsetup, cryptsetup-initramfs, 
lvm2, dmsetup
```

## What Each Dependency Does

| Package | Purpose |
|---------|---------|
| `python3` | Python interpreter |
| `python3-tk` | GUI toolkit (Tkinter) |
| `util-linux` | System utilities (fdisk, etc.) |
| `e2fsprogs` | Ext4 filesystem tools |
| `parted` | Partition management |
| `grub-pc` | BIOS bootloader |
| `dosfstools` | FAT filesystem support |
| `mtools` | FAT utilities |
| `efibootmgr` | EFI bootloader management |
| **`cryptsetup`** | **LUKS encryption tool** |
| **`cryptsetup-initramfs`** | **LUKS boot support** |
| **`lvm2`** | **LVM volume management** |
| **`dmsetup`** | **Device mapper control** |

## Installation

The updated `.deb` now includes proper LUKS dependencies:

```bash
sudo dpkg -i glitchinstall-1.0.deb
sudo apt-get install -f  # Installs all dependencies automatically
```

## LUKS Features Now Fully Supported

✅ Optional LUKS encryption during installation  
✅ Automatic crypttab configuration  
✅ Initramfs integration for boot-time unlock  
✅ UUID-based mapping  
✅ Discard support for SSDs  
✅ LVM integration  

## Build Date

Updated: April 10, 2026 @ 06:02

---

**Status:** ✅ Ready for distribution
**Version:** glitchinstall-1.0-amd64.deb
