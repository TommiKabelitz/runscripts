def runvals():
    kappa_vals = [13770]
    kds = [-1,0,1]
    shifts = ['x00t00','x16t8']
    run_prefix = 'a'
    return locals()


def submit_jobs(kappa_vals,kd,shifts,run_prefix,**kwargs):
    
    for kappa in kapp_vals:
        for kd in kds:
            for shift in shifts:
                print('kappa: ',str(kappa))
                print('run_prefix: ',run_prefix)
                print('kd: ',str(kd))
                print('shift: ',shift)

                
    



