---
- name: Resistance is futile
  hosts: all
  user: root
  gather_facts: no

  tasks:
    - name: Join cluster
      command: kubeadm join --token=53e2b6.360b4e342710e135 10.192.0.42:6443
    
