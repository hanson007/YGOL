#!/bin/bash
# celery runing script

celerybin=/home/huangxiaoxue/package/python/bin/celery
celery_pid_file=/home/huangxiaoxue/application/project/YinguOnline/log/run/celery.pid
celery_log_file=/home/huangxiaoxue/application/project/YinguOnline/log/celery.log


celery_start(){
   $celerybin  multi start  -A YinguOnline worker --pidfile=$celery_pid_file --logfile='$celery_log_file' -l info
}


celery_stop(){
   $celerybin  multi stopwait  -A YinguOnline worker --pidfile=$celery_pid_file --logfile='$celery_log_file' -l info
}



test_status(){
    if test -e $celery_pid_file
    then
        echo 'celery is runing'
    else
        echo 'celery stoped'
    fi

}

case $1 in
start)
    celery_start
    ;;
stop)
    celery_stop
    ;;
status)
    test_status
    ;;
  *)
    echo './celery.sh start | stop | status'
    ;;
esac


