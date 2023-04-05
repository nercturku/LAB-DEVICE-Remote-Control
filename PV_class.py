"""
4.4.2023 - MM

File to store utility function to ease code reading in the main file

"""
import numpy as np

class PV:
    def __init__(self, V_oc_stc: float, I_sc_stc: float, FFI: float, FFU: float) -> None:
        ## Create PV panel params and store it
        self.V_oc_stc = V_oc_stc
        self.I_sc_stc = I_sc_stc
        self.FFI = FFI
        self.FFU = FFU
        self.C_AQ = (FFU - 1)/np.log(1-FFI)
    
    def I_sc_fct(self):
        """
        
        Compute the short circuit current of the simulated PV panel
        according to irradiance level [W/m²]
        I_sc_stc : short circuit current in standard test conditions
        """
        self.I_sc = self.I_sc_stc * (self.G / 1000)
        self.I_0 = self.I_sc * (1-self.FFI)**(1/(1-self.FFU))
    
    def V_oc_fct(self, CV = 8.593e-2, CR = 1.088e-4, CG = 2.514e-3):
        """
        Parameters
        ----------
        G : Float
            irrandiance [W/m²]
        V_oc_stc : Float
            Open circuit Voltage [V]
        CV,CR,CG : Float, optional
            Techonology correction Factor. 
            The default is 8.593e-2, 1.088e-4, 2.514e-3 respectively.
        Returns
        -------
        V_oc : Open circuit voltage [V] according to irradiance
        """
        self.V_oc = self.V_oc_stc * (np.log(1 + self.G/CG)*CV - CR * self.G)
    
    def irradiance(self, count,mode,minute):
        """
        Compute irradiance [W/m²] according to the counter and the simulation mode
        """
        if mode == 'dynamic':
            slope = (1000 - 300)/(120 * minute / 7)
            sec = count %(minute*60)
            if sec < 60 * minute/7:
                G = 300
            elif sec < 60 * minute * 3 / 7:
                t = sec - 60 * minute /7 
                G = 300 + slope * t
            elif sec < 60 * minute * 4/7:
                G = 1000
            elif sec < 60 * minute * 6/7:
                t = sec - 60 * minute * 4/7
                G = 1000 - slope * t
            elif sec < 60 * minute:
                G = 300
        elif mode == 'static':
            G = 1000
        self.G = G
    
    def PV_I_V_P_array(self):
        """
        Compute Array for Voltage, Current and Power of the PV panel
        """

        self.V_PV_array = np.linspace(0,self.V_oc,1000)
        self.I_PV_array = (self.I_sc - self.I_0 * (np.exp(self.V_PV_array / (self.V_oc * self.C_AQ)) - 1)) - 0.01
        self.P_PV_array = []
        for k in range(len(self.V_PV_array)):
            self.P_PV_array.append(self.V_PV_array[k] * self.I_PV_array[k])
    
    def supply_settings(self, I_load: float):
        """Gives the seetings for the power supply regarding the command given by the load"""
        I_supply = I_load + 0.01
        V_supply = self.V_oc * self.C_AQ * np.log(1 + (self.I_sc - I_supply)/self.I_0)

        return V_supply, I_supply

    def __call__(self, count, mode, minute):
        self.irradiance(count, mode, minute)
        self.I_sc_fct()
        self.V_oc_fct()
        self.PV_I_V_P_array()