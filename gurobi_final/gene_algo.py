""" This class represents a Gene in the genetic algorithm.
    Which would return the sequence of the gene with best permutation
"""

class Gene:
    def __init__(self, gene_id, value):
        self.gene_id = gene_id
        self.value = value

    def __repr__(self):
        return f"Gene(id={self.gene_id}, value={self.value})"

    def __eq__(self, other):
        if not isinstance(other, Gene):
            return False
        return self.gene_id == other.gene_id and self.value == other.value

    def __hash__(self):
        return hash((self.gene_id, self.value))