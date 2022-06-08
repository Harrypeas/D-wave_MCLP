# -*- coding: utf-8 -*-
"""
Created on Wed Jun  8 19:59:28 2022

@author: harry
"""

import numpy as np
num_items = 17
weights = [3,4,5,6,7,4,2,3,4,5,6,3,5,4,3,5,1]
bin_capacity = 25

demandCoordinates = [(88, 16),(25, 76),(69, 13),(73, 56),(80, 100),(22, 92),(32, 84),(73, 46),(29, 10),(92, 32),(44, 44),(55, 26),(71, 27),(51, 91),(89, 54),(43, 28),(40, 78)]
centerCoordinates = [(32, 60),(69, 33),(49, 40),(72, 81),(61, 65)]

distances = np.zeros((17, 5))
for i in range(len(demandCoordinates)):
    for j in range(len(centerCoordinates)):
        distances[i][j] = np.sqrt(
            (demandCoordinates[i][0] - centerCoordinates[j][0]) ** 2 + 
            (demandCoordinates[i][0] - centerCoordinates[j][0]) ** 2)

print("Problem: Allocate demand points of total weight of {} into centers of capacity {}.".format(
      sum(weights), bin_capacity))     

from dimod import ConstrainedQuadraticModel
cqm = ConstrainedQuadraticModel()

from dimod import Binary
demand_required = [Binary(f'demand_required_{i}') for i in range(num_items)]
bin_used = [Binary(f'bin_used_{j}') for j in range(5)]

def demand_bin_result():
    res = 0
    for i in range(len(demand_required)):
        for j in range(len(bin_used)):
            res += demand_required[i] * bin_used[j] * distances[i][j]
    return res
cqm.set_objective(-sum(demand_required) + demand_bin_result())



item_in_bin = [[Binary(f'item_{i}_in_bin_{j}') for j in range(5)]
     for i in range(num_items)]
for i in range(num_items):
    one_bin_per_item = cqm.add_constraint(sum(item_in_bin[i]) - 1 <= 0, label=f'item_placing_{i}')
    
for j in range(5):
    bin_up_to_capacity = cqm.add_constraint(
        sum(weights[i] * item_in_bin[i][j] for i in range(num_items)) - bin_used[j] * bin_capacity <= 0,
        label=f'capacity_bin_{j}')
    
for j in range(5):
    bin_up_to_capacity = cqm.add_constraint(
        sum(distances[i][j] * item_in_bin[i][j] for i in range(num_items)) - 50 <= 0,
        label=f'distance_bin_{j}')
    
from dwave.system import LeapHybridCQMSampler
sampler = LeapHybridCQMSampler()

sampleset = sampler.sample_cqm(cqm,
                               time_limit=180,
                               label="SDK Examples - Bin Packing")  
feasible_sampleset = sampleset.filter(lambda row: row.is_feasible)  
if len(feasible_sampleset):      
   best = feasible_sampleset.first
   print("{} feasible solutions of {}.".format(
      len(feasible_sampleset), len(sampleset)))
   
selected_bins = [key for key, val in best.sample.items() if 'demand_required' in key and val]

def get_indices(name):
    return [int(digs) for digs in name.split('_') if digs.isdigit()]
