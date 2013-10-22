#coding:utf8
from fabric.api import run, env
env.user_ssh_config = True
def host_type():
    run('uname -s')
#'ec2-54-227-39-135.compute-1.amazonaws.com', 
env.hosts = ['ec2-54-227-39-135.compute-1.amazonaws.com', 'ec2-54-237-95-109.compute-1.amazonaws.com' ]
 
env.user = 'ubuntu'
env.key_filename = '~/.ssh/liyong2.pem'
def mergeSlave():
    run('cd /mnt/nozomiServer; sudo git pull origin slave; ')
    #run("sudo kill `ps aux | grep startApp.sh | grep -v grep | awk '{print $2}'`")
    #重新启动 gunicorn 进程 重新加载服务器 代码 
    run("sudo kill -HUP `ps aux | grep gunicorn | grep -v grep | awk '{print $2}' `")
    
