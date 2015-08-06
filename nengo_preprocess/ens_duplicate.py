import nengo
import numpy as np

# functions for reducing fanout by duplicating Ensembles
def duplicate(ens, inputs):
    # make a duplicate Ensemble with the same inputs and same parameters
    dup = nengo.Ensemble(n_neurons=ens.n_neurons, dimensions=ens.dimensions,
            intercepts=ens.intercepts, max_rates=ens.max_rates,
            radius=ens.radius, encoders=ens.encoders,
            eval_points=ens.eval_points, n_eval_points=ens.n_eval_points,
            neuron_type=ens.neuron_type, noise=ens.noise, label=ens.label)
    for c in inputs:
        nengo.Connection(c.pre, dup[c.post_slice],
            transform=c.transform, function=c.function, synapse=c.synapse,
            eval_points=c.eval_points, scale_eval_points=c.scale_eval_points,
            solver=c.solver)
    return dup

def ens_duplicate_limit_fanout(model, limit):
    inputs, outputs = nengo.utils.builder.find_all_io(model.connections)

    for obj, output_conns in outputs.items():
        n_items = int(np.ceil(len(output_conns) / float(limit)))
        if isinstance(obj, nengo.Ensemble) and n_items > 1:
            # If fanout is too big
            items = [obj]
            with model:
                # make duplicates
                for i in range(1, n_items):
                    ens = duplicate(obj, inputs[obj])
                    items.append(ens)
            
                # split the fanout connectivity among duplicates
                for i, c in enumerate(output_conns):
                    index = i % n_items
                    nengo.Connection(items[index][c.pre_slice], c.post,
                        transform=c.transform, function=c.function, 
                        synapse=c.synapse,
                        eval_points=c.eval_points, 
                        scale_eval_points=c.scale_eval_points,
                        solver=c.solver)
                    model.connections.remove(c)

    return model
