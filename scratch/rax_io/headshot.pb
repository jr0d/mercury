---
- name: Headshot
  hosts: all
  user: root
  gather_facts: no

  tasks:
    - name: install kexec-tools
      package: name=kexec-tools state=present
      environment:
        http_proxy: http://10.192.0.44:3128
        HTTPS_PROXY: http://10.192.0.44:3128

    - name: Get kernel
      get_url: url=http://10.192.0.44:9997/srv/images/preconfig/vmlinuz-3.18.9-RAX-aufs dest=/tmp/
    
    - name: Get initrd
      get_url: url=http://10.192.0.44:9997/srv/images/preconfig/initrd-3.18.9-RAX-aufs dest=/tmp/

    - name: HEADSHOT
      shell: kexec --type=bzImage --initrd=/tmp/initrd-3.18.9-RAX-aufs --append="ramdisk_size=750000 BOOTIF={{ snet_mac_address }} KCLIENTROOTFS=http://10.192.0.44/press/yolo/mercury-yolo7-kir.squashfs env=mercury console=tty0 biosdevname=0 debug" /tmp/vmlinuz-3.18.9-RAX-aufs  
      ignore_errors: True

