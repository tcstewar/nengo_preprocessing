import nengo

def remove_passthrough(model):
    objs = model.all_ensembles + model.all_nodes
    conns = model.all_connections
    objs, conns = nengo.utils.builder.remove_passthrough_nodes(objs, conns)    

    model2 = nengo.Network()
    for obj in objs:
        if isinstance(obj, nengo.Ensemble):
            model2.ensembles.append(obj)
        elif isinstance(obj, nengo.Node):
            model2.nodes.append(obj)
    for conn in conns:
        model2.connections.append(conn)  
    return model2
