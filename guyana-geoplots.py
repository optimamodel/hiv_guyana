# -*- coding: utf-8 -*-
"""
Created on Tue Dec 27 16:30:12 2016

@author: robynstuart
"""

## IMPORTS
from optima import vectocolor, odict, loadobj, dcp, gridcolormap, findinds
from pylab import figure, hold, subplot, axis, savefig, gca, \
                  Polygon, colorbar, title, scatter, concatenate, ndim, size, \
                  clim, array, append, arange, legend, zeros, barh, xlabel, ylim
import shapefile as sh
from matplotlib import pyplot, cm, ticker
from xlrd import open_workbook  # For opening Excel workbooks

torun = [
'loadgis',
'loadresults',
'prevplhiv',
'districtstackedbars',
'outcomemaps',
]


## FILEPATHS
figpath = 'files/figs/'    
gisfile = 'gis/GUY_adm1.shp'
spreadsheetpath = 'guyana-geospatial-results.xlsx' # Need to download this
portfoliopath = 'files/guyana-bocs.prt' # Need to download this -- don't need GPA
ndistricts = 10 # Could be calculated, but this is easier
nprograms = 7 # does not include ART
curryear = 2016

correction = 1 #3.6/5.77 # used wrong budget
if correction != 1: print('WARNING, using corrected budgets!')

dpi = 300
mapsize = (4.5,5)
dosave = True



def plotmap(data, names, gisfile, gisnames=None, titles=[''], figsize=(7,6), cmap=None, dotickformat=True, zeropoint=False, nameindex=4):
    
    def plotshape(points, color):
        polygon = Polygon(points, color=color)
        gca().add_patch(polygon)
        axis('scaled')
        return None

    # Read in data and get names
    sf = sh.Reader(gisfile)
    if gisnames is None:
        numregions = sf.numRecords
        gisnames = []
        for i in range(numregions): gisnames.append(sf.record(i)[nameindex])
        
    
    # Calculate number of maps
    if ndim(data)==1: nmaps = 1
    else: nmaps = size(data,0)
    
    # Process colors
    if nmaps==1:
        if zeropoint:
            maxval = abs(data).max()
            minval = -abs(data).max()
            newdata = append(data, [maxval, minval])
            newcolors = vectocolor(newdata, cmap=cm.get_cmap(cmap))
            colors = [newcolors[:-2,:]]
        else:
            colors = [vectocolor(data, cmap=cm.get_cmap(cmap))]
            
        
    else:
        colors = []
        for m in range(nmaps):
            tmp = vectocolor(concatenate(([0], [data.min()], data[m,:], [data.max()])))
            colors.append(tmp[2:-1])
            
    
    # Create figure
    fig = figure(facecolor=(1,1,1), figsize=figsize)
    
    ax = []
    for m in range(nmaps):
        ax.append(subplot(1,nmaps,m+1))
        ax[-1].get_xaxis().set_visible(False)
        ax[-1].get_yaxis().set_visible(False)
        hold(True)
        
        for i,name in enumerate(names):
            try:
                if isinstance(gisnames,dict):
                    for match in gisnames[name]:
                        pts = array(sf.shape(match).points)
                        plotshape(pts, colors[m][i])
                else:
                    match = gisnames.index(name)
                    plotshape(sf.shape(match).points, colors[m][i])
            except:
                print('Name "%s" not matched to GIS file' % name)
        xlims = ax[-1].get_xlim()
        ylims = ax[-1].get_ylim()
        scatter(data,data,c=data)
        ax[-1].set_xlim(xlims)
        ax[-1].set_ylim(ylims)
        title(titles[m], fontsize=13)
    
    if dotickformat: colorbar(format=ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    else: colorbar()
    if cmap is not None: pyplot.set_cmap(cmap)
#    clim(0,abs(data).max())
    if zeropoint:
        clim(minval,maxval)
    return fig


if 'loadgis' in torun:
    print('Loading GIS...')
    # Read in data and get names
    sf = sh.Reader(gisfile)
    numregions = sf.numRecords
    gisnames = []
    for i in range(numregions): gisnames.append(sf.record(i)[4])
    origgisnames = dcp(gisnames)
   




if 'loadresults' in torun:
    print('Loading results...')
    
    #%% Define parameters
    colors = gridcolormap(nprograms)
    namekeys = ['distnames','prognames']
    distkeys = ['popsize', 'numplhiv', 'prev']
    initoptkeys = ['budget','outcome','deaths','infections']
    arraykeys = ['alloc','coverage']
    
    
    #%% Load data
    print('Loading spreadsheet...')
    
    # Read the thing
    def getvals(row, cols=(2,3), newrow=True, verbose=False): # Default to columns 2 & 3
        output = []
        if type(cols)!=tuple: cols = (cols,)
        for col in cols: 
            val = sheet.cell_value(row,col)
            if verbose: print('row=%i, col=%i, val=%s' % (row, col, val))
            output.append(val)
        if newrow: 
            row += 1
            return output, row
        else:
            return output
    
    # Initialize for storing data
    D = odict()
    for key in namekeys:    D[key] = []
    for key in distkeys:    D[key] = zeros(ndistricts)
    for key in initoptkeys: D[key] = zeros((2, ndistricts))
    for key in arraykeys:   D[key] = zeros((2, ndistricts, nprograms))
    
    # Open the thing
    workbook = open_workbook(spreadsheetpath)
    sheet = workbook.sheet_by_index(0)
    nheaderlines = 9
    row = nheaderlines
    noptprograms = nprograms
    for di in range(ndistricts):
        row += 3
        rawname, row = getvals(row,0)
        distname = str(rawname[0][10:-1]) # Cut out 'Project: ""'
        D['distnames'].append(distname)
        row += 1
        for key in initoptkeys:
            D[key][:,di], row     = getvals(row)
        row += 2
        for p in range(noptprograms):
            if di==0: D['prognames'].append(str(getvals(row,1,newrow=False)[0])) # Once-off to get program names
            D['alloc'][:,di,p], row = getvals(row)
        row += 2
        for p in range(noptprograms):
            D['coverage'][:,di,p], row = getvals(row)
        
    # Now, read the portfolio data for population size, prevalence, PLHIV
    print('Loading portfolio...')
    F = loadobj(portfoliopath)
    projlist = {prj.name:prj for prj in F.projects[:]}
    for pr,projname in enumerate(D['distnames']):
        try: P = projlist[projname]
        except: raise Exception("District %s not found" % projname)
        if pr==0: D['fullprognames'] = [P.progsets[0].programs[i].name for i in D['prognames']] # Get full names of the programs
        try: P.results[-1].main[key].tot[0] # First try to see if it already exists
        except: P.runsim() # If not, run
        yearind = findinds(P.results[-1].tvec, curryear)[0]
        for key in distkeys:
            D[key][pr] = P.results[-1].main[key].tot[0][yearind]
    
    
    # This is used several times so pull it out here
    
    # Use medium length labels
    ppd = odict()
    ppd['General population prevention'] = (1,0.4,0.3)
    ppd['Prevention programs for FSW'] = (0.8,0.2,.7)
    ppd['Prevention programs for MSM'] = (0.6,0.2,.7)
    ppd['HTC'] = (0,1.0,0)
    ppd['ART'] = (0,0.5,1.0)
    ppd['PMTCT'] = (0.0,0.1,1.0)
    ppd['Lab monitoring']= (0,0.8,0.8)

    current = D['alloc'][0,:,:]
    optimal = D['alloc'][1,:,:]
    currentsum = current.sum(axis=0)
    optimalsum = optimal.sum(axis=0)
    proglabels = ppd.keys()
    progcolors = ppd.values()
    
    # WARNING, messes with GIS file
#    distnames = [
#    '                   Barima-Waini',
#    '              Pomeroon-Supenaam',
#    'Essequibo Islands-West Demerara',
#    '               Demerara-Mahaica',
#    '                Mahaica-Berbice',
#    '         East Berbice-Corentyne',
#    '                Cuyuni-Mazaruni',
#    '                Potaro-Siparuni',
#    '   Upper Takutu-Upper Essequibo',
#    '         Upper Demerara-Berbice']
#    D['distnames'] = distnames
#    
#    distnames = [
#    'Barima-Waini',
#    'Pomeroon-Supenaam',
#    'Essequibo Islands-West Demerara',
#    'Demerara-Mahaica',
#    'Mahaica-Berbice',
#    'East Berbice-Corentyne',
#    'Cuyuni-Mazaruni',
#    'Potaro-Siparuni',
#    'Upper Takutu-Upper Essequibo',
#    'Upper Demerara-Berbice']
#    D['distnames'] = distnames
    
    
    print('Done loading results')
    








if 'prevplhiv' in torun:

#    'Barima-Waini',
#    'Pomeroon-Supenaam',
#    'Essequibo Islands-West Demerara',
#    'Demerara-Mahaica',
#    'Mahaica-Berbice',
#    'East Berbice-Corentyne',
#    'Cuyuni-Mazaruni',
#    'Potaro-Siparuni',
#    'Upper Takutu-Upper Essequibo',
#    'Upper Demerara-Berbice']

    prevdata = odict({
    'Barima-Waini': 0.004702566,
    'Pomeroon-Supenaam': 0.009980262,
    'Essequibo Islands-West Demerara': 0.005381241,
    'Demerara-Mahaica': 0.018391654,
    'Mahaica-Berbice': 0.003025693,
    'East Berbice-Corentyne': 0.005861021,
    'Cuyuni-Mazaruni': 0.00273312,
    'Potaro-Siparuni': 0.00077706,
    'Upper Takutu-Upper Essequibo': 0.000327038,
    'Upper Demerara-Berbice': 0.000602117})
    prevdata = prevdata.sort(D['distnames'])
    
    plhdata = odict({
    'Barima-Waini': 132.9716599,
    'Pomeroon-Supenaam': 490.332996,
    'Essequibo Islands-West Demerara': 606.6831984,
    'Demerara-Mahaica': 6050.210526,
    'Mahaica-Berbice': 157.9038462,
    'East Berbice-Corentyne': 673.1690283,
    'Cuyuni-Mazaruni': 58.17510121,
    'Potaro-Siparuni': 8.310728745,
    'Upper Takutu-Upper Essequibo': 8.310728745,
    'Upper Demerara-Berbice': 24.93218623})
    plhdata = plhdata.sort(D['distnames'])

    spenddata = odict({
    'Barima-Waini': 68801.,
    'Pomeroon-Supenaam': 119543.17781954567,
    'Essequibo Islands-West Demerara': 274318.52144123736,
    'Demerara-Mahaica': 2860448.63983769256,
    'Mahaica-Berbice': 126982.38476225741,
    'East Berbice-Corentyne': 279464.41982419783,
    'Cuyuni-Mazaruni': 51790.977273667726,
    'Potaro-Siparuni': 26023.178423011548,
    'Upper Takutu-Upper Essequibo': 61832.50205868062,
    'Upper Demerara-Berbice': 100752.34888563803})
    spenddata = spenddata.sort(D['distnames'])
    
    # PLHIV
    plotmap(plhdata[:], D['distnames'], gisfile, titles=['PLHIV in 2014'], figsize=mapsize, cmap='YlOrRd')
    if dosave: savefig(figpath+'guyana-plhiv-map.png', dpi=dpi)
    
    # Prevalence 
    plotmap(prevdata[:]*100, D['distnames'], gisfile, titles=['HIV prevalence in 2014 (%)'], figsize=mapsize, cmap='YlOrRd', dotickformat=False)
    if dosave: savefig(figpath+'guyana-prev-map.png', dpi=dpi)

    # Spend
    plotmap(spenddata[:]/1e6, D['distnames'], gisfile, titles=['2015 spending (US$m)'], figsize=mapsize, cmap='Greens', dotickformat=False)
    if dosave: savefig(figpath+'guyana-spend-map.png', dpi=dpi)

    # Spend per PLHIV
    plotmap(spenddata[:]/plhdata[:], D['distnames'], gisfile, titles=['2015 spend per PLHIV (US$)'], figsize=mapsize, cmap='Greens')
    if dosave: savefig(figpath+'guyana-spendperplh-map.png', dpi=dpi)


if 'districtstackedbars' in torun:
    scalefactor = 1e-6*correction
    fig = figure(facecolor=(1,1,1), figsize=(12,6))
    ax = fig.add_subplot(1,1,1)
    
    for di in range(ndistricts):
        for i in range(nprograms):
            xdata = array([1,2])+3*di
            ydata = array([current[di,i],optimal[di,i]])*scalefactor
            bottomdata = array([sum(current[di,:i]),sum(optimal[di,:i])])*scalefactor
            label=proglabels[i] if di==0 else ''
            barh(xdata, ydata, left=bottomdata, color=progcolors[i], linewidth=0, label=label)
    
    ax.set_yticks(arange(ndistricts)*3+2)
    ax.set_yticklabels(D['distnames'], rotation=0)
    ax.set_position([0.3, 0.1, 0.6, 0.8])
    xlabel('Spending (US$m)')
    ylim([0,ndistricts*3])
    legend(loc=(0.55,0.6), frameon=False, fontsize=12)
    if dosave: savefig(figpath+'guyana-districtstackedbars.png', dpi=dpi)

   
   
   

if 'outcomemaps' in torun:
    
    plotdata = D['infections'][0,:]-D['infections'][1,:]
    plotmap(plotdata, D['distnames'], gisfile, titles=['New infections prevented'], figsize=mapsize, cmap='Greens')
    if dosave: savefig(figpath+'guyana-newinfectionsmap.png', dpi=dpi)
    
    plotdata = D['deaths'][0,:]-D['deaths'][1,:]
    plotmap(plotdata, D['distnames'], gisfile, titles=['HIV-related deaths prevented'], figsize=mapsize, cmap='Greens')
    if dosave: savefig(figpath+'guyana-deathsmap.png', dpi=dpi)
    
    plotdata = (D['budget'][0,:])/1e6
    plotmap(plotdata, D['distnames'], gisfile, titles=['Spend per region 2015 (US$)'], figsize=mapsize, cmap='Greens', dotickformat=False)
    if dosave: savefig(figpath+'guyana-currentspend.png', dpi=dpi)

    plotdata = (D['budget'][1,:]-D['budget'][0,:])
    plotmap(plotdata/1e3, D['distnames'], gisfile, titles=['Change in funding (US$th)'], figsize=mapsize, cmap='seismic_r', zeropoint=True)
    if dosave: savefig(figpath+'guyana-fundingmap.png', dpi=dpi)

print('Done.')
