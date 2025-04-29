from sympy import Symbol, diff, simplify, init_printing

init_printing(use_unicode=True)

# symbols
variables = (
  'dx0', 'vRel0', 'aObst', 'vEgo0',       # test (maneuver) parameters
  'tw', 'tp', 'dxSec', 'aEgop', 'aEgoe',  # AEBS cascade parameters
)
_loc = locals()
for var in variables:
  _loc[var] = Symbol(var)  # e.g. dx0 = Symbol('dx0')


# parameters
obstacle_stops = False
dx0_ncap = 27.766
vRel0_ncap = -6.797
aObst_ncap = -2.0
vEgo0_ncap = 50.0/3.6
tBrakeDelay1 = 0.35
tBrakeDelay2 = 0.21
subs = {
  dx0: dx0_ncap, vRel0: vRel0_ncap, aObst: aObst_ncap, vEgo0: vEgo0_ncap,
  tw: 1.0+tBrakeDelay1, tp: 0.8-tBrakeDelay1+tBrakeDelay2, dxSec: 2.5, aEgop: -3.5, aEgoe: -6.5,
}
subs = tuple(subs.iteritems())


# sub-calculations
aRelpx = -aEgop
vRelpx = vRel0
vRelex = aRelpx*tp + vRelpx

aRel0 = aObst
aRelp = aObst - aEgop
vRelp = aRel0*tw + vRel0
vRele = aRelp*tp + vRelp
dxp = aRel0/2*tw**2 + vRel0*tw + dx0
dxe = aRelp/2*tp**2 + vRelp*tp + dxp

if obstacle_stops:
  vEgoe = aEgop*tp + vEgo0
  vObste = vEgoe + vRele
  aAvoid = vEgoe**2 / (vObste**2/aObst - 2*(dxe-dxSec))
else:
  aAvoid = aObst - vRele**2/(2*(dxe-dxSec))


# dt calculation
dt = vRelex**2/(-2*vRel0*aAvoid) - aRelpx/(2*vRel0)*tp**2 - tp - \
     tw - (dx0-dxSec)/vRel0;
#dt = simplify(dt)


# dt_approx calculation
dt_approx = (
  dt.subs(subs) +
  diff(dt, dx0).subs(subs) * (dx0 - dx0_ncap) +
  diff(dt, vRel0).subs(subs) * (vRel0 - vRel0_ncap) +
  diff(dt, aObst).subs(subs) * (aObst - aObst_ncap) +
  diff(dt, vEgo0).subs(subs) * (vEgo0 - vEgo0_ncap)
)
#dt_approx = simplify(dt_approx)

print 'aAvoid =', aAvoid.subs(subs)
print
print 'dt =', dt
print
print 'dt_approx =', dt_approx
print
print 'dt_approx(x0) =', dt_approx.subs(subs)
print


#dt_gergeli = 2.03 + 0.16*dx0 + 0.72*vRel0
