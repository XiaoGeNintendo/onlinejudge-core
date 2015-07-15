import os,sys,time,atexit,fcntl
from signal import SIGTERM

class Daemon(): 
    def __init__(self,pidfile,stdin='/dev/null',stdout='/dev/null',stderr='/dev/null'):
        self.stdin=stdin
        self.stdout=stdout
        self.stderr=stderr
        self.pidfile=pidfile
 
    def daemonize(self):
        try:
            pid=os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError,e:
            sys.stderr.write("fork first faild:%d (%s)\n" % (e.errno,e.strerror))
            sys.exit(1)
 
        os.chdir('./')
        os.setsid()
        os.umask(0)
 
        try:
            pid=os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError,e:
            sys.stderr.write("fork second faild:%d (%s)\n" % (e.errno,e.strerror))
            sys.exit(1)
 
 
        sys.stdout.flush()
        sys.stderr.flush()

        si=file(self.stdin,'r')
        so=file(self.stdout,'a+')
        se=file(self.stderr,'a+',0)
        os.dup2(si.fileno(),sys.stdin.fileno())
        os.dup2(so.fileno(),sys.stdout.fileno())
        os.dup2(se.fileno(),sys.stderr.fileno())
 
        atexit.register(self.delpid)
        pid=str(os.getpid())
        file(self.pidfile,'w+').write("%s\n" % pid)
 
    def delpid(self):
        os.remove(self.pidfile)
 
    def start(self):
        try:
            pf=open(self.pidfile,'r')
            pid=int(pf.read().strip())
            pf.close()
        except IOError:
            pid=None
 
        if pid:
            ms="pidfile %s already exist,daemon already running\n"
            sys.stderr.write(ms % self.pidfile)
            sys.exit(1)
 
        self.daemonize()
        self.run()
 
    def stop(self):
        try:
            pf=open(self.pidfile,'r')
            pid=int(pf.read().strip())
            pf.close()
        except IOError:
            pid=None
 
        if not pid:
            ms="pidfile %s does not exit,daemon not running\n"
            sys.stderr.write(ms % self.pidfile)
            return
 
        try:
            while True:
                os.kill(pid,SIGTERM)
                time.sleep(0.1)
                os.remove(self.pidfile)
        except OSError,err:
            err=str(err)
            if err.find('No sush process') > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
                else:
                    print str(err)
                    sys.exit(1)
 
    def restart(self):
        self.stop()
        self.start()

    def run(self):
        pass