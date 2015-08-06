import nengo
import numpy as np

def ens_cascade_out(model, limit, synapse=0.005):
    inputs, outputs = nengo.utils.builder.find_all_io(model.connections)
    changed = False
    for obj, output_conns in outputs.items():
        if len(output_conns) > limit:
            if isinstance(obj, nengo.Ensemble):
                changed = True

                functions = {}
                for c in output_conns:
                    if c.function not in functions:
                        functions[c.function] = [c]
                    else:
                        functions[c.function].append(c)

                for func, conns in functions.items():
                    count = int(np.ceil(len(conns) / float(limit)))
                    ensembles = []
                    with model:
                        for i in range(count):
                            ens = nengo.Ensemble(n_neurons=obj.n_neurons,
                                                 dimensions=obj.dimensions,
                                                 radius=obj.radius,
                                                 encoders=obj.encoders,
                                                 intercepts=obj.intercepts,
                                                 max_rates=obj.max_rates,
                                                 eval_points=obj.eval_points,
                                                 n_eval_points=obj.n_eval_points,
                                                 neuron_type=obj.neuron_type,
                                                 seed=obj.seed
                                                 )
                            ensembles.append(ens)
                            nengo.Connection(obj, ens, synapse=synapse)
                        for i, c in enumerate(conns):
                            index = i % count
                            nengo.Connection(ensembles[index][c.pre_slice], c.post,
                                    transform=c.transform, function=c.function,
                                    synapse=c.synapse, eval_points=c.eval_points,
                                    scale_eval_points=c.scale_eval_points,
                                    solver=c.solver)
                            model.connections.remove(c)

    if changed:
        return ens_cascade_out(model, limit=limit)
    else:
        return model
