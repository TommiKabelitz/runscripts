"""
Module of particle operators to be used.

Added particles should follow the same format as those already
present. Particles with multiple terms in their interpolating
field should have each term added as an item in a list.

There are also a couple of utility functions at the bottom
QuarkCharge, HadronicCharge

"""
########################################Baryons


# Currently implemented octet baryons with _1,_2 denoting
# which of the two possible interpolating fields is used.
# Particle charge is denoted by 0 (neutral), p (+1),
# m (-1).
# ie. sigmap is a sigma+, but + cannot be used
# in an object name.
# Would recommend deltapp for charge 2 particles such
# as the delta ++


def proton_1():

    props = {}

    props["lorentz_indices"] = []
    props["gell_mann_matrices"] = []
    props["levi_civita_indices"] = ["a;b;c"]
    props["interpolator_terms"] = ["1.0 * [u^{a} (C\gamma_{5}) d^{b}] (I) u^{c}"]

    return props


def proton_1bar():

    props = {}

    props["gell_mann_matrices"] = []
    props["levi_civita_indices"] = ["ap;bp;cp"]
    props["interpolator_terms"] = ["-1.0 * Au^{cp} (I) [Ad^{bp} (C\gamma_{5}) Au^{ap}]"]
    return props


def sigmap_1():

    props = {}

    props["lorentz_indices"] = []
    props["gell_mann_matrices"] = []
    props["levi_civita_indices"] = ["a;b;c"]
    props["interpolator_terms"] = ["1.0 * [u^{a} (C\gamma_{5}) s^{b}] (I) u^{c}"]
    return props


def sigmap_1bar():

    props = {}

    props["gell_mann_matrices"] = []
    props["levi_civita_indices"] = ["ap;bp;cp"]
    props["interpolator_terms"] = ["-1.0 * Au^{cp} (I) [As^{bp} (C\gamma_{5}) Au^{ap}]"]
    return props


def sigmam_1():

    props = {}

    props["lorentz_indices"] = []
    props["gell_mann_matrices"] = []
    props["levi_civita_indices"] = ["a;b;c"]
    props["interpolator_terms"] = ["1.0 * [d^{a} (C\gamma_{5}) s^{b}] (I) d^{c}"]
    return props


def sigmam_1bar():

    props = {}

    props["gell_mann_matrices"] = []
    props["levi_civita_indices"] = ["ap;bp;cp"]
    props["interpolator_terms"] = ["-1.0 * Ad^{cp} (I) [As^{bp} (C\gamma_{5}) Ad^{ap}]"]
    return props


def neutron_1():

    props = {}

    props["lorentz_indices"] = []
    props["gell_mann_matrices"] = []
    props["levi_civita_indices"] = ["a;b;c"]
    props["interpolator_terms"] = ["1.0 * [u^{a} (C\gamma_{5}) d^{b}] (I) d^{c}"]
    return props


def neutron_1bar():

    props = {}

    props["gell_mann_matrices"] = []
    props["levi_civita_indices"] = ["ap;bp;cp"]
    props["interpolator_terms"] = ["-1.0 * Ad^{cp} (I) [Ad^{bp} (C\gamma_{5}) Au^{ap}]"]
    return props


def cascade0_1():

    props = {}

    props["lorentz_indices"] = []
    props["gell_mann_matrices"] = []
    props["levi_civita_indices"] = ["a;b;c"]
    props["interpolator_terms"] = ["1.0 * [u^{a} (C\gamma_{5}) s^{b}] (I) s^{c}"]
    return props


def cascade0_1bar():

    props = {}

    props["gell_mann_matrices"] = []
    props["levi_civita_indices"] = ["ap;bp;cp"]
    props["interpolator_terms"] = ["-1.0 * As^{cp} (I) [As^{bp} (C\gamma_{5}) Au^{ap}]"]
    return props


def cascadem_1():

    props = {}

    props["lorentz_indices"] = []
    props["gell_mann_matrices"] = []
    props["levi_civita_indices"] = ["a;b;c"]
    props["interpolator_terms"] = ["1.0 * [d^{a} (C\gamma_{5}) s^{b}] (I) s^{c}"]
    return props


def cascadem_1bar():

    props = {}

    props["gell_mann_matrices"] = []
    props["levi_civita_indices"] = ["ap;bp;cp"]
    props["interpolator_terms"] = ["-1.0 * As^{cp} (I) [As^{bp} (C\gamma_{5}) Ad^{ap}]"]
    return props


def proton_2():

    props = {}

    props["lorentz_indices"] = []
    props["gell_mann_matrices"] = []
    props["levi_civita_indices"] = ["a;b;c"]
    props["interpolator_terms"] = ["1.0 * [u^{a} (C) d^{b}] (\gamma_{5}) u^{c}"]

    return props


def proton_2bar():

    props = {}

    props["gell_mann_matrices"] = []
    props["levi_civita_indices"] = ["ap;bp;cp"]
    props["interpolator_terms"] = ["-1.0 * Au^{cp} (\gamma_{5}) [Ad^{bp} (C) Au^{ap}]"]
    return props


def sigmap_2():

    props = {}

    props["lorentz_indices"] = []
    props["gell_mann_matrices"] = []
    props["levi_civita_indices"] = ["a;b;c"]
    props["interpolator_terms"] = ["1.0 * [u^{a} (C) s^{b}] (\gamma_{5}) u^{c}"]
    return props


def sigmap_2bar():

    props = {}

    props["gell_mann_matrices"] = []
    props["levi_civita_indices"] = ["ap;bp;cp"]
    props["interpolator_terms"] = ["-1.0 * Au^{cp} (\gamma_{5}) [As^{bp} (C) Au^{ap}]"]
    return props


def sigmam_2():

    props = {}

    props["lorentz_indices"] = []
    props["gell_mann_matrices"] = []
    props["levi_civita_indices"] = ["a;b;c"]
    props["interpolator_terms"] = ["1.0 * [d^{a} (C) s^{b}] (\gamma_{5}) d^{c}"]
    return props


def sigmam_2bar():

    props = {}

    props["gell_mann_matrices"] = []
    props["levi_civita_indices"] = ["ap;bp;cp"]
    props["interpolator_terms"] = ["-1.0 * Ad^{cp} (\gamma_{5}) [As^{bp} (C) Ad^{ap}]"]
    return props


def neutron_2():

    props = {}

    props["lorentz_indices"] = []
    props["gell_mann_matrices"] = []
    props["levi_civita_indices"] = ["a;b;c"]
    props["interpolator_terms"] = ["1.0 * [u^{a} (C) d^{b}] (\gamma_{5}) d^{c}"]
    return props


def neutron_2bar():

    props = {}

    props["gell_mann_matrices"] = []
    props["levi_civita_indices"] = ["ap;bp;cp"]
    props["interpolator_terms"] = ["-1.0 * Ad^{cp} (\gamma_{5}) [Au^{bp} (C) Ad^{ap}]"]
    return props


def cascade0_2():

    props = {}

    props["lorentz_indices"] = []
    props["gell_mann_matrices"] = []
    props["levi_civita_indices"] = ["a;b;c"]
    props["interpolator_terms"] = ["1.0 * [u^{a} (C) s^{b}] (\gamma_{5}) s^{c}"]
    return props


def cascade0_2bar():

    props = {}

    props["gell_mann_matrices"] = []
    props["levi_civita_indices"] = ["ap;bp;cp"]
    props["interpolator_terms"] = ["-1.0 * As^{cp} (\gamma_{5}) [Au^{bp} (C) As^{ap}]"]
    return props


def cascadem_2():

    props = {}

    props["lorentz_indices"] = []
    props["gell_mann_matrices"] = []
    props["levi_civita_indices"] = ["a;b;c"]
    props["interpolator_terms"] = ["1.0 * [d^{a} (C) s^{b}] (\gamma_{5}) s^{c}"]
    return props


def cascadem_2bar():

    props = {}

    props["gell_mann_matrices"] = []
    props["levi_civita_indices"] = ["ap;bp;cp"]
    props["interpolator_terms"] = ["-1.0 * As^{cp} (\gamma_{5}) [Ad^{bp} (C) As^{ap}]"]
    return props


#####Mixing baryons


def sigma0_1():

    props = {}

    props["lorentz_indices"] = []
    props["gell_mann_matrices"] = []
    props["levi_civita_indices"] = ["a;b;c"]
    props["interpolator_terms"] = [
        "1.0/sqrt(2.0) * [u^{a} (C\gamma_{5}) s^{b}] (I) d^{c}",
        "1.0/sqrt(2.0) * [d^{a} (C\gamma_{5}) s^{b}] (I) u^{c}",
    ]
    return props


def sigma0_1bar():

    props = {}

    props["gell_mann_matrices"] = []
    props["levi_civita_indices"] = ["ap;bp;cp"]
    props["interpolator_terms"] = [
        "-1.0/sqrt(2.0) * Ad^{cp} (I) [As^{bp} (C\gamma_{5}) Au^{ap} ]",
        "-1.0/sqrt(2.0) * Au^{cp} (I) [As^{bp} (C\gamma_{5}) Ad^{ap} ]",
    ]
    return props


def lambda0_1():

    props = {}

    props["lorentz_indices"] = []
    props["gell_mann_matrices"] = []
    props["levi_civita_indices"] = ["a;b;c"]
    props["interpolator_terms"] = [
        "2.0/sqrt(6.0) * [u^{a} (C\gamma_{5}) d^{b} ] (I) s^{c}",
        "1.0/sqrt(6.0) * [u^{a} (C\gamma_{5}) s^{b} ] (I) d^{c}",
        "-1.0/sqrt(6.0) * [d^{a} (C\gamma_{5}) s^{b} ] (I) u^{c}",
    ]
    return props


def lambda0_1bar():

    props = {}

    props["gell_mann_matrices"] = []
    props["levi_civita_indices"] = ["ap;bp;cp"]
    props["interpolator_terms"] = [
        "-2.0/sqrt(6.0) * As^{cp} (I) [Ad^{bp} (C\gamma_{5}) Au^{ap} ]",
        "-1.0/sqrt(6.0) * Ad^{cp} (I) [As^{bp} (C\gamma_{5}) Au^{ap} ]",
        "1.0/sqrt(6.0) * Au^{cp} (I) [As^{bp} (C\gamma_{5}) Ad^{ap} ]",
    ]
    return props


# DID THIS
def sigma0_2():

    props = {}

    props["lorentz_indices"] = []
    props["gell_mann_matrices"] = []
    props["levi_civita_indices"] = ["a;b;c"]
    props["interpolator_terms"] = [
        "1.0/sqrt(2.0) * [u^{a} (C) s^{b}] (\gamma_{5}) d^{c}",
        "1.0/sqrt(2.0) * [d^{a} (C) s^{b}] (\gamma_{5}) u^{c}",
    ]
    return props


def sigma0_2bar():

    props = {}

    props["gell_mann_matrices"] = []
    props["levi_civita_indices"] = ["ap;bp;cp"]
    props["interpolator_terms"] = [
        "-1.0/sqrt(2.0) * Ad^{cp} (\gamma_{5}) [As^{bp} (C) Au^{ap} ]",
        "-1.0/sqrt(2.0) * Au^{cp} (\gamma_{5}) [As^{bp} (C) Ad^{ap} ]",
    ]
    return props


def lambda0_2():

    props = {}

    props["lorentz_indices"] = []
    props["gell_mann_matrices"] = []
    props["levi_civita_indices"] = ["a;b;c"]
    props["interpolator_terms"] = [
        "2.0/sqrt(6.0) * [u^{a} (C) d^{b} ] (\gamma_{5}) s^{c}",
        "1.0/sqrt(6.0) * [u^{a} (C) s^{b} ] (\gamma_{5}) d^{c}",
        "-1.0/sqrt(6.0) * [d^{a} (C) s^{b} ] (\gamma_{5}) u^{c}",
    ]
    return props


def lambda0_2bar():

    props = {}

    props["gell_mann_matrices"] = []
    props["levi_civita_indices"] = ["ap;bp;cp"]
    props["interpolator_terms"] = [
        "-2.0/sqrt(6.0) * As^{cp} (\gamma_{5}) [Ad^{bp} (C) Au^{ap} ]",
        "-1.0/sqrt(6.0) * Ad^{cp} (\gamma_{5}) [As^{bp} (C) Au^{ap} ]",
        "1.0/sqrt(6.0) * Au^{cp} (\gamma_{5}) [As^{bp} (C) Ad^{ap} ]",
    ]
    return props


######################Mesons


def pip():

    props = {}

    props["lorentz_indices"] = []
    props["gell_mann_matrices"] = []
    props["levi_civita_indices"] = []
    props["interpolator_terms"] = ["1.0 * [Ad^{e} (\gamma_{5}) u^{e}]"]
    return props


def pipbar():

    props = {}

    props["gell_mann_matrices"] = []
    props["levi_civita_indices"] = []
    props["interpolator_terms"] = ["-1.0 * [Au^{ep} (\gamma_{5}) d^{ep}"]
    return props


def kaonp():

    props = {}

    props["lorentz_indices"] = []
    props["gell_mann_matrices"] = []
    props["levi_civita_indices"] = []
    props["interpolator_terms"] = ["1.0 * [As^{e} (\gamma_{5}) u^{e}]"]
    return props


def kaonpbar():

    props = {}

    props["gell_mann_matrices"] = []
    props["levi_civita_indices"] = []
    props["interpolator_terms"] = ["-1.0 * [Au^{ep} (\gamma_{5}) s^{ep}"]
    return props


# Actual utility functions


def QuarkCharge(quark, *args, **kwargs):
    """
    Returns the charge of a given quark.

    Arguments:
    quark -- char: quark in question
    """

    if quark == "u":
        return -2
    elif quark in ["d", "s"]:
        return 1
    elif "n" in quark:
        return 0
    else:
        raise NotImplementedError(f"{quark} is not implemented")


def HadronicCharge(kd, particle, structure, *args, **kwargs):
    """
    Calculates the hadronic charge of a particle.

    Takes into account the particle, the quark structure being used
    and the relative background field strength.

    Arguments:
    kd        -- int: Background field strength
    particle  -- str: The particle to calculate
    structure -- char list: The quark structure in form [u,d,s]
    """

    # Interp functions contain quarks: u,d,s and anti quarks Au,Du,Ds.
    # Will count instances of each, but counting u,d,s will also count
    # Au,Ad,As.
    # We basically want number of quarks not matched by an anti-quark
    # which we get by subtracting 2*(anti quarks) from total quarks.

    # Initialise lists for counts
    totalQuarkCounts = []
    antiQuarkCounts = []

    # Particle interpolating field. Only ever need one term as all
    # terms have same base quark structure.
    particleInterp = globals()[particle]()["interpolator_terms"][0]

    # Looping over quarks
    for quark in ["u", "d", "s"]:
        # Counting and appending appearances
        totalQuarkCounts.append(particleInterp.count(quark))
    # Looping over anti-quarks
    for antiQuark in ["Au", "Ad", "As"]:
        antiQuarkCounts.append(particleInterp.count(antiQuark))

    # Calculating number of un-matched quarks in hadron.
    # List comprehension is easiest way to do element by element subtraction
    netQuarkCounts = [
        total - 2 * anti for total, anti in zip(totalQuarkCounts, antiQuarkCounts)
    ]

    # Counting up total charge by looping through structure and netQuarkCounts
    charge = 0
    for quark, count in zip(structure, netQuarkCounts):
        charge += QuarkCharge(quark) * count

    return charge * kd


def CheckForVanishingFields(
    kd, particleList=None, chi=None, chibar=None, *args, **kwargs
):
    """
    Removes interpolator combinations which vanish under isospin sym.

    Arguments:
    kd         -- int: Field strength
    particList -- nested list: List of list of particle names. In form
                       [chi,chibar].

    Returns:
    updatedList -- nested list: List of list of particle names. Format as
                       above. Function does not act in place.
    """

    if particleList is None:
        if chi is None or chibar is None:
            raise ValueError(
                "Either particleList or chi and chibar must be specified with non-None values"
            )

        particleList = [[chi, chibar]]

    # Isospin symmetry only when kd = 0
    if kd != 0:
        return particleList

    # Particles which when combined in any source/sink operator produce should
    # be placed here. Each inner list will test all permutations of that list.
    # Separate inner lists will not be compared.
    # ie. [[a,b,c],[d,e]] would check all permutations of ab,ac,ba... and de...
    # but not ad,ae...
    badParticles = [["lambda0", "sigma0"]]

    badCombinations = []
    # Getting the combinations which vanish. Assumes aa would not vanish
    for particleSet in badParticles:
        badCombinations.append(
            [[p1, p2] for p1 in particleSet for p2 in particleSet if p1 != p2]
        )
    # Un-nests the list so that we can just use 1 loop
    badCombinations = [comb for sublist in badCombinations for comb in sublist]

    # Looping through particles and bad combinations
    badList = []
    for chi, chibar in particleList:
        for pair in badCombinations:
            # Checking if the particles match
            if pair[0] in chi and pair[1] in chibar:
                badList.append([chi, chibar])

    # Don't want to modify the original list
    updatedList = particleList.copy()
    # Removing vanishing combinations
    for chi, chibar in badList:
        updatedList.remove([chi, chibar])

    return updatedList
