#13700
def one(kappa,run_prefix):
    if run_prefix == 'b':
        start = 2510
        ncon = 399
        return start, ncon
    else:
        print("Invalid (kappa,prefix) combination. Terminating")
        exit()

#13727
def two(kappa,run_prefix):
    if run_prefix == 'b':
        start = 1310
        ncon = 397
        return start, ncon
    else:
        print("Invalid (kappa,prefix) combination. Terminating")
        exit

#13754
def three(kappa,run_prefix):
    if run_prefix == 'a':
        start = 2510
        ncon = 200
        return start, ncon
    elif run_prefix == 'b':
        start = 2510
        ncon = 249
        return start, ncon
    else:
        print("Invalid (kappa,prefix) combination. Terminating")
        exit
#13770
def four(kappa,run_prefix):
    if run_prefix == 'a':
        start = 1880
        ncon = 400
        return start, ncon
    elif run_prefix == 'b':
        start = 1780
        ncon = 399
        return start, ncon
    else:
        print("Invalid (kappa,prefix) combination. Terminating")
        exit

#13781
def five(kappa,run_prefix):
        if run_prefix == 'gM':
            start = 1200
            ncon = 44
            return start, ncon
        elif run_prefix == 'hM':
            start = 1240
            ncon = 22
            return start, ncon
        elif run_prefix == 'iM':
            start = 870
            ncon = 44 
            return start, ncon
        elif run_prefix == 'jM':
            start = 260
            ncon = 44
            return start, ncon
        elif run_prefix == 'kM':
            start = 1090
            ncon = 43
            return start, ncon
        else:
            print("Invalid (kappa,prefix) combination. Terminating")
        exit


def configIDs(kappa,run_prefix):
    
    print('kappa: '+str(kappa))
    print('run prefix: '+run_prefix)

    switch = {
        13700:one,
        13727:two,
        13754:three,
        13770:four,
        13781:five
    }
    case = switch[kappa]
    start, ncon = case(run_prefix)
    
    return start,ncon
