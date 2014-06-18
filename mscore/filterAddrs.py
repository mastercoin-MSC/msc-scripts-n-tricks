a=open('./addrs.txt').readlines()
for line in a:
    linefilt=line.replace(' ','').split('=>')
    addr=linefilt[0]
    bal=linefilt[1].split('[')[0]
    res=linefilt[1:][0].split('[')[1].split('=')[1].split(']')[0] 
    print addr+bal+res 
    if bal[0] != '+':
        print 'killed'
        exit()
