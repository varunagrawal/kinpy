import numpy as np
from kinpy import mjcf
from kinpy import visualizer

chain = mjcf.build_chain_from_mjcf(open("humanoid/humanoid.xml").read())
print(chain)
print(chain.get_joint_parameter_names())
th = {'left_knee': 0.0, 'right_knee': 0.0}
ret = chain.forward_kinematics(th)
print(ret)
viz = visualizer.Visualizer()
viz.add_robot(chain, ret, axes=True)
viz.spin()