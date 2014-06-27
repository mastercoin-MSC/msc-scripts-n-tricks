a=open('./consensus/addrs.txt').readlines()
for line in a:
    linefilt=line.replace(' ','').split('=>')
    addr=linefilt[0]
    bal=linefilt[1].split('[')[0]
    sores=linefilt[1:][0].split('[')[1].split('=')[1].split(',')[0]
    acres=linefilt[1:][0].split('[')[1].split('=')[-1].split(']')[0]
    print addr+bal+sores+acres
    if bal[0] != '+':
        print 'killed'
        exit()
