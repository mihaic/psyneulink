from PsyNeuLink.Globals.Keywords import *

from PsyNeuLink.Functions.Mechanisms.ProcessingMechanisms.DDM import *
from PsyNeuLink.Functions.Mechanisms.ProcessingMechanisms.Transfer import Transfer
from PsyNeuLink.Functions.Mechanisms.MonitoringMechanisms.Comparator import kwComparatorTarget
from PsyNeuLink.Functions.Projections.Mapping import Mapping
from PsyNeuLink.Functions.Projections.LearningSignal import LearningSignal
from PsyNeuLink.Functions.Process import Process_Base
from PsyNeuLink.Functions.Utility import Logistic, LinearMatrix

Input_Layer = Transfer(name='Input Layer',
                       function=Logistic(),
                       default_input_value = [0,0])

Output_Layer = Transfer(name='Output Layer',
                        function=Logistic(),
                        default_input_value = [0,0])

Learned_Weights = Mapping(name='Learned Weights',
                          sender=Input_Layer,
                          receiver=Output_Layer,

                          # DEPRECATED:
                          # function=LinearMatrix(matrix=(DEFAULT_MATRIX,LEARNING_SIGNAL))
                          # params={FUNCTION_PARAMS:{MATRIX:(IDENTITY_MATRIX,CONTROL_SIGNAL)}}
                          # params={FUNCTION_PARAMS: {MATRIX: (FULL_CONNECTIVITY_MATRIX,LEARNING_SIGNAL)}}

                          # SORT THROUGH / TRY THESE (from Multilayer:
                          # params={FUNCTION_PARAMS: {MATRIX: IDENTITY_MATRIX}}
                          # params={FUNCTION_PARAMS: {MATRIX: (IDENTITY_MATRIX,CONTROL_SIGNAL)}}
                          # params={FUNCTION_PARAMS: {MATRIX: (FULL_CONNECTIVITY_MATRIX,LEARNING_SIGNAL)}}
                          # params={FUNCTION_PARAMS: {MATRIX: (random_weight_matrix, LEARNING_SIGNAL)}}
                          # matrix=random_weight_matrix
                          # matrix=(random_weight_matrix, LEARNING_SIGNAL)
                          # matrix=(FULL_CONNECTIVITY_MATRIX, LEARNING_SIGNAL)

                          # THESE ALL WORK:
                          # matrix=(DEFAULT_MATRIX, LEARNING_SIGNAL)
                          matrix=(DEFAULT_MATRIX, LearningSignal)
                          # matrix=(DEFAULT_MATRIX, LearningSignal())
                          # params={FUNCTION_PARAMS: {MATRIX: (IDENTITY_MATRIX,LEARNING_SIGNAL)}},
                          # params={FUNCTION_PARAMS: {MATRIX: (IDENTITY_MATRIX,LearningSignal)}}
                          )

# z = Process_Base(default_input_value=[0, 0],
#                  # params={CONFIGURATION:[Input_Layer, Learned_Weights, Output_Layer]},
#                  params={CONFIGURATION:[Input_Layer, Learned_Weights, Output_Layer]},
#                  prefs={kpVerbosePref: PreferenceEntry(True, PreferenceLevel.INSTANCE)})

z = Process_Base(default_input_value=[0, 0],
                 configuration=[Input_Layer, Learned_Weights, Output_Layer],
                 prefs={kpVerbosePref: PreferenceEntry(True, PreferenceLevel.INSTANCE)})


# Learned_Weights.monitoringMechanism.target = [1,1]
# Learned_Weights.monitoringMechanism.target = [0,0]
# from PsyNeuLink.Functions.Mechanisms.MonitoringMechanisms.Comparator import kwComparatorTarget
# Learned_Weights.monitoringMechanism.paramsCurrent[kwComparatorTarget] = [1,1]

# z.execute(input=[-1, 30],
#           runtime_params={kwComparatorTarget: [1, 1]})

for i in range(10):
    z.execute([[-1, 30],[1, 1]])
    print (Learned_Weights.matrix)
