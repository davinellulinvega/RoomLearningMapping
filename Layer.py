#!/usr/bin/python
__author__ = 'davinellulinvega'

# Import the required packages
import Synapse
import Neuron


# Define the Layer class
class Layer:
    """The basic collection of computing unit in the neural network"""

    def __init__(self, nb_neuron, prev_layer=None):
        """Define the attributes and initialize their value"""

        # A list of all the neurons in the layer
        self.neurons = []

        # Create nb_neuron new neurons
        while nb_neuron > 0:
            # Create the neuron
            tmp_neuron = Neuron.Neuron()
            # Add the neuron to the layer's list
            self.neurons.append(tmp_neuron)
            # Decrease the number of neuron
            nb_neuron -= 1

            # Check if the previous layer exist
        if not (prev_layer is None) and isinstance(prev_layer, Layer):
            # For each neuron in the layer
            for tmp_neuron in self.neurons:
                # For each neuron in the previous layer
                for prev_neuron in prev_layer.neurons:
                    # Create a synapse
                    tmp_syn = Synapse.Synapse(prev_neuron, tmp_neuron)
                    # Add the synapse in the out list
                    prev_neuron.add_out_syn(tmp_syn)
                    # Add the synapse in the in list
                    tmp_neuron.add_in_syn(tmp_syn)

    def update_weight(self, learn_rate):
        """Define the procedure to update the weights of all incoming synapses"""

        # For each neuron in the layer
        for neuron in self.neurons:
            # Ask the neuron to update the incoming synaptic weight
            neuron.update_weight(learn_rate)

    def update_error(self, error=None):
        """Define the procedure to update the weights of all neurons in the layer"""

        # For each neuron in the layer
        if error is None:
            for index, neuron in enumerate(self.neurons):
                # Ask the neuron to update its error
                neuron.update_error()
        else:
            for index, neuron in enumerate(self.neurons):
                # Ask the neuron to update its error
                neuron.update_error(error[index])

    def activate(self):
        """Define the procedure to activate all neurons in the layer"""

        # For each neuron in the layer
        for neuron in self.neurons:
            # Ask the neuron to activate
            neuron.activate()
