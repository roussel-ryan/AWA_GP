import numpy as np
import logging
import torch

from botorch import settings

settings.suppress_botorch_warnings(True)

import os
import sys

sys.path.append('\\'.join(os.getcwd().split('\\')[:-1]))

from accelerator_control import controller, observations, interface, parameter
from accelerator_control.algorithms import explore

import matplotlib.pyplot as plt

# main()
logging.basicConfig(level=logging.INFO)

c = controller.Controller('test.json', controller_interface=interface.TestInterface())
opt_params = c.get_named_parameters(['X1', 'X2'])

# MOBO test
mobo_obs = observations.TestMOBO()
for i in range(10):
    c.set_parameters(opt_params, np.random.rand(2))
    c.observe(mobo_obs)

print(c.data)

exp_obs = [mobo_obs.children[0]]
constr_obs = [mobo_obs.children[2]]
opt = explore.BayesianExploration(opt_params, exp_obs, c, constr_obs, sigma=0.01)
opt.run()
print(c.data)

# print(opt.gp.state_dict())


# plot to test
opt_data = c.group_data().loc[:, ['X1', 'X2']].to_numpy()
fig, ax = plt.subplots()
ax.plot(opt_data[10:, 0], opt_data[10:, 1], 'C0')
ax.plot(opt_data[:10, 0], opt_data[:10, 1], 'C1+')
# c.group_data().plot('FocusingSolenoid', 'BuckingSolenoid')
plt.show()
