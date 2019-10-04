from urdf_parser_py.urdf import URDF, Mesh, Cylinder, Box, Sphere
from . import frame
from . import chain
from . import transform


def _convert_transform(origin):
    if origin is None:
        return transform.Transform()
    else:
        return transform.Transform(rot=origin.rpy, pos=origin.xyz)


def _convert_visual(visual):
    if visual is None or visual.geometry is None:
        return frame.Visual()
    else:
        v_tf = _convert_transform(visual.origin)
        if isinstance(visual.geometry, Mesh):
            g_type = "mesh"
            g_param = visual.geometry.filename
        elif isinstance(visual.geometry, Cylinder):
            g_type = "cylinder"
            g_param = (visual.geometry.radius, visual.geometry.length)
        elif isinstance(visual.geometry, Box):
            g_type = "box"
            g_param = visual.geometry.size
        elif isinstance(visual.geometry, Sphere):
            g_type = "sphere"
            g_param = visual.geometry.radius
        else:
            g_typ = None
            g_param = None
        return frame.Visual(v_tf, g_type, g_param)


def _build_chain_recurse(root_frame, lmap, joints):
    children = []
    for j in joints:
        if j.parent == root_frame.link.name:
            child_frame = frame.Frame(j.child + "_frame")
            child_frame.joint = frame.Joint(j.name, offset=_convert_transform(j.origin),
                                            joint_type=j.type, axis=j.axis)
            link = lmap[j.child]
            child_frame.link = frame.Link(link.name, offset=_convert_transform(link.origin),
                                          visuals=[_convert_visual(link.visual)])
            child_frame.children = _build_chain_recurse(child_frame, lmap, joints)
            children.append(child_frame)
    return children


def build_chain_from_urdf(data):
    robot = URDF.from_xml_string(data)
    lmap = robot.link_map
    joints = robot.joints
    n_joints = len(joints)
    has_root = [True for _ in range(len(joints))]
    for i in range(n_joints):
        for j in range(i+1, n_joints):
            if joints[i].parent == joints[j].child:
                has_root[i] = False
            elif joints[j].parent == joints[i].child:
                has_root[j] = False
    for i in range(n_joints):
        if has_root[i]:
            root_link = lmap[joints[i].parent]
            break
    root_frame = frame.Frame(root_link.name + "_frame")
    root_frame.joint = frame.Joint()
    root_frame.link = frame.Link(root_link.name, _convert_transform(root_link.origin),
                                 [_convert_visual(root_link.visual)])
    root_frame.children = _build_chain_recurse(root_frame, lmap, joints)
    return chain.Chain(root_frame)


def build_serial_chain_from_urdf(data, end_link_name, root_link_name=""):
    urdf_chain = build_chain_from_urdf(data)
    return chain.SerialChain(urdf_chain, end_link_name + "_frame",
                             "" if root_link_name == "" else root_link_name + "_frame")