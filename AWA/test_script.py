import os
import sys

sys.path.append('\\'.join(os.getcwd().split('\\')[:-1]))

import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

from accelerator_control import controller, pre_observation
from accelerator_control.algorithms import sample, explore
import interface
import observations
import numpy as np
import logging

logging.getLogger().setLevel(logging.INFO)


def main():
    logging.debug('test')
    logging.getLogger('accelerator_control.algorithms').setLevel(logging.INFO)
    logging.getLogger('emittance_calculation').setLevel(logging.INFO)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)

    # define controller
    interf = interface.AWAInterface(False, testing=False)
    c = controller.Controller('config.json', controller_interface=interf)

    screen_obs = observations.AWAScreen(n_samples=5)
    emittance_obs = observations.Emittance(0.002,
                                           2.84,
                                           1086,
                                           n_samples=5,
                                           target_charge=5.3e-9,
                                           charge_deviation=0.1)

    # scan_vals = np.array(((8.3, 1.2),
    #                      (8.3, 1.4),
    #                      (8.3, 1.6)))
    # scan_vals1 = np.array(((8.84, 0.37, 0.0))).reshape(1,-1)
    
    if 1:
        n = 3
        x = np.linspace(0,1.0,n)
        xx = np.meshgrid(x,x)
        scan_vals = np.vstack([ele.ravel() for ele in xx]).T
        print(scan_vals)
    
    
    #scan_vals = np.random.rand(2, 2)
    # scan_vals = np.linspace(-0.05,0.3,10).reshape(-1,1)

    param = c.get_named_parameters(['FocusingSolenoid',
                                    'MatchingSolenoid'])

    # param = c.get_named_parameters(['DQ5'])
    pre_observation_func = pre_observation.Sleep(5)
    # pre_observation_func = pre_observation.KeyPress()

    if 0:
        sampling = sample.Sample(param,
                                 [screen_obs],
                                 c, scan_vals,
                                 normalized=False,
                                 pre_observation_function=pre_observation_func)
        sampling.run()

    if 1:
        emit_sampling = sample.Sample(param,
                                      [emittance_obs],
                                      c, scan_vals,
                                      normalized=True,
                                      save_images=True,
                                      pre_observation_function=pre_observation_func)
        emit_sampling.run()

    # c.load_data('data/good_emit_exploration.pkl')

    # do bayesian exploration
    roi_constraint = screen_obs.children[9]
    bexp = explore.BayesianExploration(param,
                                       [emittance_obs],
                                       c,
                                       [roi_constraint],
                                       n_steps=50,
                                       sigma=100)
    if 0:
        bexp.run()
        # model = bexp.create_model()
        # bexp.get_acq(model, True)

    # c.load_data('data/good_3_parameter_exploration.pkl')
    print(c.data[['MatchingSolenoid', 'FocusingSolenoid', 'LinacPhase',
                  'EMIT', 'IMGF', 'ROT_ANG']])
    # print(c.data)
    model = bexp.create_model()
    models = model.models
    for m in models:
        print(m.covar_module.base_kernel.lengthscale)
    # bexp.get_acq(model, True)
    # bexp.plot_model(0, False)


if __name__ == '__main__':
    main()
