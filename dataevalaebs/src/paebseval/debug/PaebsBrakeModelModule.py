import matplotlib.pyplot as plt
import numpy as np
from scipy import integrate


class PaebsCascadePhase:
    # Class provides properties and functions to save and handle the configuration of each paebs brake phase.

    # Constructor
    def __init__(self, duration, a_start, a_end, name="", t_start=0, t_end=0):

        # Save boundaries that are relatively but unambiguously describing every paebs brake phase
        self.duration = duration
        self.a_start = a_start
        self.a_end = a_end

        # Assign default values for additional boundaries that are used for absolute description
        self.name = name
        self.t_start = t_start
        self.t_end = t_end

        # Assign properties with initial values that are used later
        self.slope = 0.0

        return

    def _calcLineSlope(self):
        # Function calculates the slope of a straight line based on two points:
        # m = (y1-y0)/(x1-x0)
        # y represents acceleration, x represents time

        if (self.t_end - self.t_start) > 0.0:
            self.slope = (self.a_end - self.a_start) / (self.t_end - self.t_start)
        else:  # Handle edge case
            self.slope = 0.0

        return self.slope

    def getXbrPartProfile(self, step_size):
        # Function calculates the xbr profile for a phase that its instance is representing.
        # For calculation absolute time values are necessary and need to be assigned with valid values
        # on instance first.

        # Initialize acceleration and time value
        time = np.arange(self.t_start, self.t_end, step_size)
        xbr = np.zeros_like(time)

        # Calculate parameters of straight line equation y = mx + b
        m = self._calcLineSlope()
        b = self.a_start

        # Assign xbr values based on straight line equation a(t) = m*t + a0
        for i, time_value in np.ndenumerate(time):
            xbr[i[0]] = (time_value - self.t_start) * m + b

        return [time, xbr]

class PaebsBrakeModel:
    # Class provides functions for calculation and debugging of paebs brake model during conduction of brake cascade.
    # Calculation is identical to official paebs function and
    # therefore based on the same paebs parameter and variables/signals.
    # Only safety distance is not considered.

    # Constructor
    def __init__(self, warning_time_min, partial_braking_delay, partial_braking_time_min, emergency_braking_delay,
                 partial_braking_demand_ramp_start,
                 partial_braking_demand,
                 brake_demand_ramping_jerk,
                 emergency_braking_demand_assumption, emergency_braking_duration=6.0, step_size=0.01):

        # Save predefined parameter for brake model
        self._warning_time_min = warning_time_min
        self._partial_braking_delay = partial_braking_delay
        self._partial_braking_demand_ramp_start = partial_braking_demand_ramp_start
        self._partial_braking_demand = partial_braking_demand
        self._partial_braking_time_min = partial_braking_time_min
        self._emergency_braking_delay = emergency_braking_delay
        self._brake_demand_ramping_jerk = brake_demand_ramping_jerk
        self._emergency_braking_demand_assumption = emergency_braking_demand_assumption

        # Initial Values
        self._emergency_braking_duration = emergency_braking_duration
        self._step_size = step_size
        self._partial_braking_duration = 0.0

        self._last_config = None

        # Initial Routines
        self._calculateDurations()
        self._calculateMaxTime()

        return

    # Public Functions
    # Getter/Setter
    def get_emergency_braking_duration(self):
        return self._emergency_braking_duration

    def set_emergency_braking_duration(self, value):
        value = min(value, 10.0)
        value = max(value, 0.0)
        self._emergency_braking_duration = value
        self._calculateMaxTime()

        return

    # Core Functions
    def calcExpectedVelocityReduction(self, config, init_rel_velocity, init_distance):
        # Function returns the expected velocity reduction based on the paebs brake model.
        # Assumption: All input parameter are handed over as masked arrays of same length.

        # Initialize result arrays
        result = np.ma.empty_like(init_rel_velocity, dtype=np.float)
        result_perc = np.ma.empty_like(init_rel_velocity, dtype=np.float)

        # Loop through input array
        for i, element in np.ndenumerate(init_rel_velocity):

            # Consider only relevant/valid elements of the array based on the mask
            if not init_rel_velocity.mask[i]:  # valid

                # Fetch result for any element and save it on result array
                result[i] = self._calcExpectedVelocityReductionCore(config[i], element, init_distance[i])

                # Catch division by zero
                if element != 0.0:
                    result_perc[i] = result[i] / element * 100
                else:
                    result_perc[i] = 0.0

            else:  # invalid
                result[i] = 0.0
                result_perc[i] = 0.0

        return result, result_perc

    def plotProfiles(self, config, init_rel_velocity, init_distance):
        # Debugging purpose only: Shows calculated profiles for distance, velocity and xbr in a plot.
        # Beware: Intended for use with scalars not arrays!

        # Handle possible array input
        if not np.isscalar(init_rel_velocity):
            config = config[0]
            # Use mean values to imitate scalar value
            init_rel_velocity = np.mean(init_rel_velocity)
            init_distance = np.mean(init_distance)

        # Fetch profiles
        time, xbr, starts = self._getXbrProfile(config)
        time, velocity = self._getVelocityProfile(config, init_rel_velocity)
        time, distance = self._getDistanceProfile(config, init_rel_velocity, init_distance)

        # Collect phase names
        phase_names = []

        for phase in config:
            phase_names.append(phase.name)

        # Plot data
        fig = plt.figure()
        ax_xbr = fig.add_subplot(3, 1, 1)
        ax_xbr.plot(time, xbr, color='red', marker='x', linestyle='solid', linewidth=1.5, markersize=5)
        ax_xbr.set(xlabel='Time [s]', ylabel='Acceleration [m/s^2]',
                   title='XBR Profile')
        ax_xbr.grid()
        plt.vlines(starts, ymin=0, ymax=-10)
        ax_velocity = fig.add_subplot(3, 1, 2)
        ax_velocity.plot(time, velocity, color='green', marker='o', linestyle='solid', linewidth=1.5, markersize=5)
        ax_velocity.set(xlabel='Time [s]', ylabel='Relative Velocity [m/s]',
                        title='Velocity Profile')
        ax_velocity.grid()
        plt.vlines(starts, ymin=0, ymax=-30)
        ax_distance = fig.add_subplot(3, 1, 3)
        ax_distance.plot(time, distance, color='blue', marker='^', linestyle='solid', linewidth=1.5, markersize=5)
        ax_distance.set(xlabel='Time [s]', ylabel='Remaining Distance [m]',
                        title='Distance Profile')
        ax_distance.grid()
        plt.vlines(starts, ymin=0, ymax=80)

        plt.show()

        return

    def getCascadeConfigWarning(self, ego_acceleration):
        # Function returns the specific part of the config list.

        # Handle scalar input
        if np.isscalar(ego_acceleration):
            ego_acceleration = np.array([ego_acceleration])

        # Get cascade config and multiply it on array with the same length as the acceleration
        config_array = result = np.ma.empty_like(ego_acceleration, dtype=object)
        for i, element in np.ndenumerate(ego_acceleration):
            # Extract all phases
            config_array[i] = self._getCascadeConfig(element)[0:]

        return config_array

    def getCascadeConfigPartial(self, ego_acceleration):
        # Function returns the specific part of the config list.

        # Handle scalar input
        if np.isscalar(ego_acceleration):
            ego_acceleration = np.array([ego_acceleration])

        config_array = result = np.ma.empty_like(ego_acceleration, dtype=object)
        for i, element in np.ndenumerate(ego_acceleration):
            # Extract phases starting with delay
            config_array[i] = self._getCascadeConfig(element)[1:]

        return config_array

    def getCascadeConfigEmergency(self, ego_acceleration):
        # Function returns the specific part of the config list.

        # Handle scalar input
        if np.isscalar(ego_acceleration):
            ego_acceleration = np.array([ego_acceleration])
        config_array = result = np.ma.empty_like(ego_acceleration, dtype=object)
        for i, element in np.ndenumerate(ego_acceleration):
            # Extract phases starting with emergency ramp
            config_array[i] = self._getCascadeConfig(element)[4:]

        return config_array

    # Private Functions
    def _calcExpectedVelocityReductionCore(self, config, init_rel_velocity, init_distance):
        # Core function: Handles scalar input and returns expected velocity reduction based on paebs brake model.

        # Fetch profiles for velocity and distance
        time, velocity = self._getVelocityProfile(config, init_rel_velocity)
        time, distance = self._getDistanceProfile(config, init_rel_velocity, init_distance)

        # Check: Crash or not
        result = np.where(distance <= 0.0)

        if len(result[0]) == 0:
            velocity_reduction = init_rel_velocity  # Crash
        else:
            velocity_reduction = init_rel_velocity - velocity[result[0][0]]  # No crash

        return velocity_reduction

    def _getXbrProfile(self, config):
        # Builds an array representing the xbr profile based on the cascade configuration.

        # Initialize xbr array
        time = np.arange(0.0, self._max_time, 0.01)
        xbr = np.zeros_like(time)

        # Find phase starts as time and index
        starts = [0.0]
        time = np.array([])
        xbr = np.array([])

        # Loop through Cascade Phases
        for phase in config:
            # Find start and end time
            if phase.duration > 0.0:
                # Implement absolute start and end time on all phase objects
                phase.t_start = starts[-1]
                phase.t_end = starts[-1] + phase.duration
                starts.append(phase.t_end + self._step_size)

                # Fetch xbr part profile for any phase and merge
                profile = phase.getXbrPartProfile(self._step_size)  # Profile contains xbr and time!
                time = np.concatenate((time, profile[0]), axis=1)
                xbr = np.concatenate((xbr, profile[1]), axis=1)

        return time, xbr, starts

    def _getVelocityProfile(self, config, init_rel_velocity):
        # Builds an array representing the velocity profile based on the xbr profile.
        # Assumption: xbr is negative for braking and relative initial velocity is negative for approaching ego vehicle.

        # Integrate xbr profile
        time, xbr, starts = self._getXbrProfile(config)
        tmp = integrate.cumtrapz(xbr, time, initial=0)

        # Calculate actual velocity under consideration of init velocity
        velocity = init_rel_velocity - tmp  # init velocity will be raising during braking.

        # Consider stop of vehicle
        velocity[velocity > 0.0] = 0.0

        return time, velocity

    def _getDistanceProfile(self, config, init_rel_velocity, init_distance):
        # Builds an array representing the distance profile based on the velocity and xbr profile.
        # Assumption: xbr is negative for braking and relative initial velocity is negative for approaching ego vehicle.

        # Integrate xbr and velocity profile
        time, velocity = self._getVelocityProfile(config, init_rel_velocity)
        tmp = integrate.cumtrapz(velocity, time, initial=0)

        # Calculate actual distance under consideration of init distance
        distance = init_distance + tmp  # init distance will be shrinking during braking.

        # Consider crash of vehicle
        distance[distance < 0.0] = 0.0

        return time, distance

    def _calculateDurations(self):
        # Calculation of the duration of phases that are not directly predefined by parameter but
        # dependent on several parameter according to paebs brake model.
        # Results are directly saved on private properties.

        # Handle case that no jerk is assumed
        if self._brake_demand_ramping_jerk == 0.0:
            self._partial_ramping_delay = 0.0
            self._emergency_ramping_delay = self._emergency_braking_delay
        else:
            self._partial_ramping_delay = \
                (
                        self._partial_braking_demand - self._partial_braking_demand_ramp_start) \
                / self._brake_demand_ramping_jerk
            self._emergency_ramping_delay = \
                (
                        self._emergency_braking_demand_assumption - self._partial_braking_demand) \
                / self._brake_demand_ramping_jerk

        tmp = self._partial_braking_time_min - self._partial_braking_delay - self._partial_ramping_delay

        # Handle edge case
        if tmp < 0.0:
            self._partial_braking_duration = 0.0
        else:
            self._partial_braking_duration = tmp

        return

    def _calculateMaxTime(self):
        # Calculation of the maximum time for the full cascade.
        # Results are directly saved on private properties.

        self._max_time = self._warning_time_min + self._partial_braking_delay + self._partial_ramping_delay + \
                         self._partial_braking_duration + self._emergency_ramping_delay + \
                         self._emergency_braking_duration

        return

    def _getCascadeConfig(self, ego_acceleration):
        # Function saves configuration for each phase in a list.
        # Each configuration is saved on PaebsCascadePhase instance.
        # Definition of each configuration is made within this function.

        # Initialize config list
        config = []

        # Save last used values
        self._last_ego_acceleration = ego_acceleration

        # Phase 1: Warning Phase
        duration = self._warning_time_min
        a_start = ego_acceleration
        a_end = ego_acceleration
        config.append(PaebsCascadePhase(duration, a_start, a_end, "warning"))

        # Phase 2: Partial Braking Delay
        duration = self._partial_braking_delay
        a_start = ego_acceleration
        a_end = ego_acceleration
        config.append(PaebsCascadePhase(duration, a_start, a_end, "partial braking delay"))

        # Phase 3: Partial Braking Ramp
        duration = self._partial_ramping_delay
        a_start = self._partial_braking_demand_ramp_start
        a_end = self._partial_braking_demand
        config.append(PaebsCascadePhase(duration, a_start, a_end, "partial braking ramp"))

        # Phase 4: Partial Braking
        duration = self._partial_braking_duration
        a_start = self._partial_braking_demand
        a_end = self._partial_braking_demand
        config.append(PaebsCascadePhase(duration, a_start, a_end, "partial braking"))

        # Phase 5: Emergency Braking Ramp
        duration = self._emergency_ramping_delay
        a_start = self._partial_braking_demand
        a_end = self._emergency_braking_demand_assumption
        config.append(PaebsCascadePhase(duration, a_start, a_end, "emergency braking ramp"))

        # Phase 6: Emergency Braking
        duration = self._emergency_braking_duration
        a_start = self._emergency_braking_demand_assumption
        a_end = self._emergency_braking_demand_assumption
        config.append(PaebsCascadePhase(duration, a_start, a_end, "emergency braking"))

        # Save last config
        self._last_config = config

        return config
