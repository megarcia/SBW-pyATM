# pylint: disable=C0103,R0205,R0902,R0914,R0915,R1711
"""
Python script "SBW_empirical.py"
by Matthew Garcia, Postdoctoral Research Associate
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2019-2021 by Matthew Garcia
"""


import numpy as np


class SBW(object):
    """Declare SBW empirical constants and methods."""

    def __init__(self):
        # morphology - wing area from Regniere et al. [2019]
        self.A_min = [0.1563, 0.2007]       # [M, F] from Delisle data, single forewing [cm2]
        self.A_max = [0.5214, 0.6105]       # [M, F] from Delisle data, single forewing [cm2]
        self.A_mean = [0.3606, 0.4208]      # [M, F] from Delisle data, single forewing [cm2]
        self.A_stdv = [0.0472, 0.0634]      # [M, F] from Delisle data, single forewing [cm2]
        # morphology - mass (not including fecundity effects) from Regniere et al. [2019]
        self.M_min_mean = [0.0018, 0.0039]  # [M, F] spent females [kg]
        self.M_min_stdv = [0.0002, 0.0009]  # [M, F] spent females [kg]
        self.M_mean = [0.00475, 0.00684]    # [M, F] mass mean [kg]
        self.M_stdv = [0.00143, 0.00287]    # [M, F] mass stdv [kg]
        self.M_max_mean = [0.0110, 0.0194]  # [M, F] fully gravid females [kg]
        self.M_max_stdv = [0.0010, 0.0042]  # [M, F] fully gravid females [kg]
        self.M_c1 = [3.626, 3.626]          # [M, F] A coefficient [kg]
        self.M_c2 = [-6.697, -6.582]        # [M, F] intercept [kg]
        self.M_err_mean = [1.0, 1.0]        # [M, F] lognormal error mean [kg]
        self.M_err_std = [0.206, 0.289]     # [M, F] lognormal error stdv [kg]
        # fecundity
        self.F_alpha = 739.2             # A coefficient
        self.F_beta = 1.758              # A exponent
        self.F_err_mean = 1.0            # lognormal error mean
        self.F_err_stdv = 0.222          # lognormal error stdv
        # oviposition (to be replaced with temperature-based formulation)
        self.F_frac_per_brood = 0.5      # fraction of remaining fecundity laid
        # mass including fecundity effects from Regniere et al. [2019]
        self.M_F_c1 = 0.9736             # G coefficient, mass calculation using gravidity [kg]
        self.M_F_c2 = 2.14               # A coefficient, mass calculation using gravidity [kg]
        self.M_F_c3 = 1.3049             # G*A coefficient, mass calculation using gravidity [kg]
        self.M_F_c4 = -6.4648            # intercept, mass calculation using gravidity [kg]
        self.M_F_err_mean = 1.0          # lognormal error mean, mass calculation using gravidity [kg]
        self.M_F_err_stdv = 0.16         # lognormal error stdv, mass calculation using gravidity [kg]
        # wingbeat frequency coefficients
        self.K_coeff = 167.5             # from Regniere et al. [2019] [-]
        self.nu_max = 72.5               # from Regniere et al. [2019] [Hz]
        self.a = 23.0                    # from Regniere et al. [2019] [C]
        self.b = 0.115                   # from Regniere et al. [2019] [1/C]
        # defoliation
        self.D_coeff = 117.0             # from Nealis and Regniere [2004]
        self.F_intercept = 216.8         # from Nealis and Regniere [2004]
        # circadian rhythm coefficients from Regniere et al. [2019]
        self.circadian_p1_mean = -3.8    # [h]
        self.circadian_p1_stdv = 0.7     # [h]
        self.circadian_p2_mean = 0.145   # [h/C]
        self.circadian_p2_stdv = 0.031   # [h/C]
        self.circadian_p3_mean = -1.267  # [h]
        self.circadian_p3_stdv = 0.146   # [h]
        self.circadian_p4_mean = -0.397  # [-]
        self.circadian_p4_stdv = 0.187   # [-]
        self.circadian_p5_mean = -2.465  # [-]
        self.circadian_p5_stdv = 0.152   # [-]
        self.circadian_kf_mean = 1.35    # [-]
        self.circadian_kf_stdv = 0.025   # [-]
        # physics coefficients (for later use)
        self.c_L = 0.0                   # lift coefficient [-]
        self.c_D = 0.0                   # drag coefficient [-]

    def calc_nu_L(self, A, M):
        """Regniere et al. [2019]."""
        nu_L = self.K_coeff * np.sqrt(M) / A
        return nu_L

    def calc_nu_T(self, T):
        """Regniere et al. [2019]."""
        nu_T = self.nu_max / (1.0 + np.exp(-1 * self.b * (T - self.a)))
        if nu_T < 20.0:
            nu_T = 0.0
        return nu_T

    def calc_TL(self, nu_L):
        """Regniere et al. [2019]."""
        TL = self.a - self.b * np.log((self.nu_max / nu_L) - 1.0)
        return TL

    def calc_nu_L_Ts(self, Ts, delta_nu):
        """Regniere et al. [2019]."""
        nu_L_Ts = self.calc_nu_T(Ts) * delta_nu
        return nu_L_Ts

    def calc_Ts(self, nu_L, delta_nu):
        """Regniere et al. [2019]."""
        Ts = self.a - self.b * np.log((self.nu_max * delta_nu / nu_L) - 1.0)
        return Ts

    def calc_mass_from_wing_area(self, sex, A, M_err):
        """Regniere et al. [2019]."""
        M = M_err * np.exp(self.M_c1[sex] * A + self.M_c2[sex])
        return M

    def calc_fecundity(self, A, F_err):
        """Regniere et al. [2019]."""
        F = F_err * self.F_alpha * A**self.F_beta
        return F

    def calc_fecundity_0(self, F, D=0.0):
        """Nealis and Regniere [2004]; Regniere et al. [2019]."""
        F_0 = F / ((1.0 - (self.D_coeff * D)) / self.F_intercept)
        return F_0

    def calc_mass_from_gravidity(self, A, G, M_err):
        """Regniere et al. [2019]."""
        M = M_err * np.exp(self.M_F_c1 * G + self.M_F_c2 * A +
                           self.M_F_c3 * G * A + self.M_F_c4)
        return M

    def calc_circadian_deltas(self, T_ref):
        """Regniere et al. [2019]."""
        circadian_p1 = \
            np.random.normal(loc=self.circadian_p1_mean, scale=self.circadian_p1_stdv)
        circadian_p2 = \
            np.random.normal(loc=self.circadian_p2_mean, scale=self.circadian_p2_stdv)
        circadian_p3 = \
            np.random.normal(loc=self.circadian_p3_mean, scale=self.circadian_p3_stdv)
        circadian_p4 = \
            np.random.normal(loc=self.circadian_p4_mean, scale=self.circadian_p4_stdv)
        circadian_p5 = \
            np.random.normal(loc=self.circadian_p5_mean, scale=self.circadian_p5_stdv)
        circadian_kf = \
            np.random.normal(loc=self.circadian_kf_mean, scale=self.circadian_kf_stdv)
        delta_s = circadian_p1 + circadian_p2 * T_ref
        delta_0 = circadian_p3 + circadian_p4 * delta_s
        delta_f = circadian_p5 * delta_0
        delta_f_potential = circadian_kf * delta_f
        deltas = [delta_s, delta_0, delta_f, delta_f_potential]
        return deltas  # list of 4 * float

# end SBW_empirical.py
