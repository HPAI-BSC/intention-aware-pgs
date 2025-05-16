from eval.graph import PolicyGraphAndTrajectories


class NodePairList:
    def __init__(self):
        self.node_pair_list = set()

    def populate_with_shared_descendants(self, PG: PolicyGraphAndTrajectories):
        pass

    def is_empty(self):
        return len(self.node_pair_list) == 0

    def pop(self):
        return self.node_pair_list.pop()

    def remove_nodes(self, node_pair):
        node_A, node_B = node_pair
        self.node_pair_list = {(a, b) for a, b in self.node_pair_list if not {a, b}.intersection({nodeA, nodeB})}


def graph_collapse(policy_graph: PolicyGraphAndTrajectories, i_loss_threshold: float):
    PG = policy_graph.copy()
    PG.compute_node_probability()
    pending_node_pairs = NodePairList()
    pending_node_pairs.populate_with_shared_descendants(PG)
    while not pending_node_pairs.is_empty():
        node_pair = pending_node_pairs.pop()
        information_loss = PG.compute_information_loss(node_pair)
        if information_loss <= i_loss_threshold:
            new_node = PG.collapse(node_pair)
            pending_node_pairs.remove_nodes(node_pair)
            pending_node_pairs.repopulate_with_new_node(PG, new_node)


"""
XX Compute Probability of each node as frequency of appearing in a trace
XX Let K be the set of things to 'check' be for any N state, each pair of nodes (A,B) that incide into N without repetition
while K is non-empty
	for each pair of nodes (A,B) in K
		Compute the reverse of the Information function:
			Call X the attempt at unifying A&B, and At the set AUB\(A∩B) [ie differing attributes]
			Decision trees, information gain is: G(X,At,C)= I(X,C) − E(X,At,C) = I(X,C) - sum{v in At} #[At=v]/#X * I([At=v],C)
				Insights: P(s=A) is going to be the same scaler as #[At=v]/#X. What will be I([At=v],C) ? 
			Now instead, compute INFORMATION LOSS, as the information we lose when merging 2 nodes with different attributes At (ie information lost when not distinguishing At), A being the diverging representation of the node
				L(X,A,C) =  E(X,A,C) - I(X,C)
				What exactly are these? 
				Merging information should account for: difference in P(s', a | s=A) and P(s', a | s=B); but also P(s=A) & P(s=B). 
				Improbable states should tend to be merged intuitively. Derive formula backward from these?
				I(X,C) should be the information S=X
		if information Loss < threshold:
			let X be a new state with attributes (A∩B)
			let P(s=X) = P(s=A) + P(s=B)
			let X outsiding connections be created as so:
				P(s', a | s=X) = P(s', a, s=X)/P(s=X) = [P(s',a|s=A)*P(A) + P(s',a|s=B)*P(B)]/P(s=X)
					can also be interpreted as P(s',a|s=M) weighted by how much of s=M is in s=X
			forall Y in inciding nodes of A:
				forall action a which makes Y incide into A:
					if Y incides in B with action a too:
						create an edge with action a with P(s'=X, a=a|s=Y) = P(s'=A, a=a|s=Y) + P(s'=B, a=a|s=Y)
						delete previous edge from Y to B with action a
						delete previous edge from Y to A with action a
					else:
						move the destination of edge from Y to A with action a so that it points Y to X with action a.
			forall Y in inciding nodes of B:
				forall action a which makes Y incide into B:
					move the destination of edge from Y to B with action a so that it points Y to X with action a.
			delete all pairs which contain A or B from the set of things to check K
			add all pairs of nodes incinding into the new X into K
			For all N which X incides into, forall node M which also incides into N, add all (X, M) to K
			delete A
			delete B
		else:
			delete (A,B) from K
"""
