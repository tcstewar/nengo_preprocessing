import nengo
import numpy as np

def cascade_out(model, limit):
    inputs, outputs = nengo.utils.builder.find_all_io(model.connections)
    changed = False
    for obj, output_conns in outputs.items():
        if len(output_conns) > limit:
            changed = True

            functions = {}
            sizes = {}
            for c in output_conns:
                if c.function not in functions:
                    functions[c.function] = [c]
                    sizes[c.function] = c.size_mid
                else:
                    functions[c.function].append(c)

            for func, conns in functions.items():
                count = int(np.ceil(len(conns) / float(limit)))
                nodes = []
                with model:
                    for i in range(count):
                        node = nengo.Node(None, size_in=sizes[func])
                        nodes.append(node)
                        nengo.Connection(obj, node, synapse=None, function=func)
                    for i, c in enumerate(conns):
                        index = i % count
                        nengo.Connection(nodes[index][c.pre_slice], c.post,
                                transform=c.transform, function=None,
                                synapse=c.synapse, eval_points=c.eval_points,
                                scale_eval_points=c.scale_eval_points,
                                solver=c.solver)
                        model.connections.remove(c)
                

    if changed:
        return cascade_out(model, limit=limit)
    else:
        return model

def cascade_in(model, limit):
    inputs, outputs = nengo.utils.builder.find_all_io(model.connections)
    changed = False
    for obj, input_conns in inputs.items():
        if len(input_conns) > limit:
            changed = True

            count = int(np.ceil(len(input_conns) / float(limit)))
            nodes = []
            with model:
                for i in range(count):
                    node = nengo.Node(None, size_in=obj.size_in)
                    nodes.append(node)
                    nengo.Connection(node, obj, synapse=None)
                for i, c in enumerate(input_conns):
                    index = i % count
                    nengo.Connection(c.pre, nodes[index][c.post_slice],
                            transform=c.transform, function=c.function,
                            synapse=c.synapse, eval_points=c.eval_points,
                            scale_eval_points=c.scale_eval_points,
                            solver=c.solver)
                    model.connections.remove(c)
                
    if changed:
        return cascade_in(model, limit=limit)
    else:
        return model
