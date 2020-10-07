"""
GUYANA

Populations:
    FSW    Clients    MSM    Children    M 15-19    F 15-19    M 20-49    F 20-49    M 50+    F 50+

Programs:
    Condoms and SBCC    FSW program    MSM program    HIV testing    ART    PMTCT
"""

# IMPORTS
from optima import Project, Parscen, Budgetscen, dcp, pygui, odict, defaultobjectives, defaultconstraints, plotallocations
from numpy import array, nan


# DEFINE ANALYSES TO RUN
torun = [
'makeproject',
'calibrate',
'printnumbers',
'makeprograms',
#'compareoutcomes',
'budgetscens',
'printtable',
#'90-90-90',
#'prep',
#'minoutcomes',
#'savescaleup',
#'minmoney',
#'minmoneyscen',
#'preparegaprogs', 
#'savegaproject',
'saveproject',
#'makesubdividesheet'
#'minoutcomefixedart',
]


# FILEPATHS AND GLOBAL VARIABLES
folder = 'files/prj/'
#folder  = '../../gm/'
projectfile = folder + 'guyana.prj'
spreadsheetfile = 'guyana.xlsx'
interaction = 'additive'

doplotbasics = False
doplot = True
dosave = True # Export figures
saveresults = True
ndistricts = 10 # For generating geo spreadsheet




########################################################################
# RUN ANALYSES
########################################################################

# Make project
if 'makeproject' in torun:
    P = Project(spreadsheet=spreadsheetfile, dorun=False)
    P.settings.start=2000.
    

# Calibrate
if 'calibrate' in torun:
    
    P.pars()['fixproptx'].t = 2100
    P.pars()['fixpropsupp'].t = 2100
    
    P.copyparset('default','manualfit')
    
    # Main changes
    P.pars()['initprev'].y[:]   = [0.15,     0.02,       0.05,   0.001,     0.004,      0.005,  0.0055,      0.0055,   0.0001,  0.0001]
    P.pars()['force'].y[:]      = [22.,     4.,        0.8,    1.0,        16.5,        1.9,    4.7,        2.65,    .0,    .0]
    P.pars()['requiredvl'].y = 4. #1.2
    P.pars()['treatfail'].y = .5 #1.2
    mtctfactor = 0.5 # Reduce MTCT
    P.pars()['mtctbreast'].y *= mtctfactor
    P.pars()['mtctnobreast'].y *= mtctfactor
    P.pars()['hivtest'].m = .6
    P.pars()['deathlt50'].y *=2
    P.pars()['deathgt50'].y *= 2
    P.pars()['deathusvl'].y = .9
    
    # Copy things    
    P.copyparset('manualfit','no-leavecare')
    P.parsets['no-leavecare'].pars['leavecare'].m = 0.01
    P.parsets['no-leavecare'].pars['aidsleavecare'].m = 0.01
    
    P.copyparset('no-leavecare','status-quo')
    P.parsets['status-quo'].pars['fixproptx'].t = 2016
    P.parsets['status-quo'].pars['fixpropsupp'].t = 2016
    
    P.copyparset('manualfit','Calibrated') # So it's the last
    
    P.runsim(start=2000.,end=2016.)
    if doplotbasics: 
        pygui(P)


## Print out key numbers
if 'printnumbers' in torun:

    from optima import sigfig, blank
    
    blank()
    res = P.results[0]
    output =  '=========================================\n'
    output += 'Progress toward fast-track targets\n'
    output += '=========================================\n'
    output += '              PLHIV 2015: %s\n' % (sigfig(res.main['numplhiv'].tot[0][15],sigfigs=4))
    output += '   Total prevalence 2015: %.1f\n' % (100*(res.main['prev'].tot[0][15]))
    output += '   Adult prevalence 2015: %.1f\n' % (100*(res.other['adultprev'].tot[0][15]))
    output += '   Child prevalence 2015: %.1f\n' % (100*(res.other['childprev'].tot[0][15]))
    output += '=========================================\n'
    output += 'Cascade table\n'
    output += '=========================================\n'
    output += '               |        2014 |        2015 |        2016 |\n'
    output += '         PLHIV | %s (7600) | %s (7800) | %s (7891) |\n'  % (sigfig(res.main['numplhiv'].tot[0][14],sigfigs=4),sigfig(res.main['numplhiv'].tot[0][15],sigfigs=4),sigfig(res.main['numplhiv'].tot[0][16],sigfigs=4))
    output += '     Diagnosed | %s (4776) | %s (5534) | %s (5918) |\n'  % (sigfig(res.main['numdiag'].tot[0][14],sigfigs=4),sigfig(res.main['numdiag'].tot[0][15],sigfigs=4),sigfig(res.main['numdiag'].tot[0][16],sigfigs=4))
    output += '        Linked | %s (4599) | %s (5329) | %s (5622) |\n'  % (sigfig(res.main['numevercare'].tot[0][14],sigfigs=4),sigfig(res.main['numevercare'].tot[0][15],sigfigs=4),sigfig(res.main['numevercare'].tot[0][15],sigfigs=4))
    output += '      Retained | %s (4466) | %s (5176) | %s (5460) |\n'  % (sigfig(res.main['numincare'].tot[0][14],sigfigs=4),sigfig(res.main['numincare'].tot[0][15],sigfigs=4),sigfig(res.main['numincare'].tot[0][16],sigfigs=4))
    output += '       Treated | %s (4295) | %s (4551) | %s (4791) |\n'  % (sigfig(res.main['numtreat'].tot[0][14],sigfigs=4),sigfig(res.main['numtreat'].tot[0][15],sigfigs=4),sigfig(res.main['numtreat'].tot[0][16],sigfigs=4))
    output += '    Suppressed | %s (2878) | %s (3050) | %s (3211) |\n'  % (sigfig(res.main['numsuppressed'].tot[0][14],sigfigs=4),sigfig(res.main['numsuppressed'].tot[0][15],sigfigs=4),sigfig(res.main['numsuppressed'].tot[0][16],sigfigs=4))
    output += '    Tests done |        3482 |         677 |        3913 |\n'
    output += '    VS confirm |        2440 |         536 |        3211 |\n'
    output += '=========================================\n'
    output += 'Cascade table\n'
    output += '=========================================\n'
    output += '               |        2014 |        2015 |        2016 |\n'
    output += '         PLHIV | %s (7600) | %s (7800) | %s (7891) |\n'  % (sigfig(res.main['numplhiv'].tot[0][14],sigfigs=4),sigfig(res.main['numplhiv'].tot[0][15],sigfigs=4),sigfig(res.main['numplhiv'].tot[0][16],sigfigs=4))
    output += '     Diagnosed |     %.0f (63) |     %.0f (71) |     %.0f (75) |\n'  % (100*res.main['numdiag'].tot[0][14]/res.main['numplhiv'].tot[0][14],100*res.main['numdiag'].tot[0][15]/res.main['numplhiv'].tot[0][15],100*res.main['numdiag'].tot[0][16]/res.main['numplhiv'].tot[0][16])
    output += '        Linked |     %.0f (96) |     %.0f (96) |     %.0f (95) |\n'  % (100*res.main['numevercare'].tot[0][14]/res.main['numdiag'].tot[0][14],100*res.main['numevercare'].tot[0][15]/res.main['numdiag'].tot[0][15],100*res.main['numevercare'].tot[0][16]/res.main['numdiag'].tot[0][16])
    output += '      Retained |     %.0f (97) |     %.0f (97) |     %.0f (97) |\n'  % (100*res.main['numincare'].tot[0][14]/res.main['numevercare'].tot[0][14],100*res.main['numincare'].tot[0][15]/res.main['numevercare'].tot[0][15],100*res.main['numincare'].tot[0][16]/res.main['numevercare'].tot[0][16])
    output += '       Treated |     %.0f (96) |     %.0f (88) |     %.0f (88) |\n'  % (100*res.main['numtreat'].tot[0][14]/res.main['numincare'].tot[0][14],100*res.main['numtreat'].tot[0][15]/res.main['numincare'].tot[0][15],100*res.main['numtreat'].tot[0][16]/res.main['numincare'].tot[0][16])
    output += '    Suppressed |     %.0f (67) |     %.0f (67) |     %.0f (67) |\n'  % (100*res.main['numsuppressed'].tot[0][14]/res.main['numtreat'].tot[0][14],100*res.main['numsuppressed'].tot[0][15]/res.main['numtreat'].tot[0][15],100*res.main['numsuppressed'].tot[0][16]/res.main['numtreat'].tot[0][16])
    output += '    Tests done |        3482 |         677 |        3913 |\n'
    output += '    VS confirm |        2440 |         536 |        3211 |\n'
    print output


if 'makeprograms' in torun:
    
    from optima import Program, Programset
    
    def tpl(val):
        ''' Create a tuple out of a value '''
        return (val,val)
        

    # Program 1: Condoms and SBCC
    capships = P.pars()['condcas'].y.keys()
    capshippops = list(set([capship[i] for i in range(2) for capship in capships])) # WARNING, weird
    cond = Program(short='General population prevention',
                  name='General population prevention',
                  targetpars=[{'param': 'condcas', 'pop': caspship} for caspship in capships],
                  targetpops=capshippops,
                  category='Prevention')

    cond.costcovfn.addccopar({'saturation': (0.8,0.9),
                             't': 2016.0,
                             'unitcost': tpl(3.87)}) # Cost / coverage: 304910.44/54815


    # Program 2: FSW programs
    fswprog = Program(short='FSW programs',
                  name='FSW programs',
                  targetpars=[{'param': 'hivtest', 'pop': 'FSW'}, {'param': 'condcom', 'pop': ('Clients', 'FSW')}, {'param': 'condcas', 'pop': ('M 25-49', 'FSW')}, {'param': 'condcas', 'pop': ('Clients', 'FSW')}, {'param': 'condcas', 'pop': ('M 50+', 'FSW')}],
                  targetpops=['FSW'],
                  category='Prevention')

    fswprog.costcovfn.addccopar({'saturation': (0.95,0.95),
                             't': 2016.0,
                             'unitcost': tpl(67.049)})


    # Program 3: MSM programs
    msmprog = Program(short='MSM programs',
                  name='MSM programs',
                  targetpars=[{'param': 'hivtest', 'pop': 'MSM'}, {'param': 'condcas', 'pop': ('MSM', 'MSM')}],
                  targetpops=['MSM'],
                  category='Prevention')

    msmprog.costcovfn.addccopar({'saturation': (0.95,0.95),
                             't': 2016.0,
                             'unitcost': tpl(80.637)})


    # Program 4: HTC
    htcpops = ['Clients', 'M 15-24', 'M 25-49', 'M 50+','F 15-24', 'F 25-49', 'F 50+']
    htc = Program(short='HTC',
                  name='HIV testing and counseling',
                  targetpars=[{'param': 'hivtest', 'pop': popkey} for popkey in htcpops],
                  targetpops=htcpops,
                  category='Treatment')

    htc.costcovfn.addccopar({'saturation': (0.95,0.95),
                             't': 2016.0,
                             'unitcost': tpl(10.84)})

    # Program 5: ART
    art = Program(short='ART',
                  name='Antiretroviral therapy',
                  targetpars=[{'param': 'numtx', 'pop': 'tot'}],
                  targetpops=['tot'],
                  category='Treatment')
    
#    art.costcovfn.addccopar({'saturation': (0.99,0.99),
#                             't': 2016.0,
#                             'unitcost': tpl(327.)})
    art.costcovfn.addccopar({'saturation': (0.99,0.99),
                             't': 2016.0,
                             'unitcost': tpl(383.20)}) #187. # 184.4 #396.59

    # Program 6: PMTCT
    pmtct = Program(short='PMTCT',
                  name='Prevention of mother-to-child transmission',
                  targetpars=[{'param': 'numpmtct', 'pop': 'tot'}, {'param': 'numtx', 'pop': 'tot'}],
                  targetpops=['tot'],
                  category='Treatment')

    pmtct.costcovfn.addccopar({'saturation': (0.95,0.95),
                             't': 2016.0,
                             'unitcost': tpl(3000.)})

    # Program 7: Lab
    lab = Program(short='Lab',
                  name='Laboratory monitoring',
                  targetpars=[{'param': 'numvlmon', 'pop': 'tot'}],
                  targetpops=['tot'],
                  category='Treatment')

    lab.costcovfn.addccopar({'saturation': (0.95,0.95),
                             't': 2016.0,
                             'unitcost': tpl(251)})

    ## SET BUDGETS
    cond.costcovdata = odict({'cost': [211996.00], 'coverage':[nan], 't': [2016]})
    fswprog.costcovdata = odict({'cost': [223075.25], 'coverage':[nan],'t': [2016]})                    
    msmprog.costcovdata = odict({'cost': [156424.94], 'coverage':[nan],'t': [2016]})
    htc.costcovdata = odict({'cost': [731105.], 'coverage':[nan], 't': [2016]})
    art.costcovdata = odict({'cost': [1784194.], 'coverage':[nan],'t': [2016]}) #1433817 #852798
    pmtct.costcovdata = odict({'cost': [405756.24], 'coverage':[nan],'t': [2016],})   
    lab.costcovdata = odict({'cost': [974912.40], 'coverage':[nan],'t': [2016],})   

    #### MAKE PROGRAM SET
    R = Programset(programs=[cond, fswprog, msmprog, htc, art, pmtct, lab])

    R.covout['numtx']['tot'].addccopar({'intercept': (0.,0.), 't': 2016.0})
    R.covout['numvlmon']['tot'].addccopar({'intercept': (0.,0.), 't': 2016.0})
    R.covout['numpmtct']['tot'].addccopar({'intercept': (0.,0.), 't': 2016.0})

    R.covout['condcom'][('Clients','FSW')].addccopar({'intercept': (0.25,0.25), 't': 2016.0, 'FSW programs':(0.95,1.)})

    R.covout['condcas'][('Clients', 'FSW')].addccopar({'intercept':     (0.15, 0.25),'t':2016. , "General population prevention": (0.5, 0.6), "FSW programs": (0.99, 0.99)})
    R.covout['condcas'][('Clients', 'F 25-49')].addccopar({'intercept': (0.25, 0.3),'t':2016. ,  "General population prevention": (0.7, 0.8)})
    R.covout['condcas'][('Clients', 'F 50+')].addccopar({'intercept':   (0.3, 0.3),'t':2016. , "General population prevention": (0.55, 0.65)})
    R.covout['condcas'][('MSM', 'MSM')].addccopar({'intercept': (0.3, 0.3) ,'t':2016. , "MSM programs": (0.9, 0.9), "General population prevention": (0.45, 0.5)})
    R.covout['condcas'][('M 15-24', 'F 15-24')].addccopar({'intercept': (0.01, 0.01),'t':2016. , "General population prevention": (0.3, 0.4)})
    R.covout['condcas'][('M 25-49', 'FSW')].addccopar({'intercept':     (0.04, 0.05),'t':2016. ,  "General population prevention": (0.2, 0.2), "FSW programs": (0.6, 0.7)})
    R.covout['condcas'][('M 25-49', 'F 15-24')].addccopar({'intercept': (0.01, 0.01),'t':2016. , "General population prevention": (0.3, 0.4)})
    R.covout['condcas'][('M 25-49', 'F 25-49')].addccopar({'intercept': (0.01, 0.01),'t':2016. ,  "General population prevention": (0.3, 0.4)})
    R.covout['condcas'][('M 25-49', 'F 50+')].addccopar({'intercept':   (0.01, 0.01),'t':2016. ,  "General population prevention": (0.3, 0.4)})
    R.covout['condcas'][('M 50+', 'FSW')].addccopar({'intercept':       (0.05, 0.05) ,'t':2016. , "General population prevention": (0.2, 0.2), "FSW programs": (0.6, 0.7)})
    R.covout['condcas'][('M 50+', 'F 25-49')].addccopar({'intercept':   (0.01, 0.01),'t':2016. ,  "General population prevention": (0.3, 0.4)})
    R.covout['condcas'][('M 50+', 'F 50+')].addccopar({'intercept':     (0.01, 0.01) ,'t':2016. , "General population prevention": (0.3, 0.4)})

    R.covout['hivtest']['FSW'].addccopar({'intercept': (0.12, 0.12),'t':2016. , "FSW programs": (0.99, 0.99)})
    R.covout['hivtest']['MSM'].addccopar({'intercept': (0.05, 0.05),'t':2016. ,"MSM programs": (0.65, 0.65)})
    R.covout['hivtest']['Clients'].addccopar({'intercept': (0.3,0.3),'t':2016. , "HTC": (0.7, 0.7)})
    R.covout['hivtest']['M 15-24'].addccopar({'intercept': (0.05,0.05),'t':2016. , "HTC": (0.6, 0.6)})
    R.covout['hivtest']['M 25-49'].addccopar({'intercept': (0.1,0.15),'t':2016. , "HTC": (0.85, 0.95)})
    R.covout['hivtest']['M 50+'].addccopar({'intercept':   (0.1,0.15),'t':2016. , "HTC": (0.85, 0.95)})
    R.covout['hivtest']['F 15-24'].addccopar({'intercept': (0.1,0.1),'t':2016. , "HTC": (0.85, 0.95)})
    R.covout['hivtest']['F 25-49'].addccopar({'intercept': (0.2,0.2),'t':2016. , "HTC": (0.85, 0.95)})
    R.covout['hivtest']['F 50+'].addccopar({'intercept':   (0.2,0.2),'t':2016. , "HTC": (0.85, 0.95)})
    
    for parkey in R.covout.keys():
        for popkey in R.covout[parkey].keys():
            R.covout[parkey][popkey].interaction = interaction

    P.addprogset(name='default', progset=R)


## Do reconciliation
if 'reconcile' in torun:
    P.progsets[0].reconcile(year=2015, uselimits=True)



## Compare outcomes under budget and calibration
if 'compareoutcomes' in torun:
    comparison = P.progsets[0].compareoutcomes(parset=P.parsets[0], year=2016, doprint=True)


## Run sanity check budget scenarios
if 'budgetscens' in torun:
        
    ## Define scenarios
    defaultbudget = P.progsets['default'].getdefaultbudget()

    zerobudget = dcp(defaultbudget)
    for key in zerobudget: zerobudget[key] = array([0.])    
    doublebudget = dcp(defaultbudget) 
    for key in doublebudget: doublebudget[key] = array([doublebudget[key]*2])
    infbudget = dcp(defaultbudget) 
    for key in infbudget: infbudget[key] = array([infbudget[key]+1e14])

    nogog = dcp(defaultbudget) 
    nogog['General population prevention'] = 211996.00
    nogog['FSW programs'] = 210619.00
    nogog['MSM programs'] = 127949.00
    nogog['HTC'] = 535310.00
    nogog['ART'] = 861122.
    nogog['PMTCT'] = 110337.00
    nogog['Lab'] = 238616.00

    usgtreat = dcp(defaultbudget) 
    usgtreat['General population prevention'] = 211996.00
    usgtreat['FSW programs'] = 31678.64
    usgtreat['MSM programs'] = 47697.69
    usgtreat['HTC'] = 731105.17
    usgtreat['ART'] = 2084318.
    usgtreat['Lab'] = 974912.40
    usgtreat['PMTCT'] = 405756.24

    optim = dcp(defaultbudget) 
    optim['General population prevention'] = 0.
    optim['FSW programs'] = 609757.103747
    optim['MSM programs'] = 56651.5226374
    optim['HTC'] = 0.
    optim['ART'] = 2644940.28762
    optim['Lab'] = 770358.675995
    optim['PMTCT'] = 405756.24

    lessma = dcp(defaultbudget) 
    lessma['General population prevention'] = 0.
    lessma['FSW programs'] = 658767.006461
    lessma['MSM programs'] = 89576.693833
    lessma['HTC'] = 0.
    lessma['ART'] = 2748037.17366
    lessma['Lab'] = 1110127.12853
    lessma['PMTCT'] = 457925.83751

    nspopt = dcp(defaultbudget) 
    nspopt['General population prevention'] = 453332.2464
    nspopt['FSW programs'] = 477024.1146
    nspopt['MSM programs'] = 334499.091696
    nspopt['HTC'] = 1563394.932
    nspopt['ART'] = 3815320.4496
    nspopt['Lab'] = 2084752.67616
    nspopt['PMTCT'] = 867669.143616

    nspnonopt = dcp(defaultbudget) 
    nspnonopt['General population prevention'] = 699586.8
    nspnonopt['FSW programs'] = 736148.325
    nspnonopt['MSM programs'] = 516202.302
    nspnonopt['HTC'] = 2412646.5
    nspnonopt['ART'] = 5887840.2
    nspnonopt['Lab'] = 1338995.592
    nspnonopt['PMTCT'] = 3217210.92

    step1 = dcp(defaultbudget) 
    step1['General population prevention'] = 211996.0-100000
    step1['FSW programs'] = 223075.25+100000
    step1['MSM programs'] = 156424.94
    step1['HTC'] = 731105-250000
    step1['ART'] = 1433817.54+250000
    step1['Lab'] = 405756.24
    step1['PMTCT'] = 974912.4

    step2 = dcp(defaultbudget) 
    step2['General population prevention'] = 211996.0-200000
    step2['FSW programs'] = 223075.25+200000
    step2['MSM programs'] = 156424.94+200000
    step2['HTC'] = 731105-500000
    step2['ART'] = 1433817.54+500000
    step2['Lab'] = 405756.24+200000
    step2['PMTCT'] = 974912.4-400000

    startyear = 2016.
    endyear = 2020.
    endyear2 = 2030.

    P.scens = odict()
    scenlist = [
#        Parscen(name='Current conditions', parsetname='manualfit', pars=[]),
        Budgetscen(name='Baseline', parsetname='Calibrated', progsetname='default', t=[2017], budget=defaultbudget),
        Budgetscen(name='Optimal', parsetname='Calibrated', progsetname='default', t=[2017], budget=optim),
        Budgetscen(name='Optimal (lower management)', parsetname='Calibrated', progsetname='default', t=[2017], budget=lessma),
        Budgetscen(name='USG more treat', parsetname='manualfit', progsetname='default', t=[2016], budget=usgtreat),
        Parscen(name='Status quo', parsetname='status-quo', pars=[]),
        Parscen(name='PrEP',
              parsetname='status-quo',
              pars=[
              {'name': 'prep',
               'for': ['FSW'],
               'startyear': 2016,
               'endyear': 2018,
               'endval': .9, },]),
        Parscen(name='Treat all',
              parsetname='no-leavecare',
              pars=[
              {'name': 'proptx',   'for': 'tot', 'startyear': startyear, 'endyear': 2018., 'endval': 1., },
                ]),
        Parscen(name='90-90-90',
              parsetname='no-leavecare',
              pars=
              [
              {'name': 'propdx',   'for': 'tot', 'startyear': startyear, 'endyear': endyear, 'endval': .9, },
              {'name': 'propcare',   'for': 'tot', 'startyear': startyear, 'endyear': endyear, 'endval': 1., },
              {'name': 'proptx',   'for': 'tot', 'startyear': startyear, 'endyear': endyear, 'endval': .9, },
              {'name': 'propsupp', 'for': 'tot', 'startyear': startyear, 'endyear': endyear, 'endval': .9,},
              {'name': 'propdx',   'for': 'tot', 'startyear': endyear, 'endyear': endyear2, 'startval':.9, 'endval': .95, },
              {'name': 'proptx',   'for': 'tot', 'startyear': endyear, 'endyear': endyear2, 'startval':.9, 'endval': .95, },
              {'name': 'propsupp', 'for': 'tot', 'startyear': endyear, 'endyear': endyear2, 'startval':.9, 'endval': .95,},
                ]),
        Budgetscen(name='NSP optimal', parsetname='Calibrated', progsetname='default', t=[2017], budget=nspopt),
        Budgetscen(name='NSP non-optimal', parsetname='Calibrated', progsetname='default', t=[2017], budget=nspnonopt),
#        Budgetscen(name='Zero', parsetname='Calibrated', progsetname='default', t=[2017], budget=zerobudget),
#        Budgetscen(name='Step 1', parsetname='manualfit', progsetname='default', t=[2016], budget=step1),
#        Budgetscen(name='Step 2', parsetname='manualfit', progsetname='default', t=[2016], budget=step2),
#        Budgetscen(name='Infinite budget', parsetname='manualfit', progsetname='default', t=[2017], budget=infbudget),
#        Budgetscen(name='No GoG budget', parsetname='manualfit', progsetname='default', t=[2017], budget=nogog),
        ]
    
    # Run the scenarios
    P.addscens(scenlist)
    P.runscenarios(start=2000, end=2020, debug=True) 
     
#    if doplot: pygui(P.results[-1])

    ## Print out key numbers
    if 'printtable' in torun:
    
        from optima import sigfig, blank
        
        blank()
        res = P.results[-1]
        output =  '=========================================\n'
        output += 'Summary table\n'
        output += '=========================================\n'
        for sn in range(10):
            if hasattr(P.scens[sn],'budget'):
                arvbudget = P.scens[sn].budget['ART'][0]
                otherbudget = P.scens[sn].budget[:].sum()-arvbudget
            else:
                arvbudget = P.results[-1].main['numtreat'].tot[sn][17:21].sum()/4.*396.93
                otherbudget = P.progsets[0].getdefaultbudget()[:].sum()-arvbudget
            inf = P.results[-1].main['numinci'].tot[sn][17:21].sum()
            death = P.results[-1].main['numdeath'].tot[sn][17:21].sum()
            output += ' %s:, %s, %s, %s, %s\n' % (sn, arvbudget, otherbudget, inf, death)
        output += '=========================================\n'

    import csv
    resultfile = 'scenresults.csv'
    with open(resultfile, 'w') as f:
        for line in output:
            f.write(line)
    


if '90-90-90' in torun:
    startyear = 2016.
    endyear = 2020.
    endyear2 = 2030
    
#    P.scens = odict()
    defaultbudget = P.progsets['default'].getdefaultbudget()
    
    ## Define scenarios  90-90-90 cost estimate 20.6/10*15.2
    scenlist = [
        Parscen(name='Status quo',
                parsetname='status-quo', 
                pars=[]),
        
        Parscen(name='Treat all',
              parsetname='no-leavecare',
              pars=[
              {'name': 'proptx',   'for': 'tot', 'startyear': startyear, 'endyear': 2018., 'endval': 1., },
                ]),
                
        Parscen(name='90-90-90',
              parsetname='no-leavecare',
              pars=
              [
              {'name': 'propdx',   'for': 'tot', 'startyear': startyear, 'endyear': endyear, 'endval': .9, },
              {'name': 'propcare',   'for': 'tot', 'startyear': startyear, 'endyear': endyear, 'endval': 1., },
              {'name': 'proptx',   'for': 'tot', 'startyear': startyear, 'endyear': endyear, 'endval': .9, },
              {'name': 'propsupp', 'for': 'tot', 'startyear': startyear, 'endyear': endyear, 'endval': .9,},
              {'name': 'propdx',   'for': 'tot', 'startyear': endyear, 'endyear': endyear2, 'startval':.9, 'endval': .95, },
              {'name': 'proptx',   'for': 'tot', 'startyear': endyear, 'endyear': endyear2, 'startval':.9, 'endval': .95, },
              {'name': 'propsupp', 'for': 'tot', 'startyear': endyear, 'endyear': endyear2, 'startval':.9, 'endval': .95,},
                ]),
        ]

    # Store these in the project
    P.addscens(scenlist)

    # Run the scenarios
    P.runscenarios()
    if doplot: pygui(P)


if 'prep' in torun:
    startyear = 2016.
    endyear = 2020.
    
#    P.scens = odict()
    scenlist = [
        Parscen(name='Status quo',
                parsetname='status-quo', 
                pars=[]),
        
        Parscen(name='PrEP',
              parsetname='status-quo',
              pars=[
              {'name': 'prep',
               'for': ['FSW'],
               'startyear': startyear,
               'endyear': 2018,
               'endval': .9, },
                ])]

    # Store these in the project
    P.addscens(scenlist)

    # Run the scenarios
    P.runscenarios()
    if doplot: pygui(P)
    

## Do a basic optimization
if 'minoutcomes' in torun:

    objectives = defaultobjectives(P.progsets[0]) 
    objectives['start'] = 2017.
    objectives['end'] = 2030.
    objectives['deathweight'] = 1
    objectives['inciweight'] = 5
#    objectives['budgetscale'] = [0.5, 0.6, 0.7, .8, .9, 1., 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.]
#    constraints = defaultconstraints(P.progsets[0])

    objectives2 = defaultobjectives(P.progsets[0]) 
    objectives2['start'] = 2017.
    objectives2['end'] = 2030.
    objectives2['deathweight'] = 1
    objectives2['inciweight'] = 5
    objectives2['budget'] = 5064433.8399999999

    maxtime = 1000
    randseed = 27042007
    P.optims = odict()
    P.optimize(name='Basic optimization', parsetname='Calibrated', progsetname='default', objectives=objectives, maxtime=maxtime, randseed=randseed, mc=3)
    P.optimize(name='Lower management', parsetname='Calibrated', progsetname='default', objectives=objectives2, maxtime=maxtime, randseed=randseed, mc=3)
    
    print('Original allocation: '),
    print(P.optims[0].getresults().budgets[0])
    print('Optimal allocation: '),
    print(P.optims[0].getresults().budgets[1])

#    P.scens = odict()
#    scenlist = [
#        Budgetscen(name='Current', parsetname='Calibrated', progsetname='default', t=[2016], budget=P.optims[0].getresults().budgets[0]),
#        Budgetscen(name='Optimal', parsetname='Calibrated', progsetname='default', t=[2016], budget=P.optims[0].getresults().budgets[1]),
#        Budgetscen(name='Optimal (lower management)', parsetname='Calibrated', progsetname='default', t=[2016], budget=P.optims[1].getresults().budgets[1]),
#        ]
#    
#    # Run the scenarios
#    P.addscenlist(scenlist)
#    P.runscenarios(start=2000, end=2030, debug=True) 
     
    if doplot:
#        plotallocations(P)
        pygui(P.results[-1])





if 'minmoney' in torun:

    print('Running minimize money for Guyana...')
    
    objectives = defaultobjectives(P.progsets[0], which='money')
#    objectives['deathfrac'] = 0.5
    objectives['incifrac'] = 0.25
    objectives['base'] = 2012
    objectives['start'] = 2017
    objectives['end'] = 2020
    P.optimize(name='Achive NSP', parsetname='Calibrated', progsetname='default', objectives=objectives, maxtime=500, ccsample='best')
    
    print('Original allocation: ($%g)' % sum(P.results[-1].budgets[0][:]))
    print(P.results[-1].budgets[0])
    print('Optimal allocation: ($%g)' % sum(P.optims[-1].getresults().budgets[1][:]))
    print(P.optims[-1].getresults().budgets[1]) # Showing that results are "stored" in the optimization -- same object as before
    if doplot: 
        pygui(P)



if 'minmoneyscen' in torun:
    
    ## Define scenarios
    defaultbudget = P.progset().getdefaultbudget()

    factor = 3.3
    nspbudget = dcp(defaultbudget) 
    for key in nspbudget: nspbudget[key] = array([nspbudget[key]*factor])
    
    P.scens = odict()
    
    scenlist = [
        Budgetscen(name='Achieved NSP', parsetname='no-leavecare', progsetname='default', t=[2016], budget=nspbudget),
        Parscen(name='Status quo',
                parsetname='Calibrated',
                pars=[]),
        ]
    
    # Run the scenarios
    P.addscens(scenlist)
    P.runscenarios(debug=False, end=2020) 
    


# Prepare the budgets for GA by removing ART and PMTCT, resetting intercepts and removing USG spending
if 'preparegaprogs' in torun:
    P.copyprogset(orig='default', new='gaprogs')

    P.progsets[1].programs['General population prevention'].costcovdata = odict({'cost': [211996.00],'t': [2016]})
    P.progsets[1].programs['FSW programs'].costcovdata = odict({'cost': [31678.64],'t': [2016]})                    
    P.progsets[1].programs['MSM programs'].costcovdata = odict({'cost': [47697.69],'t': [2016]})
    P.progsets[1].programs['HTC'].costcovdata = odict({'cost': [107516.67], 't': [2016]})
    P.progsets[1].programs['ART'].costcovdata = odict({'cost': [479339.97],'t': [2016]})
    P.progsets[1].programs['PMTCT'].costcovdata = odict({'cost': [736296.84],'t': [2016],})   
    P.progsets[1].programs['Lab'].costcovdata = odict({'cost': [295419.05],'t': [2016],})   

    P.progsets[1].covout['numtx']['tot'].ccopars = odict({'intercept': [4791.],'t': [2016],})   
    P.progsets[1].covout['numpmtct']['tot'].ccopars = odict({'intercept': [131.],'t': [2016],})   



## Save GA project
if 'savegaproject' in torun:
    print('  Saving project for GA')
    P.scens=odict()
    P.optims=odict()
    theparset = dcp(P.parsets['Calibrated'])
    theprogset = dcp(P.progsets['gaprogs'])
#    theprogset = dcp(P.progsets['default'])
    P.parsets=odict()
    P.progsets=odict()
    P.addparset('Calibrated',theparset)
    P.addprogset('nousg',theprogset)
    
    P.save(filename=projectfile, saveresults=False)



## Save project
if 'saveproject' in torun or 'trainingexample' in torun:
    print('  Saving project')
    P.save(filename=projectfile, saveresults=saveresults)
     
     

## Make subdivision sheet
if 'makesubdividesheet' in torun:
    print("  Generating Guyana subdivide sheet")
    
    geo.makesheet(projectpath=projectfile, spreadsheetpath='guyana-geospatial-division-'+str(ndistricts)+'-districts-template.xlsx', copies=ndistricts, refyear=2014)









#%% 
#OLD ANALYSES
if 'minoutcomefixedart' in torun:
    
    P.copyprogset(orig='default', new='scale-up')
    P.progsets['scale-up'].rmprogram('ART')
    P.progsets['scale-up'].rmprogram('PMTCT')
    
    P.copyparset('Calibrated','scale-up') # So it's the last
    
    P.pars()['proptx'].t['tot'] = array([0, 2015, 2020])
    P.pars()['proptx'].y['tot'] = array([nan, 0.68, 0.9]) # eyeballed
    
    if doplotbasics: 
        P.runsim()
        pygui(P)
    
    if not 'savescaleup' in torun:
        objectives = defaultobjectives(P.progsets['scale-up']) 
        objectives['start'] = 2016.
        objectives['end'] = 2030.
        objectives['budget'] = P.progsets['scale-up'].getdefaultbudget()[:].sum()
        constraints = defaultconstraints(P.progsets[0])
    
        maxtime = 30
        randseed = 1
        P.optimize(name='minoutcomefixedart', parsetname='scale-up', progsetname='scale-up', objectives=objectives, constraints=constraints, method='asd', maxtime=maxtime, randseed=randseed)
        
        print('Original allocation: '),
        print(P.results[-1].budget[0])
        print('Optimal allocation: '),
        print(P.optims[-1].getresults().budget[1]) # Showing that results are "stored" in the optimization -- same object as before
    
        if doplot:
            plotallocations(P)
            pygui(P.results[-1])
    
    # Use this for running geospatial -- WARNING, should be automated!
    if 'savescaleup' in torun:
        Q = Project(spreadsheet=spreadsheetfile, dorun=False)
        Q.parsets[0] = P.parsets['scale-up']
        Q.progsets[0] = P.progsets['scale-up']
        Q.parsets[0].name = 'default'
        Q.progsets[0].name = 'default'
        Q.parsets[0].project = Q
        Q.progsets[0].project = Q
        Q.runsim()
        Q.save(filename=projectfile, saveresults=True)
        

