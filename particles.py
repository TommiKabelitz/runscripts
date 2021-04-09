#todo
#charge conjugation form
#mass?
#other properties?



def AntiParticle(arg):

    def Bar(particle):
        if particle[-3:] == 'bar':
            return particle[:-3]
        else:
            return particle + 'bar'

        
    in_type = type(arg)
    if in_type is str:
        return Bar(arg)
        
    elif in_type is list:
        for i,particle in enumerate(arg):
            input[i] = Bar(particle)
                
    elif in_type is dict:
        particle_list = arg['struct']
        for i,particle in enumerate(particle_list):
            arg['struct'][i] = Bar(particle)

    else:
        raise TypeError


        
#Partially neutral
def ddnl():

    props['struct'] = ['d','d','nl']
    
def ddnh():

    props['struct'] = ['d','d','nh']

def nlnld():

    props['struct'] = ['nl','nl','d']

def nhnhd():

    props['struct'] = ['nh','nh','d']

#"Real" Baryons
def proton():

    props['struct'] = ['u','u','d']

def neutron():

    props['struct'] = ['d','d','u']

def sigma_p():

    props['struct'] = ['u','u','s']

#"Real" Mesons
def pi_p():

    props['struct'] = ['u','dbar']

def pi_m():

    props['struct'] = ['d','ubar']
