class Vertex(object):
    def __init__(self, internal_vertices, num_inputs, num_outputs, equiv=None):
        self.vertices = internal_vertices
        self.equiv = equiv if equiv is not None else []
        self.old_input_values = None
        self.input_values = [None] * num_inputs
        self.output_values = [None] * num_outputs

    def compute(self, init=False):
        """ Returns whether the output changed."""
        new_inputs = self.input_values
        changed_output = False
        if new_inputs != self.old_input_values:
            self.old_input_values = self.input_values[:]
            changed = []
            for i in range(len(self.input_values)):
                for name, _, j in self.equiv[(None, 'in', i)]:
                    self.vertices[name].input_values[j] = self.old_input_values[i]
                    changed.append((name, 'in', j))
            for name, _, _ in changed:
                if name is None:
                    continue
                elem = self.vertices[name]
                if elem.compute(init) or init:
                    for i, _ in enumerate(elem.output_values):
                        if (name, 'out', i) in self.equiv:
                            # import pdb; pdb.set_trace()
                            for out, _, j in self.equiv[(name, 'out', i)]:
                                if out is None:
                                    changed_output = True
                                    self.output_values[j] = elem.output_values[i]
                                else:
                                    self.vertices[out].input_values[j] = elem.output_values[i]
                            changed.extend(self.equiv[(name, 'out', i)])
        return changed_output

    def copy(self):
        vertices = {k:v.copy() for k, v in self.vertices.items()}
        return Vertex(vertices, len(self.input_values), len(self.output_values),
                      self.equiv)

    def __call__(self, *input_values):
        self.input_values = input_values
        self.compute()
        return self.output_values

    def size(self):
        return sum(vertex.size() for vertex in self.vertices.values())

class FuncVertex(Vertex):
    def __init__(self, func, num_inputs=2, num_outputs=1, default=None):
        self.vertices = {}
        self.old_input_values = None
        self.input_values = [False] * num_inputs
        self.default = default
        self.output_values = [default] * num_outputs
        self.changed = True
        self.func = func

    def compute(self, init=False):
        # print "Recomputing func", self.func, self.input_values
        new_inputs = self.input_values
        if new_inputs != self.old_input_values or init:
            if self.input_values is None or self.input_values == [None]:
                self.old_input_values = self.default
            else:
                self.old_input_values = self.input_values[:]
            self.output_values = self.func(self.old_input_values)
            return True
        return False

    def copy(self):
        return FuncVertex(self.func,
                          len(self.input_values),
                          len(self.output_values),
                          self.default)

    def size(self):
        return 1

def nand(input_values):
    return [not(input_values[0] and input_values[1])]
