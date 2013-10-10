from fabric.api import run
def pullSlave():
    run("sudo -s; cd /mnt/nozomiServer; git pull origin slave; kill `ps aux | grep startApp | awk '{print $2}'`; screen -d -m sh startApp.sh")
