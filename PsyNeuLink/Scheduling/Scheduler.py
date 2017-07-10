# Princeton University licenses this file to You under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.  You may obtain a copy of the License at:
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.


# ********************************************* Scheduler ***************************************************************

"""

Overview
--------

A Scheduler is used to generate an order in which the `Mechanisms <Mechanism>`s of a `System` are to be executed.
By default, Mechanisms are executed in the order in which they are specified in the `Processes <System.processes>`
of the System, with each Mechanism executed once per `round of execution <Run_TRIAL>`.  A Scheduler can be used to
implement more sophisticated patterns of execution, by specifying `Conditions <Condition>` that determine when and
COMMENT:
  (`ConditionSet`)  [<- **??REFERENCE HERE OR INTRODUCE BELOW?]
COMMENT
how many times individual Mechanisms execute, and whether and how this depends on the execution of others.  Conditions
can be combined in arbitrary ways to generate any pattern of execution that is logically possible.

.. _Scheduler_Creation:

Creating a Scheduler
--------------------

A Scheduler is created either explicitly, or automatically by a `System`. When creating a Scheduler explicitly,
the set of `Mechanisms <Mechanism>` to be executed and their order must be specified in one of the following
ways in the Scheduler's constructor:

COMMENT:
    [** IS A GRAPH ENOUGH, OR DOES THE TOPOSORT ALSO HAVE TO BE SPECIFIED (SEEMS UNNECESSARY SINCE IT CAN BE
        CREATED FROM A DIRECTED ACYCLIC GRAPH - NOTE THAT CIRCULAR GRAPHS CAN BE HANLDED BY COMPOSITIONS]
COMMENT

COMMENT:
    [** NOT SURE WHAT WAS MEANT BY THIS:
     (this can be generated by submitting a dictionary of Mechanism dependencies to the `toposort <LINK>` module;
     WHICH MODULE?  THE IMPORTED ONE?
COMMENT

* a `System` or a **graph specification dictionary** in the **system** argument - if a System is specified,
  the schedule is created using the Mechanisms in the System's `executionList <System.exeuctionList>` and the order
  specified in its `executionGraph <System.executionGraph>`.  If graph specification dictionary is used,  it must
  describe a directed acyclic graph of `Mechanisms <Mechanism>`, in which the key for each entry is a Mechanism and
  the value is a set specifying the Mechanisms that project directly to the one in the key;  an error is generated if
  any cycles (e.g., recurrent `Projections <Projections>`) are detected.
COMMENT:
     ??**DOES SCHEDULER HANDLE CREATING THE GRAPH IF A THE DEPENDENCY DICT IS USED?
COMMENT

* a **list of Mechanisms** in the **nodes** argument - the list must acyclic; as with a
  graph specification dictionary, an error is generated if any cycles (e.g., recurrent `Projections <Projections>`)
  are detected.  If the **nodes** argument is used, then a topologically sorted list of the Mechanisms must be
  provided in the **toposort_ordering** argument
COMMENT:
     ??**WHY IS THE TOPOSORT OREDERING REQUIRED IF THE nodes ARGUMENT IS USED?
     **CONSIDER CHANGING nodes TO mechanisms
 COMMENT

In addition, a `ConditionSet` may be specified, by assigning one to the **condition_set** argument of the constructor.
A ConditionSet is simply a list of `Conditions <Condition>`.  These will be added to the list generated from the
`System` or graph specified in the **system** argument, or the list specified in the **toposort_ordering** argument.
The Conditions will be added to the ones derived from the `System`, graph, or list specified in the **system** or
**toposort_ordering** arguments, with any conflicts resolved in favor of the ConditionSet. ConditionSets can also
be added after a Scheduler has been created, using its `add_condition` and `add_condition_set` methods.
If both a System and a set of nodes are specified, the Scheduler will initialize based on the System.

.. _Scheduler_Algorithm:

Algorithm
---------

COMMENT:
    [** DEFINE consideration_set]
A Scheduler first constructs a `consideration_queue` of its Mechanisms using the topological ordering. A
`consideration_queue` consists of a list of `consideration_sets <consideration_set>` of Mechanisms grouped based on
the dependencies among them specified by the graph. The first `consider_set` consists of only `ORIGIN` Mechanisms.
The second consists of all Mechanisms that receive `Projections <Projection>` from Mechanisms in the first
`consideration_set`. The third consists of Mechanisms that receive Projections from Mechanisms in the first two
`consideration_sets <consideration_set>`, and so forth.  When executing, the Scheduler maintains a record
of the number of times its Mechanisms have been assigned to execute, and the total number of `time_steps <time_step>`
that have occurred in each `TimeScale`. This information is used by `Conditions`.
COMMENT:
    [**??HOW IS IT USED BY Conditions?]
                                                                                   The Scheduler evaluates the
`consider_sets <consideration_set>` in their order in the `consideration_queue`, and determines which Mechanisms in
each are allowed to run based on whether their associated Conditions have been met; all Mechanisms within a
`consideration_set` that are allowed to run comprise a `time_step`<TimeScale.TIME_STEP>. These Mechanisms are
considered for simultaneous execution, and so the execution of a Mechanism within a `time_step` may trigger the
execution of another Mechanism within its `consideration_set`.
COMMENT:
    [**??ISN'T THE ABOVE PROBLEMATIC??]
The ordering of these Mechanisms is irrelevant, as there are no "parent-child" dependencies among Mechanisms within
the same `consideration_set`. A key feature is that all parents have the chance to execute (even if they do not
actually execute) before their children.  At the beginning of each `timestep`, the Scheduler evaluates whether the
specified termination conditions have been met, and terminates if so.

.. _Scheduler_Execution:

Execution
---------

COMMENT:
    [** ??DOES 'Always` MEAN IT RUNS ONCE AND ONLY ONCE PER ROUND OF EXECUTION??]
    [** NEED TO DEFINE `time_step` AND `round of execution`]
    [** CONDITION NAMES SHOULD PROBABLY USE UNDERSCORE NOTATION OR, AT LEAST INITIAL LOWER CASE CAMEL CASE]
COMMENT
When the Scheduler is executed with its `run <Scheduler.run>` method, it creates a generator that specifies the
ordering in which the `Mechanisms` specified should be executed to meet the conditions specified in its
`condition_set`. Any Mechanisms that do not have a `Condition` explicitly specified are assigned the Condition
`Always`, that allows it to execute any time it is under consideration.  If no `Termination` Conditions are
specified, the Scheduler terminates a round of execution when all of the Mechanisms have been specified for execution
at least once (corresponding to the `AllHaveRun` Condition.  Each iteration of the `run <Scheduler.run>` method
generates the executions for a `time_step`, which constitutes the set of Mechanisms that are currently eligible for
execution and that do not have any dependencies on one another;  the order of execution of Mechanisms within a
time_step is not defined (and should not matter since, by definition, there are no dependencies).


Examples
--------

Please see `Condition` for a list of all supported Conditions and their behavior.

*Basic phasing in a linear process:*
    A = TransferMechanism(function = Linear(), name = 'A')
    B = TransferMechanism(function = Linear(), name = 'B')
    C = TransferMechanism(function = Linear(), name = 'C')

    p = process(
        pathway=[A, B, C],
        name = 'p',
    )
    s = system(
        processes=[p],
        name='s',
    )
    sched = Scheduler(system=s)

    #impicit condition of Always for A

    sched.add_condition(B, EveryNCalls(A, 2))
    sched.add_condition(C, EveryNCalls(B, 3))

    # implicit AllHaveRun condition
    output = list(sched.run())

    # output will produce
    # [A, A, B, A, A, B, A, A, B, C]

*Alternate basic phasing in a linear process:*
    A = TransferMechanism(function = Linear(), name = 'A')
    B = TransferMechanism(function = Linear(), name = 'B')

    p = process(
        pathway=[A, B],
        name = 'p',
    )
    s = system(
        processes=[p],
        name='s',
    )
    sched = Scheduler(system=s)

    sched.add_condition(A, Any(AtPass(0), EveryNCalls(B, 2)))
    sched.add_condition(B, Any(EveryNCalls(A, 1), EveryNCalls(B, 1)))

    termination_conds = {ts: None for ts in TimeScale}
    termination_conds[TimeScale.TRIAL] = AfterNCalls(B, 4, time_scale=TimeScale.TRIAL)
    output = list(sched.run(termination_conds=termination_conds))

    # output will produce
    # [A, B, B, A, B, B]

*Basic phasing in two processes:*
    A = TransferMechanism(function = Linear(), name = 'A')
    B = TransferMechanism(function = Linear(), name = 'B')
    C = TransferMechanism(function = Linear(), name = 'C')

    p = process(
        pathway=[A, C],
        name = 'p',
    )
    q = process(
        pathway=[B, C],
        name = 'q',
    )
    s = system(
        processes=[p, q],
        name='s',
    )
    sched = Scheduler(system=s)

    sched.add_condition(A, EveryNPasses(1))
    sched.add_condition(B, EveryNCalls(A, 2))
    sched.add_condition(C, Any(AfterNCalls(A, 3), AfterNCalls(B, 3)))

    termination_conds = {ts: None for ts in TimeScale}
    termination_conds[TimeScale.TRIAL] = AfterNCalls(C, 4, time_scale=TimeScale.TRIAL)
    output = list(sched.run(termination_conds=termination_conds))

    # output will produce
    # [A, set([A,B]), A, C, set([A,B]), C, A, C, set([A,B]), C]

"""

import logging

from toposort import toposort

from PsyNeuLink.Globals.TimeScale import TimeScale
from PsyNeuLink.Scheduling.Condition import AllHaveRun, Always, ConditionSet, Never

logger = logging.getLogger(__name__)


class SchedulerError(Exception):

    def __init__(self, error_value):
        self.error_value = error_value

    def __str__(self):
        return repr(self.error_value)


class Scheduler(object):
    """
        Used to generate the order in which `Mechanisms <Mechanism>` are executed, using a set of arbitrary
        `Conditions <Condition>` (`ConditionSet`<ConditionSet>).

        Arguments
        ---------

        system : System
            specifies the Mechanisms to be ordered for execution, and any dependencies among them, based on the
            Sysytem's `executionGraph <System.executionGraph>` and `executionList <System.executionList>`.

        COMMENT:
            [**??IS THE FOLLOWING CORRECT]:
        condition  : ConditionSet
            set of `Conditions <Condition>` that specify when individual Mechanisms in **system**
            execute and any dependencies among them, that complements any that are implicit in the System,
            and supercede those where they are in conflict.

        nodes : List[Mechanism]
            list of Mechanisms to be ordered for execution;  must be paired with a specification of the **toposort**
            argument which is used to determine the order of execution.

        toposort : **??list?? dict??
            topological ordering of Mechanisms, **??FORMAT?  DEPENDENCY DICT?

        Attributes
        ----------

        condition_set : ConditionSet
            the set of Conditions this Scheduler will use when running

        execution_list : list
            the full history of time steps this scheduler has produced

        consideration_queue: list
            a list form of the scheduler's toposort ordering of its nodes

        termination_conds : Dict[TimeScale:Condition]
            a mapping from :keyword:`TimeScale`s to :keyword:`Condition`s that when met
            terminate the execution of the specified :keyword:`TimeScale`
    """
    def __init__(
        self,
        composition=None,
        graph=None,
        condition_set=None,
        nodes=None,
        toposort_ordering=None,
        termination_conds=None,
    ):
        '''
        :param self:
        :param composition: (Composition) - the Composition this scheduler is scheduling for
        :param condition_set: (ConditionSet) - a :keyword:`ConditionSet` to be scheduled
        '''
        self.condition_set = condition_set if condition_set is not None else ConditionSet(scheduler=self)
        # stores the in order list of self.run's yielded outputs
        self.execution_list = []
        self.consideration_queue = []
        self.termination_conds = {
            TimeScale.RUN: Never(),
            TimeScale.TRIAL: AllHaveRun(),
        }
        self.update_termination_conditions(termination_conds)

        if composition is not None:
            self.nodes = [vert.component for vert in composition.graph_processing.vertices]
            self._init_consideration_queue_from_graph(composition.graph_processing)
        elif graph is not None:
            self.nodes = [vert.component for vert in graph.vertices]
            self._init_consideration_queue_from_graph(graph)
        elif nodes is not None:
            self.nodes = nodes
            if toposort_ordering is None:
                raise SchedulerError('Instantiating Scheduler by list of nodes requires a toposort ordering (kwarg toposort_ordering)')
            self.consideration_queue = list(toposort_ordering)
        else:
            raise SchedulerError('Must instantiate a Scheduler with either a Composition (kwarg composition) [defaulting to its processing graph, Graph (kwarg graph), or a list of Mechanisms (kwarg nodes) and and a toposort ordering over them (kwarg toposort_ordering)')

        self._init_counts()

    # the consideration queue is the ordered list of sets of nodes in the graph, by the
    # order in which they should be checked to ensure that all parents have a chance to run before their children
    def _init_consideration_queue_from_graph(self, graph):
        dependencies = {}
        for vert in graph.vertices:
            dependencies[vert.component] = set()
            for parent in graph.get_parents_from_component(vert.component):
                dependencies[vert.component].add(parent.component)

        self.consideration_queue = list(toposort(dependencies))
        logger.debug('Consideration queue: {0}'.format(self.consideration_queue))

    def _init_counts(self):
        # self.times[p][q] stores the number of TimeScale q ticks that have happened in the current TimeScale p
        self.times = {ts: {ts: 0 for ts in TimeScale} for ts in TimeScale}
        # stores total the number of occurrences of a node through the time scale
        # i.e. the number of times node has ran/been queued to run in a trial
        self.counts_total = {ts: None for ts in TimeScale}
        # counts_useable is a dictionary intended to store the number of available "instances" of a certain node that
        # are available to expend in order to satisfy conditions such as "run B every two times A runs"
        # specifically, counts_useable[a][b] = n indicates that there are n uses of a that are available for b to expend
        # so, in the previous example B would check to see if counts_useable[A][B] is 2, in which case B can run
        self.counts_useable = {node: {n: 0 for n in self.nodes} for node in self.nodes}

        for ts in TimeScale:
            self.counts_total[ts] = {n: 0 for n in self.nodes}

    def _reset_counts_total(self, time_scale):
        for ts in TimeScale:
            # only reset the values underneath the current scope
            # this works because the enum is set so that higher granularities of time have lower values
            if ts.value <= time_scale.value:
                for c in self.counts_total[ts]:
                    logger.debug('resetting counts_total[{0}][{1}] to 0'.format(ts, c))
                    self.counts_total[ts][c] = 0

    def _increment_time(self, time_scale):
        for ts in TimeScale:
            self.times[ts][time_scale] += 1

    def _reset_time(self, time_scale):
        for ts_scope in TimeScale:
            # reset all the times for the time scale scope up to time_scale
            # this works because the enum is set so that higher granularities of time have lower values
            if ts_scope.value <= time_scale.value:
                for ts_count in TimeScale:
                    self.times[ts_scope][ts_count] = 0

    def update_termination_conditions(self, termination_conds):
        if termination_conds is not None:
            logger.info('Specified termination_conds {0} overriding {1}'.format(termination_conds, self.termination_conds))
            self.termination_conds.update(termination_conds)

        for ts in self.termination_conds:
            self.termination_conds[ts].scheduler = self

    ################################################################################
    # Wrapper methods
    #   to allow the user to ignore the ConditionSet internals
    ################################################################################
    def __contains__(self, item):
        return self.condition_set.__contains__(item)

    def add_condition(self, owner, condition):
        '''
        :param: self:
        :param owner: the :keyword:`Component` that is dependent on the :param conditions:
        :param conditions: a :keyword:`Condition` (including All or Any)
        '''
        self.condition_set.add_condition(owner, condition)

    def add_condition_set(self, conditions):
        '''
        :param: self:
        :param conditions: a :keyword:`dict` mapping :keyword:`Component`s to :keyword:`Condition`s,
               can be added later with :keyword:`add_condition`
        '''
        self.condition_set.add_condition_set(conditions)

    ################################################################################
    # Validation methods
    #   to provide the user with info if they do something odd
    ################################################################################
    def _validate_run_state(self):
        self._validate_condition_set()

    def _validate_condition_set(self):
        unspecified_nodes = []
        for node in self.nodes:
            if node not in self.condition_set:
                self.condition_set.add_condition(node, Always())
                unspecified_nodes.append(node)
        if len(unspecified_nodes) > 0:
            logger.info('These nodes have no Conditions specified, and will be scheduled with condition Always: {0}'.format(unspecified_nodes))

    ################################################################################
    # Run methods
    ################################################################################

    def run(self, termination_conds=None):
        '''
        :param self:
        :param termination_conds: (dict) - a mapping from :keyword:`TimeScale`s to :keyword:`Condition`s that when met terminate the execution of the specified :keyword:`TimeScale`
        '''
        self._validate_run_state()
        self.update_termination_conditions(termination_conds)

        self.counts_useable = {node: {n: 0 for n in self.nodes} for node in self.nodes}
        self._reset_counts_total(TimeScale.TRIAL)
        self._reset_time(TimeScale.TRIAL)
        self._num_passes = 0

        while not self.termination_conds[TimeScale.TRIAL].is_satisfied() and not self.termination_conds[TimeScale.RUN].is_satisfied():
            self._reset_counts_total(TimeScale.PASS)
            self._reset_time(TimeScale.PASS)

            execution_list_has_changed = False
            cur_index_consideration_queue = 0

            while (
                cur_index_consideration_queue < len(self.consideration_queue)
                and not self.termination_conds[TimeScale.TRIAL].is_satisfied()
                and not self.termination_conds[TimeScale.RUN].is_satisfied()
            ):
                # all nodes to be added during this time step
                cur_time_step_exec = set()
                # the current "layer/group" of nodes that MIGHT be added during this time step
                cur_consideration_set = self.consideration_queue[cur_index_consideration_queue]
                try:
                    iter(cur_consideration_set)
                except TypeError as e:
                    raise SchedulerError('cur_consideration_set is not iterable, did you ensure that this Scheduler was instantiated with an actual toposort output for param toposort_ordering? err: {0}'.format(e))
                logger.debug('trial, num passes in trial {0}, consideration_queue {1}'.format(self.times[TimeScale.TRIAL][TimeScale.PASS], ' '.join([str(x) for x in cur_consideration_set])))

                # do-while, on cur_consideration_set_has_changed
                # we check whether each node in the current consideration set is allowed to run,
                # and nodes can cause cascading adds within this set
                while True:
                    cur_consideration_set_has_changed = False
                    for current_node in cur_consideration_set:
                        logger.debug('cur time_step exec: {0}'.format(cur_time_step_exec))
                        for n in self.counts_useable:
                            logger.debug('Counts of {0} useable by'.format(n))
                            for n2 in self.counts_useable[n]:
                                logger.debug('\t{0}: {1}'.format(n2, self.counts_useable[n][n2]))

                        # only add each node once during a single time step, this also serves
                        # to prevent infinitely cascading adds
                        if current_node not in cur_time_step_exec:
                            if self.condition_set.conditions[current_node].is_satisfied():
                                logger.debug('adding {0} to execution list'.format(current_node))
                                logger.debug('cur time_step exec pre add: {0}'.format(cur_time_step_exec))
                                cur_time_step_exec.add(current_node)
                                logger.debug('cur time_step exec post add: {0}'.format(cur_time_step_exec))
                                execution_list_has_changed = True
                                cur_consideration_set_has_changed = True

                                for ts in TimeScale:
                                    self.counts_total[ts][current_node] += 1
                                # current_node's node is added to the execution queue, so we now need to
                                # reset all of the counts useable by current_node's node to 0
                                for n in self.counts_useable:
                                    self.counts_useable[n][current_node] = 0
                                # and increment all of the counts of current_node's node useable by other
                                # nodes by 1
                                for n in self.counts_useable:
                                    self.counts_useable[current_node][n] += 1
                    # do-while condition
                    if not cur_consideration_set_has_changed:
                        break

                # add a new time step at each step in a pass, if the time step would not be empty
                if len(cur_time_step_exec) >= 1:
                    self.execution_list.append(cur_time_step_exec)
                    yield self.execution_list[-1]

                    self._increment_time(TimeScale.TIME_STEP)

                cur_index_consideration_queue += 1

            # if an entire pass occurs with nothing running, add an empty time step
            if not execution_list_has_changed:
                self.execution_list.append(set())

                yield self.execution_list[-1]

                self._increment_time(TimeScale.TIME_STEP)

            # can execute the execution_list here
            logger.info(self.execution_list)
            logger.debug('Execution list: [{0}]'.format(' '.join([str(x) for x in self.execution_list])))
            self._increment_time(TimeScale.PASS)

        self._increment_time(TimeScale.TRIAL)

        return self.execution_list
