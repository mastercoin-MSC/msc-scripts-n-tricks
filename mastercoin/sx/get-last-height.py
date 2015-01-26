import obelisk
from twisted.internet import reactor

def flh(err, height):
    print "HEIGHT", height
    print "ERR", err
    reactor.stop()

c = obelisk.ObeliskOfLightClient('tcp://x.x.x:9091')
print c
err=''
height=''
c.fetch_last_height(flh)
print err, height

reactor.run()

