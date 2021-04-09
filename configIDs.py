#13700
def One(kappa,run_prefix):
    if run_prefix == 'b':
        start = 2510
        ncon = 399
        return start, ncon
    else:
        print("Invalid (kappa,prefix) combination. Terminating")
        exit()

#13727
def Two(kappa,run_prefix):
    if run_prefix == 'b':
        start = 1310
        ncon = 397
        return start, ncon
    else:
        print("Invalid (kappa,prefix) combination. Terminating")
        exit

#13754
def Three(kappa,run_prefix):
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
def Four(kappa,run_prefix):
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
def Five(kappa,run_prefix):
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



def ConfigDetails(kappa,run_prefix):
    
    switch = {
        13700:One,
        13727:Two,
        13754:Three,
        13770:Four,
        13781:Five
    }
    case = switch[kappa]
    start, ncon = case(kappa,run_prefix)
    
    return start,ncon

def ConfigID(nth_con,run_prefix,start,**kwargs):

    if run_prefix in ['a','b']:
        gap = 10
    elif run_prefix in ['gM','hM','iM','jM','kM']:
        gap = 20
    else:
        print('abort')
        exit()

    ID = start + (nth_con-1)*gap
    return f'-{run_prefix}-00{ID}'
