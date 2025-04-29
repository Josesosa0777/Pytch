# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

"""
PlotNavigator scripting tutorial
This tutorial contains basic examples of the PlotNavigator.
"""

from interface import iView
import datavis
import numpy as np
from config.Config import init_dataeval
from bisect import bisect_left, bisect_right

# necessary constants
INVALID_ID = 0xFFFF
FAULT_ID_MAX = 500


def add_delta_compare_plot_for(sgnl_grp1, sgnl_grp2, pn, compare_group1, compare_group2, compare_group3, compare_group4, compare_group5, compare_group6, compare_group7, compare_group8, compare_group9):
    
    time = compare_group1.get_time(sgnl_grp1)
    
    sgnl_1_1 = compare_group1.get_value(sgnl_grp1)
    sgnl_1_2 = compare_group2.get_value(sgnl_grp1)
    sgnl_1_3 = compare_group3.get_value(sgnl_grp1)
    sgnl_1_4 = compare_group4.get_value(sgnl_grp1)
    sgnl_1_5 = compare_group5.get_value(sgnl_grp1)
    sgnl_1_6 = compare_group6.get_value(sgnl_grp1)
    sgnl_1_7 = compare_group7.get_value(sgnl_grp1)
    sgnl_1_8 = compare_group8.get_value(sgnl_grp1)
    sgnl_1_9 = compare_group9.get_value(sgnl_grp1)

    sgnl_2_1 = compare_group1.get_value(sgnl_grp2)
    sgnl_2_2 = compare_group2.get_value(sgnl_grp2)
    sgnl_2_3 = compare_group3.get_value(sgnl_grp2)
    sgnl_2_4 = compare_group4.get_value(sgnl_grp2)
    sgnl_2_5 = compare_group5.get_value(sgnl_grp2)
    sgnl_2_6 = compare_group6.get_value(sgnl_grp2)
    sgnl_2_7 = compare_group7.get_value(sgnl_grp2)
    sgnl_2_8 = compare_group8.get_value(sgnl_grp2)
    sgnl_2_9 = compare_group9.get_value(sgnl_grp2)

    min_sample_length = min((len(sgnl_1_1),len(sgnl_1_2),len(sgnl_1_3),len(sgnl_1_4),len(sgnl_1_5),len(sgnl_1_6),len(sgnl_1_7),len(sgnl_1_8),len(sgnl_1_9)))
    time = time[0:min_sample_length]
    sgnl_1_1 = sgnl_1_1[0:min_sample_length]
    sgnl_1_2 = sgnl_1_2[0:min_sample_length]
    sgnl_1_3 = sgnl_1_3[0:min_sample_length]
    sgnl_1_4 = sgnl_1_4[0:min_sample_length]
    sgnl_1_5 = sgnl_1_5[0:min_sample_length]
    sgnl_1_6 = sgnl_1_6[0:min_sample_length]
    sgnl_1_7 = sgnl_1_7[0:min_sample_length]
    sgnl_1_8 = sgnl_1_8[0:min_sample_length]
    sgnl_1_9 = sgnl_1_9[0:min_sample_length]

    sgnl_2_1 = sgnl_2_1[0:min_sample_length]
    sgnl_2_2 = sgnl_2_2[0:min_sample_length]
    sgnl_2_3 = sgnl_2_3[0:min_sample_length]
    sgnl_2_4 = sgnl_2_4[0:min_sample_length]
    sgnl_2_5 = sgnl_2_5[0:min_sample_length]
    sgnl_2_6 = sgnl_2_6[0:min_sample_length]
    sgnl_2_7 = sgnl_2_7[0:min_sample_length]
    sgnl_2_8 = sgnl_2_8[0:min_sample_length]
    sgnl_2_9 = sgnl_2_9[0:min_sample_length]
    
    ax = pn.addAxis(ylabel="%s - %s" % (sgnl_grp1, sgnl_grp2))

    pn.addSignal2Axis(ax, "delta__main", time, sgnl_1_1 - sgnl_2_1)
    pn.addSignal2Axis(ax, "delta_test2", time, sgnl_1_2 - sgnl_2_2)
    pn.addSignal2Axis(ax, "delta_test3", time, sgnl_1_3 - sgnl_2_3)
    pn.addSignal2Axis(ax, "delta_test4", time, sgnl_1_4 - sgnl_2_4)
    pn.addSignal2Axis(ax, "delta_test5", time, sgnl_1_5 - sgnl_2_5)
    pn.addSignal2Axis(ax, "delta_test6", time, sgnl_1_6 - sgnl_2_6)
    pn.addSignal2Axis(ax, "delta_test7", time, sgnl_1_7 - sgnl_2_7)
    pn.addSignal2Axis(ax, "delta_test8", time, sgnl_1_8 - sgnl_2_8)
    pn.addSignal2Axis(ax, "delta_test9", time, sgnl_1_9 - sgnl_2_9)

    return


def first_nonzero(arr, axis, invalid_val=-1):
    first_zero = np.where(arr == 0)[0][0]
    first_non_zero = np.min(np.nonzero(arr))
    return first_zero if first_non_zero < first_zero else first_non_zero
    #mask = arr!=0
    #return np.where(mask.any(axis=axis), mask.argmax(axis=axis), invalid_val)


def first_value_of(arr, value):
    first_val = np.where(arr == value)[0][0]
    return first_val if not None else 0


def last_value_of(arr, value):
    last_val = np.where(arr == value)[0][-1]
    return last_val if not None else 0


def last_nonzero(arr, axis, invalid_val=-1):
    return np.max(np.nonzero(arr))


def get_data_range(signal, group):
        data = group.get_value(signal)
        start = first_nonzero(data, 0)
        end = last_nonzero(data, 0)
        return start, end


def get_non_zero_range(arr):
    return first_nonzero(arr, 0), last_nonzero(arr, 0)
    

def where_condition(arr, threshold):
    return np.nonzero(arr<threshold)[0][0]


def add_cem_compare_plot(signal_group, pn, compare_group, compare_groups, meas_paths):

    ax_dx = pn.addAxis(ylabel='dx')
    ax_dy = pn.addAxis(ylabel='dy')
    ax_vx = pn.addAxis(ylabel='vx_rel')
    ax_ay = pn.addAxis(ylabel='ay_rel')
    ax_ax = pn.addAxis(ylabel='ax_rel')
    ax_dyn = pn.addAxis(ylabel='dynProp')
    ax_meas = pn.addAxis(ylabel='measured_by')
    ax_class = pn.addAxis(ylabel='classif')
    ax_poe = pn.addAxis(ylabel='poe')
    aebs = compare_group.get_value(signal_group)
    aebs_id = find_consecutive(aebs)
    _, manager, manager_modules = init_dataeval(['-m', meas_paths[0]])
    cem_tracks, cem_signals = manager_modules.calc('fill_flc25_cem_tpf_tracks@aebs.fill', manager)
    first, last = 10000, 0
    longest_id = 0
    longst, longend = 0, 0
    for id in aebs_id:
        for inter in cem_tracks[id].alive_intervals:
            start, end = inter
            if (end - start) > (longend - longst):
                longst = start
                longend = end
                longest_id = id
    for interval in cem_tracks[longest_id].alive_intervals:
        first = min(interval) if min(interval) < first else first
        last = max(interval) if max(interval) > last else last
    time = cem_tracks.time[first-20:last]
    pn.addSignal2Axis(ax_dx, "dx" + "_main_", time, cem_tracks[longest_id].dx[first-20:last])
    pn.addSignal2Axis(ax_dy, "dy" + "_main_", time, cem_tracks[longest_id].dy[first-20:last])
    pn.addSignal2Axis(ax_vx, "vx_rel" + "_main_", time, cem_tracks[longest_id].vx[first-20:last])
    pn.addSignal2Axis(ax_ay, "ay_rel" + "_main_", time, cem_tracks[longest_id].ay[first-20:last])
    pn.addSignal2Axis(ax_ax, "ax_rel" + "_main_", time, cem_tracks[longest_id].ax[first-20:last])
    pn.addSignal2Axis(ax_dyn, "dynprop" + "_main_", time, cem_tracks[longest_id]._eDynamicProperty[first-20:last])
    pn.addSignal2Axis(ax_meas, "measuredby" + "_main_", time, cem_tracks[longest_id]._eMeasuredBy[first-20:last])
    pn.addSignal2Axis(ax_class, "classification" + "_main_", time, cem_tracks[longest_id]._eClassification[first-20:last])
    pn.addSignal2Axis(ax_poe, "poe" + "_main_", time, cem_tracks[longest_id]._uiProbabilityOfExistence[first-20:last])
    max_diff = last - first

    for idx, grp in enumerate(compare_groups):
        print(str(idx))
        aebs = grp.get_value(signal_group)
        aebs_id = find_consecutive(aebs)
        _, manager, manager_modules = init_dataeval(['-m', meas_paths[1+idx]])
        cem_tracks, cem_signals = manager_modules.calc('fill_flc25_cem_tpf_tracks@aebs.fill', manager)
        longest_id = 0
        longst, longend = 0, 0
        for id in aebs_id:
            for inter in cem_tracks[id].alive_intervals:
                start, end = inter
                if (end - start) > (longend - longst):
                    longst = start
                    longend = end
                    longest_id = id
        first, last = 10000, 0
        for interval in cem_tracks[longest_id].alive_intervals:
            first = min(interval) if min(interval) < first else first
            last = max(interval) if max(interval) > last else last
        diff_check = last - first
        if diff_check != max_diff:
            dif = max_diff - diff_check
            last = last + dif
        pn.addSignal2Axis(ax_dx, "dx" + "_test_" + str(idx), time, cem_tracks[longest_id].dx[first-20:last])
        pn.addSignal2Axis(ax_dy, "dy" + "_test_" + str(idx), time, cem_tracks[longest_id].dy[first-20:last])
        pn.addSignal2Axis(ax_vx, "vx_rel" + "_test_" + str(idx), time, cem_tracks[longest_id].vx[first-20:last])
        pn.addSignal2Axis(ax_ay, "ay_rel" + "_test_" + str(idx), time, cem_tracks[longest_id].ay[first-20:last])
        pn.addSignal2Axis(ax_ax, "ax_rel" + "_test_" + str(idx), time, cem_tracks[longest_id].ax[first-20:last])
        pn.addSignal2Axis(ax_dyn, "dynprop" + "_test_" + str(idx), time, cem_tracks[longest_id]._eDynamicProperty[first-20:last])
        pn.addSignal2Axis(ax_meas, "measuredby" + "_test_" + str(idx), time, cem_tracks[longest_id]._eMeasuredBy[first-20:last])
        pn.addSignal2Axis(ax_class, "classification" + "_test_" + str(idx), time, cem_tracks[longest_id]._eClassification[first-20:last])
        pn.addSignal2Axis(ax_poe, "poe" + "_test_" + str(idx), time, cem_tracks[longest_id]._uiProbabilityOfExistence[first-20:last])
    return


def add_compare_plot_for(signal_group, pn,  compare_group, compare_groups):
    
    time = compare_group.get_time(signal_group)
    rescale_kwargs = {'ScaleTime': time}
    _, aebs, unit = compare_group.get_signal(signal_group, **rescale_kwargs)
    #aebs = compare_group.get_value(signal_group)
    first_val, last_val  =  get_data_range("meanspd", compare_group)
    max_diff = last_val - first_val
    time = time[first_val:last_val]
    aebs = aebs[first_val:last_val]

    ax = pn.addAxis(ylabel=signal_group)
    pn.addSignal2Axis(ax, signal_group + "_main", time, aebs)

    for idx, grp in enumerate(compare_groups):
        print(str(idx))
        signal = grp.get_value(signal_group)
        first, last  =  get_data_range("meanspd", grp)
        diff_check = last - first
        if diff_check != max_diff:
            dif = max_diff - diff_check
            last = last + dif
        signal = signal[first:last]
        pn.addSignal2Axis(ax, signal_group + "_test" + str(idx), time, signal)
    return


def add_compare_plot_for_extended(signal_group, pn,  compare_group, compare_groups):
    
    interval_grps = []
    extended_grps = []
    time = compare_group.get_time(signal_group)
    aebs = compare_group.get_value(signal_group)
    first_val, last_val  =  get_data_range("meanspd", compare_group)
    interval_grps.append(first_val)
    interval_grps.append(last_val)
    for idx, grp in enumerate(compare_groups):
        first, last  =  get_data_range("meanspd", grp)
        interval_grps.append(first)
        interval_grps.append(last)
    abs_max = max(interval_grps)
    max_diff = last_val - first_val
    time = time[first_val:last_val]
    aebs = aebs[first_val:last_val]

    ax = pn.addAxis(ylabel=signal_group)
    pn.addSignal2Axis(ax, signal_group + "_main", time, aebs)

    for idx, grp in enumerate(compare_groups):
        print(str(idx))
        signal = grp.get_value(signal_group)
        first, last  =  get_data_range("meanspd", grp)
        if signal.size < abs_max:
            extension_size = abs_max - signal.size
            extension = np.zeros(extension_size)
            signal = np.append(signal, extension)
        diff_check = last - first
        if diff_check != max_diff:
            dif = max_diff - diff_check
            last = last + dif
        signal = signal[first:last]
        pn.addSignal2Axis(ax, signal_group + "_test" + str(idx), time, signal)
    return


def add_compare_plot_original_vs_resim(signal_group, pn,  compare_group, compare_groups):
    
    time = compare_group.get_time(signal_group)
    aebs = compare_group.get_value(signal_group)
    meanspd_orig = compare_group.get_value("meanspd")
    meanspd_orig_time = compare_group.get_time("meanspd")

    can_sig_last_index = len(meanspd_orig) - 50
    can_sig_first_index = 50

    signal_first_index = bisect_left(time, meanspd_orig_time[can_sig_first_index])
    signal_last_index = bisect_right(time, meanspd_orig_time[can_sig_last_index])
    orig_diff = signal_last_index - signal_first_index

    time = time[signal_first_index:signal_last_index]
    aebs = aebs[signal_first_index:signal_last_index]
    ax = pn.addAxis(ylabel=signal_group)
    pn.addSignal2Axis(ax, signal_group + "_main", time, aebs)

    for idx, grp in enumerate(compare_groups):
        signal = grp.get_value(signal_group)
        resim_time = grp.get_time(signal_group)
        mean_spd_time = grp.get_time("meanspd")
        meanspd = grp.get_value("meanspd")

        searchval = meanspd_orig[can_sig_first_index:can_sig_first_index+10]
        N = len(searchval)
        possibles = np.where(meanspd == searchval[0])[0]
        solns = []
        for p in possibles:
            check = meanspd[p:p+N]
            if np.all(check == searchval):
                solns.append(p)
        resim_time_sync = mean_spd_time[solns[0]]
        resim_first_index = bisect_left(resim_time, resim_time_sync)
        #resim_first_index = int(solns[0] * og_ratio)
        resim_last_index = resim_first_index + orig_diff

        signal = signal[resim_first_index:resim_last_index]
        pn.addSignal2Axis(ax, signal_group + "_test" + str(idx), time, signal)
        
    return



def add_compare_plot_start_synced(signal_group, pn,  compare_group, compare_groups):
    
    interval_grps = []
    extended_grps = []
    time = compare_group.get_time(signal_group)
    aebs = compare_group.get_value(signal_group)
    first_val, last_val  =  get_data_range("meanspd", compare_group)
    meanspdval = compare_group.get_value("meanspd")
    og_ratio = float(len(aebs)) / float(len(meanspdval))
    first_val = int(first_val * og_ratio)
    last_val = int(last_val* og_ratio)
    interval_grps.append(first_val)
    interval_grps.append(last_val)
    for idx, grp in enumerate(compare_groups):
        first, last  =  get_data_range("meanspd", grp)
        meanspdval = compare_group.get_value("meanspd")
        cmpr_grp_sig = grp.get_value(signal_group)
        cmpr_grp_ratio = float(len(cmpr_grp_sig)) / float(len(meanspdval))
        first = int(cmpr_grp_ratio * first)
        last = int(cmpr_grp_ratio * last)
        interval_grps.append(first)
        interval_grps.append(last)
    abs_max = max(interval_grps)
    max_diff = last_val - first_val
    time = time[first_val:last_val]
    aebs = aebs[first_val:last_val]

    ax = pn.addAxis(ylabel=signal_group)
    pn.addSignal2Axis(ax, signal_group + "_main", time, aebs)

    for idx, grp in enumerate(compare_groups):
        print(str(idx))
        signal = grp.get_value(signal_group)
        first, last  =  get_data_range("meanspd", grp)
        meanspdval = grp.get_value("meanspd")
        cmpr_grp_ratio = float(len(signal)) / float(len(meanspdval))
        first = int(cmpr_grp_ratio * first)
        last = int(cmpr_grp_ratio * last)
        if signal.size < abs_max:
            extension_size = abs_max - signal.size
            extension = np.zeros(extension_size)
            signal = np.append(signal, extension)
        diff_check = last - first
        if diff_check != max_diff:
            dif = max_diff - diff_check
            last = last + dif
        signal = signal[first:last]
        pn.addSignal2Axis(ax, signal_group + "_test" + str(idx), time, signal)
    return

def add_compare_plot_fer_start_synced(signal_group, pn,  compare_group, compare_groups):
    
    interval_grps = []
    extended_grps = []
    time = compare_group.get_time(signal_group)
    aebs = compare_group.get_value(signal_group)
    meanspdval = compare_group.get_value("meanspd")
    first_val, last_val  =  10, len(meanspdval) - 10
    og_ratio = float(len(aebs)) / float(len(meanspdval))
    first_val = int(first_val * og_ratio)
    last_val = int(last_val* og_ratio)
    interval_grps.append(first_val)
    interval_grps.append(last_val)
    for idx, grp in enumerate(compare_groups):
        meanspdval = compare_group.get_value("meanspd")
        first, last  =  10, len(meanspdval) - 10
        cmpr_grp_sig = grp.get_value(signal_group)
        cmpr_grp_ratio = float(len(cmpr_grp_sig)) / float(len(meanspdval))
        first = int(cmpr_grp_ratio * first)
        last = int(cmpr_grp_ratio * last)
        interval_grps.append(first)
        interval_grps.append(last)
    abs_max = max(interval_grps)
    max_diff = last_val - first_val
    time = time[first_val:last_val]
    aebs = aebs[first_val:last_val]

    ax = pn.addAxis(ylabel=signal_group)
    pn.addSignal2Axis(ax, signal_group + "_main", time, aebs)

    for idx, grp in enumerate(compare_groups):
        print(str(idx))
        signal = grp.get_value(signal_group)
        meanspdval = grp.get_value("meanspd")
        first, last  =  10, len(meanspdval) - 10
        cmpr_grp_ratio = float(len(signal)) / float(len(meanspdval))
        first = int(cmpr_grp_ratio * first)
        last = int(cmpr_grp_ratio * last)
        if signal.size < abs_max:
            extension_size = abs_max - signal.size
            extension = np.zeros(extension_size)
            signal = np.append(signal, extension)
        diff_check = last - first
        if diff_check != max_diff:
            dif = max_diff - diff_check
            last = last + dif
        signal = signal[first:last]
        pn.addSignal2Axis(ax, signal_group + "_test" + str(idx), time, signal)
    return


def add_compare_plot_for_extended_rescale(signal_group, pn,  compare_group, compare_groups):
    
    interval_grps = []
    extended_grps = []
    time = compare_group.get_time(signal_group)
    rescale_kwargs = {'ScaleTime': time}
    _, aebs = compare_group.get_signal(signal_group, **rescale_kwargs)

    ax = pn.addAxis(ylabel=signal_group)
    pn.addSignal2Axis(ax, signal_group + "_main", time, aebs)

    for idx, grp in enumerate(compare_groups):
        print(str(idx))
        _, signal = grp.get_signal(signal_group, **rescale_kwargs)
        pn.addSignal2Axis(ax, signal_group + "_test" + str(idx), time, signal)
    return


def add_compare_plot_min_sample_for(signal_group, pn,  compare_group, compare_groups):
    

    time = compare_group.get_time(signal_group)
    aebs = compare_group.get_value(signal_group)
    signal_lst = [aebs]

    ax = pn.addAxis(ylabel=signal_group)

    for idx, grp in enumerate(compare_groups):
        signal = grp.get_value(signal_group)
        signal_lst.append(signal)
        
    min_sample_length = min([len(s) for s in signal_lst])

    for idx, sig in enumerate(signal_lst):
        pn.addSignal2Axis(ax, signal_group + "_test" + str(idx), time[0:min_sample_length], sig[0:min_sample_length])

    return


def add_compare_plot_rescale_sample_for(signal_group, pn,  compare_group, compare_groups):
    

    time = compare_group.get_time(signal_group)
    aebs = compare_group.get_value(signal_group)
    aebs_id = compare_group.get_value('aebs_id')
    start_indx, length = find_longest_consecutive(aebs_id)
    div = float(len(aebs)) / float(len(aebs_id))
    first = int(start_indx * div)
    last = int((start_indx + length) * div)
    max_diff = last - first
    time = time[first:last]

    ax = pn.addAxis(ylabel=signal_group)
    pn.addSignal2Axis(ax, signal_group + "_main", time, aebs[first:last])

    for idx, grp in enumerate(compare_groups):
        signal = grp.get_value(signal_group)
        aebs_id = grp.get_value('aebs_id')

        start_indx, length = find_longest_consecutive(aebs_id)
        div = float(len(signal)) / float(len(aebs_id))
        first = int(start_indx * div)
        last = int((start_indx + length) * div)
        diff_check = last - first
        if diff_check != max_diff:
            dif = max_diff - diff_check
            last = last + dif
        pn.addSignal2Axis(ax, signal_group + "_test" + str(idx), time, signal[first:last])		

    return



def add_compare_plot_non_zero_for(signal_group, pn,  compare_group, compare_groups):
    
    time = compare_group.get_time(signal_group)
    aebs = compare_group.get_value(signal_group)
    first_val, last_val  =  get_non_zero_range(aebs)
    max_diff = last_val - first_val
    time = time[first_val:last_val]
    aebs = aebs[first_val:last_val]

    ax = pn.addAxis(ylabel=signal_group)
    pn.addSignal2Axis(ax, signal_group + "_main", time, aebs)

    for idx, grp in enumerate(compare_groups):
        signal = grp.get_value(signal_group)
        first, last  =  get_non_zero_range(signal)
        diff_check = last - first
        if diff_check != max_diff:
            dif = max_diff - diff_check
            last = last + dif
        signal = signal[first:last]
        pn.addSignal2Axis(ax, signal_group + "_test" + str(idx), time, signal)
    return


def find_consecutive(x):
    """Find consecutive items in an array."""

    x = np.asanyarray(x)
    if x.ndim != 1:
        raise ValueError('only 1D array supported')
    n = x.shape[0]

    if n == 0:
        return np.array([]), np.array([]), np.array([])

    else:
        loc_run_start = np.empty(n, dtype=bool)
        loc_run_start[0] = True
        np.not_equal(x[:-1], x[1:], out=loc_run_start[1:])
        #run_starts = np.nonzero(loc_run_start)[0]
        run_values = x[loc_run_start]
        #run_lengths = np.diff(np.append(run_starts, n))

        run_values = [y for y in run_values if y != 255]
        set_values = set(run_values)
        return list(set_values)


def find_longest_consecutive(x):
    """Find consecutive items in an array."""

    x = np.asanyarray(x)
    if x.ndim != 1:
        raise ValueError('only 1D array supported')
    n = x.shape[0]

    if n == 0:
        return np.array([]), np.array([]), np.array([])

    else:
        loc_run_start = np.empty(n, dtype=bool)
        loc_run_start[0] = True
        np.not_equal(x[:-1], x[1:], out=loc_run_start[1:])
        run_starts = np.nonzero(loc_run_start)[0]
        run_values = x[loc_run_start]
        run_lengths = np.diff(np.append(run_starts, n))

        val_indx = [i for i, j in enumerate(run_values) if j != 255]
        longest_val = max(run_lengths[val_indx])
        longest_index = np.where(run_lengths == longest_val)[0]
        return run_starts[longest_index], longest_val


fault_signals = [
    {
        "engspd": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sAoa_CanInput_EEC1_EEC1_EngSpd"),
        "fPitch": ("MFC5xx Device.ACAL.pAcalOutput","MFC5xx_Device_ACAL_pAcalOutput_onlineOutput_worldToCamInstant_pose_fPitch"),
        "fRoll": ("MFC5xx Device.ACAL.pAcalOutput","MFC5xx_Device_ACAL_pAcalOutput_onlineOutput_worldToCamInstant_pose_fRoll"),
        "fYaw": ("MFC5xx Device.ACAL.pAcalOutput","MFC5xx_Device_ACAL_pAcalOutput_onlineOutput_worldToCamInstant_pose_fYaw"),
        "fTz": ("MFC5xx Device.ACAL.pAcalOutput","MFC5xx_Device_ACAL_pAcalOutput_onlineOutput_worldToCamInstant_pose_fTz"),
        "fTy": ("MFC5xx Device.ACAL.pAcalOutput","MFC5xx_Device_ACAL_pAcalOutput_onlineOutput_worldToCamInstant_pose_fTy"),
        "fTx": ("MFC5xx Device.ACAL.pAcalOutput","MFC5xx_Device_ACAL_pAcalOutput_onlineOutput_worldToCamInstant_pose_fTx"),
        "meanspd": ("EBC2_0B","EBC2_FrontAxleSpeed_0B_s0B"),
        "axle_speed": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_vehicle_brake_system_front_axle_speed"),
    }]

mat_file_test_signal = [
    {
        "meanspd": ("CAN_MFC_Public_EBC2_0B","EBC2_FrontAxleSpeed_0B_CAN_MFC_Public")
    },
    {
        "meanspd": ("CAN_MFC_Public_EBC2_0B","EBC2_FrontAxleSpeed_0B")
    },
    {
        "meanspd": ("EBC2_0B","EBC2_FrontAxleSpeed_0B_s0B"),
    },
    {
        "meanspd": ("EBC2_0B","EBC2_FrontAxleSpeed_0B_s0B"),
    }
]


signal_grp = [
    {
        #"fDistX": ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas","MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObject0_kinematic_fDistX"),
        #"GlobalTime": ("TimeStampConversion_Rx","MFC5xx_Device_FCU_TimeStampConversion_Rx_GlobalTime"),
        #"recObjectTime": ("LdOutput","MFC5xx_Device_LD_LdOutput_road_ego_left_clothoidFar_offset"),
        #"ttc": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_EbOutput_hmi_output_aebs_ttc"),
        "source": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_aebs_object_source"),
        "axle_speed": ("EBC2_0B","EBC2_FrontAxleSpeed_0B_s0B"),
        "engspd": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sAoa_CanInput_EEC1_EEC1_EngSpd"),
        "meanspd": ("EBC2_0B","EBC2_FrontAxleSpeed_0B_s0B"),
        "dx": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_aebs_object_dx"),
        "EM_dx": ("MFC5xx Device.EM.EmGenObjectList","MFC5xx_Device_EM_EmGenObjectList_aObject0_Kinematic_fDistX"),
        "aebs_id": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_aebs_object_id"),
        "aebs_state": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_EbOutput_hmi_output_aebs_system_state"),

    }
]

cem_signals = [
    {
        "engspd": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sAoa_CanInput_EEC1_EEC1_EngSpd"),
        "aebs_id": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_aebs_object_id"),
        "aebs_state": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_EbOutput_hmi_output_aebs_system_state"),
        "meanspd": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sAoa_CanInput_EBC2_EBC2_MeanSpdFA"),
        "CemState": ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_StateOutputIfMeas", "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_CemState"),
        "sensorRadar_state": ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_StateOutputIfMeas", "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sensorRadar_state"),
        "sensorCamera_state": ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_StateOutputIfMeas", "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sensorCamera_state"),
        "dx": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_aebs_object_dx"),
    }
]

paebs_signals = [
    {
        "engspd": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sAoa_CanInput_EEC1_EEC1_EngSpd"),
        "meanspd": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sAoa_CanInput_EBC2_EBC2_MeanSpdFA"),
        "paebs_state": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_system_state"),
        "detected": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_relevant_object_detected"),
        "dx": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_relevant_object_dx"),
        "ttc": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_relevant_object_ttc"),
        "vx": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_relevant_object_vx_rel"),
        "warning": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_warning_level"),
    }
]

state_sgs  = [
    {
        "engspd": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sAoa_CanInput_EEC1_EEC1_EngSpd"),
        "aebs_id": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_aebs_object_id"),
        "meanspd": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sAoa_CanInput_EBC2_EBC2_MeanSpdFA"),
        "CemState": ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_StateOutputIfMeas", "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_CemState"),
        "sensorRadar_state": ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_StateOutputIfMeas", "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sensorRadar_state"),
        "sensorCamera_state": ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_StateOutputIfMeas", "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sensorCamera_state"),
        "aebs_state": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_EbOutput_hmi_output_aebs_system_state"),
        "cam_eDynamicProperty": ("MFC5xx Device.EM.EmGenObjectList","MFC5xx_Device_EM_EmGenObjectList_aObject0_Attributes_eDynamicProperty"),
        "dx": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_aebs_object_dx"),
        "dynamic_property_of_aebs_relevant_object": ("MFC5xx Device.KB.MTSI_stKBFreeze_010ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_010ms_t_sFlc25_OmLonControlMessages_mro2_aebs_dynamic_property_of_aebs_relevant_object")
    }
]



# initial parameter definition
init_params = dict(KBfreeze =dict(compare_signals=signal_grp, compare_aebs=1),
                   calibration =dict(compare_signals=fault_signals, compare_aebs=2),
                   CEM =dict(compare_signals=cem_signals, compare_aebs=3),
                   paebs =dict(compare_signals=paebs_signals, compare_aebs=4),
                   state_sigs = dict(compare_signals=state_sgs, compare_aebs=5),
                   can_test = dict(compare_signals=mat_file_test_signal, compare_aebs=6))


class View(iView):
    # define two measurement channel for the script
    channels = 'main', 'test0'#, 'test1', 'test2', 'test3', 'test4', 'test5', 'test6', 'test7', 'test8', 'test9'#, 'test10', 'test11', 'test12', 'test13', 'test14', 'test15', 'test16', 'test17', 'test18', 'test19'

    # the init method gets the selected initial parameters
    def init(self, compare_signals, compare_aebs):
        self.compare_signals = compare_signals
        self.compare_aebs = compare_aebs
        return

    def check(self):
        compare_group = self.source.selectSignalGroup(self.compare_signals)
        sources = []
        for ch in self.channels[1:]:
            sources.append(self.get_source(ch))
        meas_paths = [self.source.FileName]
        compare_groups = []
        for src in sources:
            meas_paths.append(src.FileName)
            compare_groups.append(src.selectSignalGroup(self.compare_signals))
         

        return compare_group, compare_groups, meas_paths

    # fill method is needed to pass through the signal groups to the view method
    def fill(self, compare_group, compare_groups, meas_paths):
        return compare_group, compare_groups, meas_paths

    # view method will create the plots
    def view(self, compare_group, compare_groups, meas_paths):
        
        pn = datavis.cPlotNavigator(title="Compare measurements")
        if self.compare_aebs == 1:
            add_compare_plot_original_vs_resim('aebs_id', pn, compare_group, compare_groups)
            add_compare_plot_original_vs_resim('source', pn, compare_group, compare_groups)
            add_compare_plot_original_vs_resim('dx', pn, compare_group, compare_groups)
            add_compare_plot_original_vs_resim('aebs_state', pn, compare_group, compare_groups)
            #pn1 = datavis.cPlotNavigator(title="FCU")
            #pn2 = datavis.cPlotNavigator(title="EM")
            #add_compare_plot_rescale_sample_for('FCU_dx', pn, compare_group, compare_groups)
            #add_compare_plot_rescale_sample_for('EM_dx', pn, compare_group, compare_groups)
            add_compare_plot_original_vs_resim('axle_speed', pn, compare_group, compare_groups)
            
        elif self.compare_aebs == 2:
            add_compare_plot_fer_start_synced('fPitch', pn, compare_group, compare_groups)
            add_compare_plot_fer_start_synced('fRoll', pn, compare_group, compare_groups)
            add_compare_plot_fer_start_synced('fYaw', pn, compare_group, compare_groups)
            add_compare_plot_fer_start_synced('fTz', pn, compare_group, compare_groups)
            add_compare_plot_fer_start_synced('fTy', pn, compare_group, compare_groups)
            add_compare_plot_fer_start_synced('fTx', pn, compare_group, compare_groups)
            add_compare_plot_fer_start_synced('meanspd', pn, compare_group, compare_groups)

        elif self.compare_aebs == 3:
            add_cem_compare_plot('aebs_id', pn, compare_group, compare_groups, meas_paths)
            #add_compare_plot_for('aebs_state', pn, compare_group, compare_groups)
            add_compare_plot_min_sample_for('CemState', pn, compare_group, compare_groups)
            add_compare_plot_min_sample_for('sensorRadar_state', pn, compare_group, compare_groups)
            add_compare_plot_min_sample_for('sensorCamera_state', pn, compare_group, compare_groups)
            #add_compare_plot_for('aebs_state', pn, compare_group, compare_groups)
            add_compare_plot_for_extended('dx', pn, compare_group, compare_groups)
            #add_compare_plot_for('cam_eDynamicProperty', pn, compare_group, compare_groups)
            #add_compare_plot_for('dynamic_property_of_aebs_relevant_object', pn, compare_group, compare_groups)
            #add_compare_plot_for('meanspd', pn, compare_group, compare_groups)

        if self.compare_aebs == 4:
            add_compare_plot_for_extended('paebs_state', pn, compare_group, compare_groups)
            add_compare_plot_for_extended('detected', pn, compare_group, compare_groups)
            add_compare_plot_for_extended('dx', pn, compare_group, compare_groups)
            add_compare_plot_for_extended('ttc', pn, compare_group, compare_groups)
            add_compare_plot_for_extended('vx', pn, compare_group, compare_groups)
            add_compare_plot_for_extended('warning', pn, compare_group, compare_groups)
            add_compare_plot_for_extended('meanspd', pn, compare_group, compare_groups)

        if self.compare_aebs == 5:
            add_compare_plot_min_sample_for('CemState', pn, compare_group, compare_groups)
            add_compare_plot_min_sample_for('sensorRadar_state', pn, compare_group, compare_groups)
            add_compare_plot_min_sample_for('sensorCamera_state', pn, compare_group, compare_groups)
            add_compare_plot_for_extended('aebs_state', pn, compare_group, compare_groups)
            add_compare_plot_for_extended('dx', pn, compare_group, compare_groups)
            add_compare_plot_rescale_sample_for('cam_eDynamicProperty', pn, compare_group, compare_groups)
            add_compare_plot_rescale_sample_for('dynamic_property_of_aebs_relevant_object', pn, compare_group, compare_groups)
            add_compare_plot_for_extended('meanspd', pn, compare_group, compare_groups)

        if self.compare_aebs == 6:
            add_compare_plot_original_vs_resim('meanspd', pn, compare_group, compare_groups)


        # add the PlotNavigator client to the Synchronizer
        self.sync.addClient(pn)




def consecutive(data, stepsize=1):
    return np.split(data, np.where(np.diff(data) != stepsize)[0]+1)

a = np.array([0, 47, 48, 49, 50, 97, 98, 99])
consecutive(a)
