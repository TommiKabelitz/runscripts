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



########################################Baryons        

def proton():

    props = {}

    props['lorentz_indices'] = []
    props['gamma_matrices'] = []
    props['levi_civita_indices'] = ['a;b;c']
    props['cfun_terms'] = ['1.0 * [u^{a} (C\gamma_{5}) d^{b}] (I) u^{c}']
    return props

def protonbar():

    props = {}

    props['gamma_matrices'] = []
    props['levi_civita_indices'] = ['ap;bp;cp']
    props['cfun_terms'] = ['-1.0 * Au^{cp} (I) [Ad^{bp} (C\gamma_{5}) Au^{ap}]']
    return props


def sigmap():

    props = {}

    props['lorentz_indices'] = []
    props['gamma_matrices'] = []
    props['levi_civita_indices'] = ['a;b;c']
    props['cfun_terms'] = ['1.0 * [u^{a} (C\gamma_{5}) s^{b}] (I) u^{c}']
    return props

def sigmapbar():

    props = {}

    props['gamma_matrices'] = []
    props['levi_civita_indices'] = ['ap;bp;cp']
    props['cfun_terms'] = ['-1.0 * Au^{cp} (I) [As^{bp} (C\gamma_{5}) Au^{ap}]']
    return props


def sigmam():

    props = {}

    props['lorentz_indices'] = []
    props['gamma_matrices'] = []
    props['levi_civita_indices'] = ['a;b;c']
    props['cfun_terms'] = ['1.0 * [d^{a} (C\gamma_{5}) s^{b}] (I) d^{c}']
    return props

def sigmambar():

    props = {}

    props['gamma_matrices'] = []
    props['levi_civita_indices'] = ['ap;bp;cp']
    props['cfun_terms'] = ['-1.0 * Ad^{cp} (I) [As^{bp} (C\gamma_{5}) Ad^{ap}]']
    return props


def neutron():

    props = {}

    props['lorentz_indices'] = []
    props['gamma_matrices'] = []
    props['levi_civita_indices'] = ['a;b;c']
    props['cfun_terms'] = ['1.0 * [u^{a} (C\gamma_{5}) d^{b}] (I) d^{c}']
    return props

def neutronbar():

    props = {}

    props['gamma_matrices'] = []
    props['levi_civita_indices'] = ['ap;bp;cp']
    props['cfun_terms'] = ['-1.0 * Ad^{cp} (I) [Ad^{bp} (C\gamma_{5}) Au^{ap}]']
    return props


def cascade0():

    props = {}

    props['lorentz_indices'] = []
    props['gamma_matrices'] = []
    props['levi_civita_indices'] = ['a;b;c']
    props['cfun_terms'] = ['1.0 * [u^{a} (C\gamma_{5}) s^{b}] (I) s^{c}']
    return props

def cascade0bar():

    props = {}

    props['gamma_matrices'] = []
    props['levi_civita_indices'] = ['ap;bp;cp']
    props['cfun_terms'] = ['-1.0 * As^{cp} (I) [As^{bp} (C\gamma_{5}) Au^{ap}]']
    return props


def cascadem():

    props = {}

    props['lorentz_indices'] = []
    props['gamma_matrices'] = []
    props['levi_civita_indices'] = ['a;b;c']
    props['cfun_terms'] = ['1.0 * [d^{a} (C\gamma_{5}) s^{b}] (I) s^{c}']
    return props

def cascadembar():

    props = {}

    props['gamma_matrices'] = []
    props['levi_civita_indices'] = ['ap;bp;cp']
    props['cfun_terms'] = ['-1.0 * As^{cp} (I) [As^{bp} (C\gamma_{5}) Ad^{ap}]']
    return props


#####Mixing baryons
def sigma0():

    props = {}

    props['lorentz_indices'] = []
    props['gamma_matrices'] = []
    props['levi_civita_indices'] = ['a;b;c']
    props['cfun_terms'] = ['1.0/sqrt(2.0) * [u^{a} (C\gamma_{5}) s^{b}] (I) d^{c}',
                           '1.0/sqrt(2.0) * [d^{a} (C\gamma_{5}) s^{b}] (I) u^{c}']
    return props

def sigma0bar():

    props = {}

    props['gamma_matrices'] = []
    props['levi_civita_indices'] = ['ap;bp;cp']
    props['cfun_terms'] = ['-1.0/sqrt(2.0) * Ad^{cp} (I) [As^{bp} (C\gamma_{5}) Au^{ap} ]',
                           '-1.0/sqrt(2.0) * Au^{cp} (I) [As^{bp} (C\gamma_{5}) Ad^{ap} ]']
    return props


def lambda0():

    props = {}

    props['lorentz_indices'] = []
    props['gamma_matrices'] = []
    props['levi_civita_indices'] = ['a;b;c']
    props['cfun_terms'] = ['2.0/sqrt(6.0) * [u^{a} (C\gamma_{5}) d^{b} ] (I) s^{c}',
                           '1.0/sqrt(6.0) * [u^{a} (C\gamma_{5}) s^{b} ] (I) d^{c}',
                           '-1.0/sqrt(6.0) * [d^{a} (C\gamma_{5}) s^{b} ] (I) u^{c}']
    return props

def lambda0bar():

    props = {}

    props['gamma_matrices'] = []
    props['levi_civita_indices'] = ['ap;bp;cp']
    props['cfun_terms'] = ['-2.0/sqrt(6.0) * As^{cp} (I) [Ad^{bp} (C\gamma_{5}) Au^{ap} ]',
                           '-1.0/sqrt(6.0) * Ad^{cp} (I) [As^{bp} (C\gamma_{5}) Au^{ap} ]',
                           '1.0/sqrt(6.0) * Au^{cp} (I) [As^{bp} (C\gamma_{5}) Ad^{ap} ]']
    return props




######################Mesons

def pip():

    props = {}

    props['lorentz_indices'] = []
    props['gamma_matrices'] = []
    props['levi_civita_indices'] = []
    props['cfun_terms'] = ['1.0 * [Ad^{e} (\gamma_{5}) u^{e}]']
    return props

def pipbar():

    props = {}

    props['gamma_matrices'] = []
    props['levi_civita_indices'] = []
    props['cfun_terms'] = ['-1.0 * [Au^{ep} (\gamma_{5}) d^{ep}']
    return props


def QuarkCharge(quark,*args,**kwargs):
    
    if quark == 'u':
        return 2
    elif quark in ['d','s']:
        return -1
    elif 'n' in quark:
        return 0
    else:
        raise NotImplementedError(f'{quark} is not implemented')


def HadronicCharge(kd,particle,structure,*args,**kwargs):
    
    counts = []
    for quark in ['u','d','s']:
        counts.append(globals()[particle]()['cfun_terms'][0].count(quark))
        
    charge = 0
    for quark,count in zip(structure,counts):
        charge += QuarkCharge(quark)*count
        
    if 'bar' in particle:
        return -1*charge*kd
    else:
        return charge*kd

