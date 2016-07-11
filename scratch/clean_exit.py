import subprocess
import time

WORK = './work.sh'


def main():
    p = subprocess.Popen([WORK])
    print(p.pid)
    print(p.poll())

    while p.poll() is None:
        time.sleep(1)

    print(p.returncode)

if __name__ == '__main__':
    main()
