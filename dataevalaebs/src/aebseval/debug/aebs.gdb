# make breakpoint pending on future shared lib automatically (w/o confirmation)
set breakpoint pending on

# disable the "Type <return> to continue, or q <return> to quit" pagination prompt in GDB
set pagination off

# turn off thread event messages (new/exit)
set print thread-events off

# print override vars (all should be updated at this point)
break orvUpdateInternalStates
commands
silent
up-silently
printf "\n%d,%d,%d,%d,", GPPosOvrActive, GPDeltaGradOvrActive, BPPosOvrActive, StWheelOvrActive
continue
end

# print agent values (all should be updated at this point)
break mstCalcCascade
commands
silent
up-silently
printf "%d,%d,%d,", brkRes.plaus, brkRes.skill, brkRes.skillw
printf "%d,%d,%d,", evaResLeft.plaus, evaResLeft.skill, evaResLeft.skillw
printf "%d,%d,%d,", evaResRight.plaus, evaResRight.skill, evaResRight.skillw
printf "%d,%d,%d,", pasRes.plaus, pasRes.skill, pasRes.skillw
continue
end

# print global vars (all should be updated at this point)
break acoCalc
commands
silent
# final column left out
printf "%d,%d,%f,%f,%f,%f", (int)mstState, (int)mstCascadeState, tWarnDtForPredApprox, aAvoidDynWarnApprox, ttcSimpleDBG, ttcSimpleMaxDBG
continue
end

# output only to log file
set logging redirect on
set logging on

# print header
printf "GPPosOvrActive,GPDeltaGradOvrActive,BPPosOvrActive,StWheelOvrActive,brkPlaus,brkSkill,brkSkillW,evaLeftPlaus,evaLeftSkill,evaLeftSkillW,evaRightPlaus,evaRightSkill,evaRightSkillW,pasPlaus,pasSkill,pasSkillW,mstState,mstCascadeState,tWarnDt,aAvoid,ttcSimple,ttcSimpleMax\n"
