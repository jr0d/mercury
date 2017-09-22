---
- name: Headshot
  hosts: all
  user: root

  tasks:
    - name: Get kernel
      get_url: url=http://10.192.0.44:9997/srv/images/preconfig/vmlinuz-3.18.9-RAX-aufs dest=/tmp/
    
    - name: Get initrd
      get_url: url=http://10.192.0.44:9997/srv/images/preconfig/initrd-3.18.9-RAX-aufs dest=/tmp/

    - name: HEADSHOT
      command: kexec --type=bzImage --initrd=/tmp/initrd-3.18.9-RAX-aufs --append="ramdisk_size=750000 KCLIENTROOTFS=http://10.192.0.44/press/yolo/mercury-yolo7-kir.squashfs env=kclient_legacy console=tty0 biosdevname=0 debug" /tmp/vmlinuz-3.18.9-RAX-aufs
      ignore_errors: True

