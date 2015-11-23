#!/usr/bin/python
__author__ = 'davinellulinvega'

# Import the required packages
from math import tanh
import Synapse


# Declare the class Neuron
class Neuron:
    """The basic computing unit on the neural network"""

    def __init__(self):
        """Define the attributes and initialize the neuron"""

        self.output = 0
        self.in_syn = []
        self.out_syn = []
        self.error = 0

    def add_in_syn(self, synapse):
        """Define the operations to be executed when adding an input synapse"""

        # Check if the synapse is an instance of Synapse
        if not (isinstance(synapse, Synapse.Synapse)):
            # If not raise an error
            raise TypeError("Only synapses can link neurons")
        else:
            # Else add the synapse to the in_syn list
            self.in_syn.append(synapse)

    def add_out_syn(self, synapse):
        """Define the operations to be executed when adding an ouput synapse"""

        # Check if the synapse is an instance of Synapse
        if not (isinstance(synapse, Synapse.Synapse)):
            # If not raise an error
            raise TypeError("Only synapses can link neurons")
        else:
            # Else add the synapse to the out_syn list
            self.out_syn.append(synapse)

    def update_error(self, error=None):
        """Define the procedure to update the error on the output"""

        # If no error is provided
        if error is None:
            sum_err = 0
            # For each out synapse
            for syn in self.out_syn:
                sum_err += syn.neuron_out.error * syn.weight
            # Compute the error
            self.error = sum_err * (1 - self.output ** 2)
        else:
            # Else store the error value
            self.error = error

    def update_weight(self, learn_rate):
        """Define the procedure to update the weight of the input synapses"""

        # For each input synapse
        for syn in self.in_syn:
            # Ask the synapse to update its weight
            syn.update_weight(learn_rate)
            # Normalize the synaptic weight
            # self.normalize_weight()

    def normalize_weight(self):
        """Normalize the weight, while keeping the dispersion ratio"""

        # For each input synapse
        avg = 0
        # Compute the average
        for syn in self.in_syn:
            avg += syn.weight
        avg /= len(self.in_syn)

        # For each input synapse
        var = 0
        # Compute the standard deviation
        for syn in self.in_syn:
            var += (syn.weight - avg) ** 2
        var /= len(self.in_syn)
        dev = var ** 0.5

        # For each input synapse
        for syn in self.in_syn:
            # Subtract the average
            syn.weight -= avg
            # And divide by the standard deviation
            syn.weight /= dev

    def activate(self):
        """Compute the new value of the neuron's output"""

        # Get the weighted sum of the inputs
        sum_in = 0
        for syn in self.in_syn:
            sum_in += syn.get_weighted_input()

        # Apply the activation function and assign the result to the output
        self.output = tanh(sum_in)
