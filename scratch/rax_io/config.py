TARGET_CABINET = 'g13-27'
MERCURY = 'http://mercury.iad3.kir.kickstart.rackspace.com:9005'
TARGET_QUERY = {'interfaces.lldp.switch_name': {'$regex': '{}.*'.format(TARGET_CABINET)}}
CENT7_KEXEC = {
    'kernel': 'vmlinuz-3.10.0-327.10.1.el7.x86_64',
    'initrd': 'initramfs-3.10.0-327.10.1.el7.x86_64.img',
    'options': [
        'root=/dev/sda2',
        'ro',
        'crashkernel=auto',
        'rhgb',
        'biosdevname=1',
        'net.ifnames=0',
        'rdblacklist=bfa',
        'nomodeset'
    ]
}
KUBE_TOKEN = '53e2b6.360b4e342710e135'
KUBE_IP = '10.192.0.42'
KUBE_PORT = '6443'
