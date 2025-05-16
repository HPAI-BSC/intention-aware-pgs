from eval.graph import PolicyGraphAndTrajectories, Node

import csv

from eval.utils import load_semaphor


def pg_from(domain, disc):
    transitions_file, state_file = f"policygraphs/pg_{domain}_{disc}_edges.csv", \
                                   f"policygraphs/pg_{domain}_{disc}_nodes.csv"
    state_type = "Propositional"
    x = PolicyGraphAndTrajectories()
    x.load_graph_from_files(transitions_file, state_file, state_type)
    return x


def node_partner_held_for_12(contents):
    print(contents)
    def f(n: Node):
        return n.state_rep.split('+')[1] == contents
    return f

def node_partner_loc_for13(contents):
    print(contents)
    def f(n: Node):
        return n.state_rep.split('+')[-1] == contents
    return f

def node_is_hold_nothing_for_13(n: Node):
    return n.state_rep.split('+') == 'Nothing'


def experiment1():
    global tracked_metrics
    tracked_metrics = ['Environment', 'Disc', 'H', 'H_a', 'H_w']
    with open('logs/entropy_log.csv', 'w') as f:
        w = csv.DictWriter(f, tracked_metrics)
        w.writeheader()
        for domain in ['simple', 'random0', 'unident_s']:
            results = {'Environment': domain}
            for disc in ["R1", "R2", "R3", "R4"]:
                results['Disc'] = disc
                x = pg_from(domain, disc)
                results['H'] = x.compute_entropy("global")
                results['H_a'] = x.compute_entropy("agent")
                results['H_w'] = x.compute_entropy("world")
                print(results)
                w.writerow(results)


def semaphor_test():
    p,d,s = load_semaphor('perfect'), load_semaphor('dumb'), load_semaphor('smart')
    print(s.get_action_probability(1))
    print(p.compute_entropy("world"))
    print(s.compute_entropy("world"))
    print(d.compute_entropy("world"))

if __name__ == '__main__':
    experiment1()
    tracked_metrics = ['Environment', 'DISC', 'PARAM', 'H', 'H_a', 'H_w', 'P(param)']
    """with open('logs/entropy_log_prima.csv', 'w') as f:  # You will need 'wb' mode in Python 2.x
        w = csv.DictWriter(f, tracked_metrics)
        w.writeheader()
        for domain in ['random0']:
            results = {'Environment': domain}
            disc = 12
            results['DISC'] = disc
            for possibility in ['NOTHING', 'ONION', 'DISH']:
                results['PARAM'] = possibility
                x = pg_from(domain, disc)
                if disc == 12:
                    a_func = node_partner_held_for_12(possibility)
                else:
                    raise NotImplementedError()
                _, results['H'], results['P(param)'] = x.compute_selective_entropy(a_func, "global")
                _, results['H_a'], _ = x.compute_selective_entropy(a_func, "agent")
                _, results['H_w'], _ = x.compute_selective_entropy(a_func, "world")
                w.writerow(results)
            disc = 13
            for possibility in ['NORTHWEST', 'WEST', 'SOUTHWEST']:
                results['PARAM'] = possibility
                x = pg_from(domain, disc)
                if disc == 13:
                    a_func = node_partner_loc_for13(possibility)
                else:
                    raise NotImplementedError()
                _, results['H'], results['P(param)'] = x.compute_selective_entropy(a_func, "global")
                _, results['H_a'], _ = x.compute_selective_entropy(a_func, "agent")
                _, results['H_w'], _ = x.compute_selective_entropy(a_func, "world")
                w.writerow(results)
            disc = 14
            pass"""
    # experiment1()
    # semaphor_test()
