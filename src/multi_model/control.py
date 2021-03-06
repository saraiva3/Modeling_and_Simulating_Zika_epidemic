'''
Created on 20 Feb. 2016

This file illustrated the use of classes to create multiple models hybrid ABM-SD Model specified in Mesa and PySD

.. codeauthor::  GitHub: philippschw  <philipp.schw@gmail.com>

'''
'''
Created on 20 Feb. 2016

This file illustrated the use of classes to create multiple models hybrid ABM-SD Model specified in Mesa and PySD

.. codeauthor::  GitHub: philippschw  <philipp.schw@gmail.com>

'''
import pandas as pd
import numpy as np
import pysd
import math

#global dct_adjacency
adjacency_matrix_df = pd.read_csv(r'input_data_simulation/csv_files/adjacency_matrix.csv', index_col=0)
# Script to transform matrix to dict with list
dct_adjacency = {}
for index, row in adjacency_matrix_df.iterrows():
    dct_adjacency[index] = row[row == 1].index.tolist()

#============================================================================================
#    Agent Based SIR Model Built in Python
#============================================================================================
from models.abm.Model_v1 import Human, Mosquito, SEIR_vector_borne_disease

#============================================================================================
#    Load System Dynamics SIR Model into Python
#============================================================================================
SD_model = pysd.read_vensim(r'src/models/sd/Model_v1.mdl') ######DIFFERNT STRUCTURE !!!!!!!!!!!!!

class Multi_models(object):
    _registry = []
    def __init__(self,
                 name):
        self._registry.append(self)
        self.name = int(name)
        self.lst_adjacency_regions = dct_adjacency[self.name]
        self.outbreak = False

    def __str__(self):
        return self.name

    def return_share_infectious(self, timestep):
        '''
        Function used for updating Flight Matrix
        '''
        return (self.ABM_SD_results.iloc[timestep]['infectious'] / dic['population'][self.name])

    def initialize_simulation_run(self,
                                    transmission_prob,
                                    recovery_period,
                                    intrinsic_incubation_period,
                                    share_herd_immunity,
                                    simultanousAct,
                                    network_type,
                                    Brazil_initial_infected,
                                    network_connectivity,
                                    Travel_adjacency_region,
                                    share_m_vertical_transmission,
                                    extrinsic_incubation_period,
                                    m_prob_reproduce,
                                    personal_protection_poor,
                                    personal_protection_rich,
                                    breeding_site_recreation_rich,
                                    breeding_site_recreation_poor,
                                    destruction_time_ponds,
                                    delaytime_reporting,
                                    share_reported_cases,
                                    month
                                  ):
        '''
        Initialize Pandas Dataframe where simulation result after each tick are stored for each regional model
        '''

        h_symptomatic_infectious_rich, h_exposed_rich = 0, 0
        if self.name == Region_initially_infected:
            h_symptomatic_infectious_rich, h_exposed_rich = Brazil_initial_infected, Brazil_initial_infected

        self.m_susceptible  = int(dic['population'][int(self.name)]*dic_vector[month][('Aegypti', self.name)])

        self.poor_population = int(dic['population'][int(self.name)]*dic['perc_pover'][self.name])
        self.rich_population = int(dic['population'][int(self.name)]* (1. - dic['perc_pover'][self.name]))

        self.nr_susceptible_poor = int(self.poor_population*(1.-share_herd_immunity))
        self.nr_susceptible_rich = int(self.rich_population*(1.-share_herd_immunity))

        self.nr_recovered_poor = int(self.poor_population*share_herd_immunity)
        self.nr_recovered_rich = int(self.rich_population*share_herd_immunity)

        ABM_SD_results = pd.DataFrame({
                                        "m_susceptible": self.m_susceptible,
                                        "m_exposed": 0,
                                        "m_infectious": 0,

                                         'h_recovered_immune_rich': self.nr_recovered_rich,
                                         'h_susceptible_rich': self.nr_susceptible_rich,
                                         "h_exposed_rich": h_exposed_rich,
                                         "h_symptomatic_infectious_rich": h_symptomatic_infectious_rich,
                                         "h_asymptomatic_infectious_rich": h_symptomatic_infectious_rich*5,

                                        'h_recovered_immune_poor': self.nr_recovered_poor,
                                        'h_susceptible_poor': self.nr_susceptible_poor,
                                        "h_exposed_poor": 0,
                                        "h_symptomatic_infectious_poor":0,
                                        "h_asymptomatic_infectious_poor": 0,

                                        'cumulative_cases': 0,
                                      }, index=[0])# Retrieve data from input data df and index with time zero
                                      
       


        if network_type == 0:
            network_type = 'erdos_renyi_graph'
        elif  network_type == 1:
            network_type = 'barabasi_albert_graph'
        elif network_type == 2:
            network_type = 'watts_strogatz_graph'
        else:
            network_type = 'grid_2d_graph'

        if simultanousAct == 0:
            simultanousAct = False
        else:
            simultanousAct = True

        self.First_Time = True        
        self.ABM_population_size = 250
        self.share_herd_immunity = share_herd_immunity

        self.recovery_period = recovery_period
        self.intrinsic_incubation_period = intrinsic_incubation_period
        self.extrinsic_incubation_period = extrinsic_incubation_period
        self.m_prob_reproduce =  m_prob_reproduce
        self.transmission_probability = transmission_prob

        self.personal_protection_poor = personal_protection_poor
        self.personal_protection_rich = personal_protection_rich
        self.breeding_site_recreation_rich = breeding_site_recreation_rich
        self.breeding_site_recreation_poor = breeding_site_recreation_poor
        self.destruction_time_ponds = destruction_time_ponds
        self.delaytime_reporting = delaytime_reporting
        self.share_reported_cases = share_reported_cases

        self.share_m_vertical_transmission = share_m_vertical_transmission
        self.Travel_adjacency_region = Travel_adjacency_region

        ABM_model = SEIR_vector_borne_disease(
                 nr_infected=(h_symptomatic_infectious_rich+h_symptomatic_infectious_rich*5),
                 nr_exposed=h_exposed_rich,
                 nr_recovered_immune=int(self.share_herd_immunity*self.ABM_population_size),
                 simultanousAct=simultanousAct,
                 network_type = network_type,
                 human_population=self.ABM_population_size,
                 ratio_vectors_per_person = dic_vector[month][('Aegypti', self.name)],
                 intrinsic_incubation_period = intrinsic_incubation_period,
                 extrinsic_incubation_period = extrinsic_incubation_period,
                 m_prob_reproduce = m_prob_reproduce,
                 transmission_prob_human_to_vector = transmission_prob,
                 transmission_prob_vector_to_human =transmission_prob,
                 blood_meals_per_day = 4,
                 share_m_vertical_transmission = share_m_vertical_transmission,
                 recovery_period_human = recovery_period,
                 sexual_intercourse_day = .2,
                 share_symptomatic_humans = .2,
                 share_infected_mosquitos = 0,
                 share_extreme_poverty = dic['perc_pover'][self.name],
                 network_connectivity = network_connectivity
                 )
        # Store for convenience fixed var as instance parameters
        # self.infectivity= infectivity
        # self.duration = duration
        #Associate ABM model and simulation result collector with instance
        self.ABM_SD_results = ABM_SD_results
        self.ABM_model = ABM_model

        self.ABM_SD_results['infectious'] = self.ABM_SD_results['h_symptomatic_infectious_rich'] + self.ABM_SD_results['h_asymptomatic_infectious_rich']\
                                          + self.ABM_SD_results['h_symptomatic_infectious_poor'] + self.ABM_SD_results['h_asymptomatic_infectious_poor']
        #print ('succesfully init')

    def step_simulation(self, vector, Switch_flights, tick, month):
        exinfectious = 0
        #print ('step')
        for m in self._registry:
            if m.name in self.lst_adjacency_regions and m.outbreak == True:
                exinfectious += self.Travel_adjacency_region

        if Switch_flights == 1:
            if self.name in vector.countries_in_matrix:
                if int(vector.get_external_infectious(self.name)) > 0:
                    print (self.name, exinfectious, (vector.get_external_infectious(self.name)), self.ABM_SD_results.loc[tick, 'infectious'])
                exinfectious += vector.get_external_infectious(self.name)

        if  self.ABM_SD_results.iloc[-1]['infectious'] <= 20 and self.First_Time == True:

            #self.ABM_SD_results.iloc[-1]['infectious'] < 25 : # Condition for last row and specific column
            #print ('ABM Model Running', len(self.ABM_SD_results))
            try:
                self.ABM_model.Feed_data(int(exinfectious))
            except:
                pass
            
            self.ABM_model.step()
            model_step = self.ABM_model.datacollector.get_model_vars_dataframe()
            # print ('df ABM SD Results_Model Step{}'.format(self.ABM_SD_results))
            # print ('df ABM SD Results_Model Step{}'.format(model_step))

            # print model_step
            poor_pop_ABM =  self.ABM_population_size * dic['perc_pover'][self.name]
            rich_pop_ABM =  self.ABM_population_size * (1. - dic['perc_pover'][self.name])

            model_step['h_recovered_immune_rich'] = model_step['h_recovered_immune_rich'] + self.nr_recovered_rich\
                                             - poor_pop_ABM *  self.share_herd_immunity
            model_step['h_susceptible_rich'] = model_step['h_susceptible_rich'] + self.nr_susceptible_rich\
                                             - poor_pop_ABM *   (1.-self.share_herd_immunity)

            model_step['h_recovered_immune_poor'] = model_step['h_recovered_immune_poor'] + self.nr_recovered_poor\
                                 - rich_pop_ABM *   self.share_herd_immunity
            model_step['h_susceptible_poor'] = model_step['h_susceptible_poor'] + self.nr_susceptible_poor\
                                 - rich_pop_ABM * (1.-self.share_herd_immunity)

            model_step['m_susceptible'] = model_step['m_susceptible'] + self.m_susceptible\
                                 - self.ABM_population_size * dic_vector[month][('Aegypti', self.name)]

            self.ABM_SD_results = pd.concat([self.ABM_SD_results, model_step.tail(1)], axis=0, join='inner') # Concatenate ABM and SD datafranes

        else:
            if self.First_Time == True:

                sim_time_switch = len(self.ABM_SD_results)-1
                rest_sim_time = Simulation_time - sim_time_switch

                self.outbreak = True

                #print ('Simulation-time: Switch', len(self.ABM_SD_results))
                self.ABM_SD_results['diagnosed_zika_cases']= 0
                self.ABM_SD_results['reported_cases']= 0
                self.ABM_SD_results['max_awareness']= 0
                self.ABM_SD_results['public_awareness']= 0
                self.ABM_SD_results['availability_breeding_poor']= 100
                self.ABM_SD_results['availability_breeding_rich']= 70
                
                #print ('Setting up SD model')

                model_step = pd.DataFrame(SD_model.run(
                    params = {

                            'normal_blood_meals_a_day':1.5,
                            'transmission_probability':self.transmission_probability,

                            'normal_personal_protection_poor': self.personal_protection_poor,
                            'normal_personal_protection_rich': self.personal_protection_rich,
                            'rate_of_breeding_site_recreation_rich': self.breeding_site_recreation_rich,
                            'rate_of_breeding_site_recreation_poor': self.breeding_site_recreation_poor,
                            'destruction_time_of_water_ponds' : self.destruction_time_ponds,
                            'delaytime_of_reporting' : self.delaytime_reporting,
                            'share_reported_cases' : self.share_reported_cases,

                            'population': dic['population'][self.name],
                            #'share_herd_immunity': self.share_herd_immunity,
                            'human_population': dic['population'][self.name],
                            'vertical_transmission_infection_rate' : self.share_m_vertical_transmission,
                            'recovery_period_human' : self.recovery_period,
                            'ratio_vectors_per_person' : dic_vector[month][('Aegypti', self.name)],
                            'intrinsic_incubation_period' : self.intrinsic_incubation_period,
                            'extrinsic_incubation_period' : self.extrinsic_incubation_period,

                            'initial_susceptible_m': self.ABM_SD_results.iloc[-1]['m_susceptible'],
                            'initial_exposed_m': self.ABM_SD_results.iloc[-1]['m_exposed'],
                            'intial_infectious_m' : self.ABM_SD_results.iloc[-1]['m_infectious'],

                            'initial_recovered_poor': self.ABM_SD_results.iloc[-1]['h_recovered_immune_poor'],
                            'inital_susceptible_poor' : self.ABM_SD_results.iloc[-1]['h_susceptible_poor'],
                            'initial_exposed_poor' : self.ABM_SD_results.iloc[-1]['h_exposed_poor'],
                            'initial_infectious_poor_sym' : self.ABM_SD_results.iloc[-1]['h_symptomatic_infectious_poor'],
                            'initial_infectious_poor_asym': self.ABM_SD_results.iloc[-1]['h_asymptomatic_infectious_poor'],

                            'initial_recovered_rich': self.ABM_SD_results.iloc[-1]['h_recovered_immune_rich'],
                            'inital_susceptible_rich' : self.ABM_SD_results.iloc[-1]['h_susceptible_rich'],
                            'initial_exposed_rich' : self.ABM_SD_results.iloc[-1]['h_exposed_rich'],
                            'initial_infectious_rich_sym' : self.ABM_SD_results.iloc[-1]['h_symptomatic_infectious_rich'],
                            'initial_infectious_rich_asym': self.ABM_SD_results.iloc[-1]['h_asymptomatic_infectious_rich'],

                            'init_cumulative_cases': self.ABM_SD_results.iloc[-1]['cumulative_cases'],
                            'init_diagnosed_cases': self.ABM_SD_results.iloc[-1]['diagnosed_zika_cases'],
                            'init_reported_cases': self.ABM_SD_results.iloc[-1]['reported_cases'],
                            'init_max_awareness': self.ABM_SD_results.iloc[-1]['max_awareness'],
                            'init_public_awareness': self.ABM_SD_results.iloc[-1]['public_awareness'],
                            'init_breeding_sites_poor': self.ABM_SD_results.iloc[-1]['availability_breeding_poor'],
                            'init_breeding_sites_rich': self.ABM_SD_results.iloc[-1]['availability_breeding_rich'],

                             },
                return_timestamps=np.linspace(1, rest_sim_time, rest_sim_time)))
                self.First_Time = False
                self.ABM_SD_results = pd.concat([self.ABM_SD_results, model_step], axis=0, join='inner') # Concatenate ABM and SD datafranes

            #print 'succesfully advanced SD model'
            # print model_step
        self.ABM_SD_results = self.ABM_SD_results.reset_index(drop=True) #  Reset index

        self.ABM_SD_results['infectious'] = self.ABM_SD_results['h_symptomatic_infectious_rich'] + self.ABM_SD_results['h_asymptomatic_infectious_rich']\
                                          + self.ABM_SD_results['h_symptomatic_infectious_poor'] + self.ABM_SD_results['h_asymptomatic_infectious_poor']

        # print len(self.ABM_SD_results)
        # print (self.ABM_SD_results)

    def show_ABM_SD_results(self):
        self.ABM_SD_results['recovered_immune'] = self.ABM_SD_results['h_recovered_immune_rich']+self.ABM_SD_results['h_recovered_immune_poor']
        self.ABM_SD_results['susceptible'] = self.ABM_SD_results['h_susceptible_rich']+self.ABM_SD_results['h_susceptible_poor']
        self.ABM_SD_results['exposed'] = self.ABM_SD_results['h_exposed_rich']+self.ABM_SD_results['h_exposed_poor']

        self.ABM_SD_results.rename(columns=lambda x: str(self.name)+'_'+x , inplace=True)

        lst_KPI = ['susceptible', 'exposed', 'infectious','recovered_immune', 'cumulative_cases']
        lst_KPI = [str(self.name)+'_'+ s for s in lst_KPI]
        #print ('passed show ABM')
        return self.ABM_SD_results[lst_KPI]

'''
2. Class Flight Matrix Model
-Interaction between models on country level
'''
class Flight_Matrix(object):
    def __init__(self,
                matrix, fkt_gradient=1, fkt_diminisher=1):
    ###
    ### Flight matrix has multiple indexes - select first month for now
    ###
        # self.init_normal_matrix = matrix.loc[1].copy()#Make a copy of initial flight matrix!!
        # self.matrix = matrix.loc[1]

        self.multiindex_matrix = matrix

        self.countries_in_matrix = matrix.loc[1].index.tolist()
        self.fkt_diminisher = fkt_diminisher
        self.fkt_gradient = fkt_gradient
        self.arr = np.linspace(0,1,100)

        self.normalized_array = self.normalized_sigmoid_fkt()
        # print self.normalized_array

    def select_flight_matrix(self, month):
        self.init_normal_matrix = self.multiindex_matrix.loc[month].copy()
        self.matrix = self.multiindex_matrix.loc[month].copy()
        ## Ensure that diagonal 0, so that ther is no air-travel within region
        for i in self.matrix.index:
            self.matrix.set_value(i, i, 0)
            self.init_normal_matrix.set_value(i, i, 0)

    def normalized_sigmoid_fkt(self): #Returns array of normalized exponential function, output between 0 and 1
        a, b = self.fkt_diminisher, self.fkt_gradient
        #sigmoid function with parameters a = center; b = width
        s= 1/(1+np.exp(b*(self.arr-a)))
        return 1*(s-min(s))/(max(s)-min(s)) # normalize function to 0-1

    def find_nearest(self, value=0): #Returns approximated index of  input value in array
        idx = np.searchsorted(self.arr, value, side="left")
        if math.fabs(value - self.arr[idx-1]) < math.fabs(value - self.arr[idx]):
            return idx-1
        else:
            return idx

    def show_vector(self):
        return self.matrix

    def show_vector_normal(self):
        return self.init_normal_matrix

    def update_flight_matrix(self, timestep):
        for m in Multi_models._registry: #Iteratre over the index (rows) and apply specified function that\
            if m.__str__() in self.countries_in_matrix:
                # print (m.return_share_infectious())
                # print (m.__str__())
                self.matrix[m.__str__()] = self.init_normal_matrix.apply(lambda x:\
                        x[m.__str__()]* self.normalized_array[self.find_nearest(value=m.return_share_infectious(timestep))], axis=1)

    def update_column_share_infectious(self, timestep):
        self.matrix['share_infectious'] = np.nan
        for m in Multi_models._registry:
            self.matrix.set_value(m.__str__(), 'share_infectious', m.return_share_infectious(timestep))

    def get_external_infectious(self, country):
        return (self.matrix[int(country)]*self.matrix['share_infectious']).sum(axis=0)



