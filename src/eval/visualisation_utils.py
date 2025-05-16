from typing import List, Tuple

import networkx as nx
from matplotlib import pyplot as plt

from eval.compute_entropies import pg_from
from eval.graph import Node
from eval.utils import load_semaphor

action_idx_to_name = {'0': 'UP', '1': 'DOWN', '2': 'RIGHT', '3': 'LEFT', '4': 'STAY', '5': 'Interact'}

def __recurrent_node_retrieval(node: Node, depth, prob_cutoff: float) -> Tuple[List, List]:  # node-id and edges
    if depth == 0:
        return ([], [])
    transitions = node.check_out_transitions()
    print(transitions)
    node_list = list()
    edge_list = []
    for action, world_trans in transitions.items():
        action_prob = 0
        for _, prob in world_trans.items():
            action_prob += prob
        if action_prob >= prob_cutoff:
            if action in {'0', '1','2','3','4','5'}: # overcooked
                node_id = node.node_id
                new_action_node = action_idx_to_name[action] + str(node.node_id)
            elif action in {'l', 'd','r','u'}: # semaphor
                node_id = node.node_id
                new_action_node = action + str(node_id)
            node_list.append((new_action_node, {'type': 'action'}))
            for new_node_id, prob in world_trans.items():
                trans_prob = prob / action_prob
                if trans_prob >= prob_cutoff:
                    new_node = node.pg.nodes[new_node_id]
                    node_list.append((new_node_id, {'type': 'state'}))
                    sub_nodes, sub_edges = __recurrent_node_retrieval(new_node, depth - 1, prob_cutoff)
                    node_list += sub_nodes
                    edge_list += sub_edges
                    edge_list.append((new_action_node, new_node_id, {'p': round(trans_prob, 2)}))
            edge_list.append((node_id, new_action_node, {'p': round(action_prob, 2)}))
    return node_list, edge_list


def plot_nodes_from_src(node: Node, depth=1, prob_cutoff: float = 0, **beautifer_args):
    """
    :param node: Starting point of exploration
    :param depth: maximum 'states' of depth to explore from node
    :param prob_cutoff: Remove action and state transitions with probability of less than it
    :param beautifer_args: Args for the plotting:
        scale_weight: larger = smaller plot / larger dots (default 10)
        edge_prob_shift: shift the label of the edges to one side or the other (default 0)
        engine: which engine to use: twopi, fruchterman, neato
        title: the plot title
    """
    G = nx.DiGraph(name="actionspace")
    nodes, edges = __recurrent_node_retrieval(node, depth=depth, prob_cutoff=prob_cutoff)
    if node.node_id not in [n for n, _ in nodes]:
        nodes.append((node.node_id, {'type': 'state'}))
    scaler = len(nodes) / beautifer_args.get('scale_weight', 10)
    fig = plt.figure(figsize=(20 * scaler, 5 * scaler))

    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    engine = beautifer_args.get('engine', 'twopi')
    if engine == 'twopi':
        pos = nx.nx_agraph.graphviz_layout(G, prog="twopi", args="")
    elif engine == 'neato':
        pos = nx.nx_agraph.graphviz_layout(G, prog="neato", args="")
    elif engine == 'fruchterman':
        pos = nx.fruchterman_reingold_layout(G)
    else:
        raise ValueError(f'Engine not understood:{engine}')

    # pos = nx.nx_agraph.graphviz_layout(G, prog="twopi", args='-Granksep="0.5 equally"')

    node_aux_transform = {node_id: props for node_id, props in nodes}
    node_color = ['red' if props['type'] == 'action' else 'blue' for props in node_aux_transform.values()]
    print(node_color)
    print(nodes)
    print(node_aux_transform)
    nx.draw_networkx(G, pos=pos, node_color=node_color, with_labels=False, node_size=600,
                     connectionstyle='arc3, rad = 0.1')
    nx.draw_networkx_labels(G, pos=pos, font_weight='bold', font_size=6)
    edge_labels = nx.get_edge_attributes(G, "p")
    title = beautifer_args.get('title', None)
    if title is not None:
        plt.title(title)
    nx.draw_networkx_edge_labels(G, pos, edge_labels, label_pos=0.2 + beautifer_args.get('edge_prob_shift', 0),
                                 font_size=5)
    fig.savefig('test.png', dpi=300, bbox_inches='tight')
    fig.show()

    print(node.state_rep)
    for node_idx, props in sorted([(k, p) for k, p in node_aux_transform.items() if p['type'] == 'state']):
        if node_idx != node.node_id:
            node_to_write: Node = node.pg.nodes[node_idx]
            print(node_idx)
            # print(node_to_write.state_rep)
            _, added, removed = node.compute_differences(node_to_write)
            print(removed, " ===>", added)
            print(node_to_write.intention)
            print()


def plot_semaphor_experiment():
    p,d,s = load_semaphor('perfect'), load_semaphor('dumb'), load_semaphor('smart')
    # plot_nodes_from_src(x.nodes[0], prob_cutoff=0.1, scale_weight=20, engine='neato', edge_prob_shift=0.2)
    # plot_nodes_from_src(x.nodes[17], depth=2, prob_cutoff=0.1, scale_weight=50, engine='neato', edge_prob_shift=0.2)
    plot_nodes_from_src(p.nodes[0], depth=2, engine='neato', scale_weight=80, edge_prob_shift=0.2, title='Perfect information')
    plot_nodes_from_src(d.nodes[0], depth=2, engine='neato', scale_weight=80, edge_prob_shift=0.2, title='(Red+Green) and Yellow discretisation')
    plot_nodes_from_src(s.nodes[0], depth=2, engine='neato', scale_weight=80, edge_prob_shift=0.2, title='(Red+Yellow) and Green discretisation')


def examine_overcooked():
    domain, disc = 'simple', '11'
    x = pg_from(domain, disc)
    # plot_nodes_from_src(x.nodes[0], prob_cutoff=0.1, scale_weight=20, engine='neato', edge_prob_shift=0.2)
    # plot_nodes_from_src(x.nodes[17], depth=2, prob_cutoff=0.1, scale_weight=50, engine='neato', edge_prob_shift=0.2)
    plot_nodes_from_src(x.nodes[17], depth=4, prob_cutoff=0.1, scale_weight=200, engine='neato', edge_prob_shift=0.2)



if __name__ == '__main__':
    # plot_semaphor_experiment()
    # examine_overcooked()
    examine_overcooked()