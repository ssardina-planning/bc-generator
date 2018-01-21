from bc.generators.base import Generator
import networkx as nx
import random
import sys


class Class_B_Generator(Generator):
    def __init__(self, n, l, p, m, k, seed):
        Generator.__init__(self)
        self.num_behaviors = n
        self.num_actions = m
        self.num_acts_per_beh = l
        self.prob_failure = p
        assert self.num_actions > self.num_acts_per_beh
        self.num_target_seqs = k
        self.problem_name = 'class-B-%d-%d-%d-%d-%d-%d' % (seed, n, l, p * 100, m, k)
        self.output_folder = 'class-B-%d/%d-%d-%d-%d-%d' % (seed, n, l, p * 100, m, k)
        self.setup()

    def generate_beh_graphs(self):
        self.beh_graphs = []
        for i in range(self.num_behaviors):
            b = nx.MultiDiGraph(name='beh_%d' % i)
            for j in range(self.num_acts_per_beh):
                b.add_node(j)
            for j in range(self.num_acts_per_beh - 1):
                b.add_edge(j, j + 1)
            b.add_edge(self.num_acts_per_beh - 1, 0)
            behavior_actions = random.sample(range(0, self.num_actions), self.num_acts_per_beh)
            random.shuffle(behavior_actions)
            for e, action in zip(b.edges(data=True), behavior_actions):
                e[2]['label'] = action
            state_idx = len(b.nodes())
            for n in b.nodes():
                for e in b.edges([n], data=True):
                    if random.random() <= self.prob_failure:
                        act = e[2]['label']
                        b.add_node(state_idx)
                        b.add_edge(n, state_idx, label=act)
                        state_idx += 1
            self.beh_graphs.append(b)

    def generate_target_request_sequences(self):
        seqs = []
        prefixes = range(self.num_actions)
        if self.num_target_seqs > self.num_actions:
            print >> sys.stderr, "|A| < # of plans in target!"

        while len(prefixes) > 0 and len(seqs) < self.num_target_seqs:
            a0 = random.choice(prefixes)
            prefixes.remove(a0)
            done = False
            while not done:
                actions = range(0, self.num_actions)
                actions.remove(a0)
                random.shuffle(actions)
                seq = [a0] + actions
                if seq not in seqs:
                    done = True
                    seqs.append(seq)
        return seqs

    def generate_target_graph(self):
        self.tgt_graph = nx.MultiDiGraph(name='target')
        target_requests = self.generate_target_request_sequences()
        print >> sys.stdout, len(target_requests), "generated"
        if len(target_requests) == 0:
            print >> sys.stdout, "Check parameters: no target requests were generated!"
        self.tgt_graph.add_node(0)
        next_state = 1
        for seq in target_requests:
            self.tgt_graph.add_node(next_state)
            self.tgt_graph.add_edge(0, next_state, label=seq[0])
            for i in range(1, len(seq) - 1):
                next_state += 1
                self.tgt_graph.add_node(next_state)
                self.tgt_graph.add_edge(next_state - 1, next_state, label=seq[i])
            self.tgt_graph.add_edge(next_state, 0, label=seq[len(seq) - 1])
            next_state += 1
