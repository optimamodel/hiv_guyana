"""
Can run as a script, and will do the things in torun list. Otherwise, can pick
and choose by running from command line:

python batchguyana.py export

General workflow:
1. Run guyana.py to generate guyana.prj
2. Run this file to generate results
3. Run dataforguyanaplots.py to generate guyana-plotdata.dat
4. Run plotguyanageo.py to make actual plots

Version: 2016sep28
"""

from optima import batchautofit, batchBOC, runcommand,  Portfolio, loadobj, saveobj, uuid, defaultobjectives
from optima import _geospatial as geo
from sys import argv
from os.path import abspath
from os import sep
from glob import glob

# Set which analyses you want to run
torun = [
'makeprojects',
#'calibrate',
#'updateregion4budget',
#'bocs',
#'makeportfolio',
#'rungeo',
#'export',
]

projectname = 'files/prj/guyana.prj'
portfolionamein = 'files/guyana-bocs.prt'
portfolionameout = 'files/guyana-gpa.prt'
spreadsheetpath = 'guyana-geospatial-division-10-districts.xlsx'

# Folders for the different steps
districtfolder = 'files/prj/guyana-01-initial'
calibratedfolder = 'files/prj/guyana-02-calibrated'
bocsfolder = 'files/prj/guyana-05-bocs'
outputname = 'guyana-geospatial-results.xlsx'

maxtime = 120
maxiters = 120

if len(argv)>1: torun=argv[1:] # If run from command line, use this instead


print('Running: %s\n\n\n' % torun)

if 'makeprojects' in torun:
    print('Making projects...')
    destination = abspath(districtfolder)
    runcommand('mkdir -p %s' % districtfolder)
    geo.makeproj(projectpath=projectname, spreadsheetpath=spreadsheetpath, destination=destination, checkplots=False)
    

if 'calibrate' in torun:
    print('Calibrating...')
    runcommand('mkdir -p %s' % calibratedfolder)
    runcommand('cp -r %s/* %s/' % (districtfolder, calibratedfolder))
    batchautofit(abspath(calibratedfolder))


if 'updateregion4budget' in torun:
    print('Updating budget for Region 4...')
    from optima import loadproj
    P = loadproj(districtfolder+'/Demerara-Mahaica.prj')
    P.progsets[0].programs['FSW programs'].costcovdata['cost'][0] +=  191397.
    P.progsets[0].programs['MSM programs'].costcovdata['cost'][0] +=  108727.
    P.progsets[0].programs['HTC'].costcovdata['cost'][0] +=  456460.
#    P.progsets[0].programs['ART'].costcovdata['cost'][0] +=   954478.
#    P.progsets[0].programs['PMTCT'].costcovdata['cost'][0] +=    110337.
    P.progsets[0].programs['Lab'].costcovdata['cost'][0] += 238616.
    P.save(districtfolder+'/Demerara-Mahaica.prj')
        

if 'bocs' in torun:
    print('Making BOCs...')
    runcommand('mkdir -p %s' % bocsfolder)
    runcommand('cp -r %s/*.prj %s/' % (calibratedfolder, bocsfolder))
    batchBOC(abspath(bocsfolder), maxiters=maxiters)


if 'makeportfolio' in torun:
    print('Making portfolio...')
    F = Portfolio()
    projlist = []
    filelist = glob(abspath(bocsfolder)+sep+'*.prj')
    for fi in filelist:
        tmpproj = loadobj(fi)
        tmpproj.uid = uuid()
        projlist.append(tmpproj)
    F.addprojects(projlist)
    saveobj(portfolionamein, F)


if 'rungeo' in torun:
    print('Performing geospatial analysis...')  
    F = loadobj(portfolionamein)
    objectives = defaultobjectives(F.projects[0].progsets[0]) 
    objectives['budget'] = 2130385.# P.progset().getdefaultbudget()[:].sum()

    objectives['start'] = 2016.
    objectives['end'] = 2030.
    objectives['deathweight'] = 1
    objectives['inciweight'] = 5
    import traceback; traceback.print_exc(); import pdb; pdb.set_trace()

    F.fullGA(objectives, doplotBOCs=False, budgetratio=F.getdefaultbudgets(), maxtime=maxtime)
    saveobj(portfolionameout, F)
    

if 'export' in torun:
    print('Exporting geospatial results...')
    F = loadobj(portfolionameout)
    geo.export(portfolio=F, filepath=outputname)
    
