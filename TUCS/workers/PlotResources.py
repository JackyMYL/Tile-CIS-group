#!/bin/env python
# Author: Joshua Montgomery <Joshua.J.Montgomery@cern.ch>
# March 01, 2012
#
# Resource Plotting Module 
# Makes plots of the memory use
# Could be adapted in the future to 
# do CPU use relatively easily.


def makeplots(MemLog=None, TimeLine=None, Output=None):
    
    import os
    import sys
    import ROOT
    from ROOT import TCanvas, TPad, TH1F
    import src.MakeCanvas
    import re

    memorylog = MemLog
    timelog   = TimeLine
    pname     = Output
    plotmem   = []
    workers   = []
    dupchecks = []
    
    
    
    for entry in memorylog:
        memper  = round(float(entry.split('_')[1]), 2)
        memtime = round(float(entry.split('_')[3]), 2)
        plotmem.append((memtime, memper))
    
    commandl = None
    for entry in timelog:
        if '+' in entry:
            firstworker = entry.split(' ')[0]
            if (firstworker in dupchecks) and (dupchecks.count(firstworker)>2) and (dupchecks.count(firstworker) % 2 ==1):
                        noccur = dupchecks.count(firstworker)
                        noccur = str(((noccur - 1)/2)+1) #grrrr
                        worker = '{0}_#{1}'.format(firstworker, noccur)
            else:
                worker = firstworker
            dupchecks.append(firstworker)
            wtime  = round(float(entry.split('+')[1]), 2)
            workers.append((wtime, worker))
        else:
            commandl = re.sub(r'[\x00]', ' ',str(entry)).replace('_', '\_')
            commandlist = commandl.split('--')
            print(commandlist)

    plotnames = 'Resource Plots PID: {0}'.format(pname)
    workersmax = max(workers, key=lambda x: x[0])[0]
    memlistmax = max(plotmem, key=lambda x: x[0])[0]
    
    globalmax  = max(workersmax, memlistmax)
    
    maxtimebin = plotmem[-1][0]
    colors     = []
    numworkers = (len(workers)-2)/2
    for iter in range(1, numworkers+1):
        colors.append([])
        for point in plotmem:
            # print point[0], workers[2*iter - 1][0], workers[2*iter][0]
            if point[0] > workers[2*iter - 1][0] and point[0] < workers[2*iter][0]:
                colors[iter-1].append((point[0], point[1], workers[2*iter][1]))
    
#     c1 = src.MakeCanvas.MakeCanvas()
#     c1.Clear()
#     c1.cd(0)

    #######################    #######################    ######################
    can = ROOT.TCanvas('can', 'can')
    #ROOT.SetOwnership(can, False)
    tpad0 = ROOT.TPad("0", 'plot pad', 0.0, 0.0, 0.75, 1.0)
    tpad1 = ROOT.TPad("1", "Info Pad", 0.75, 0.0, 1.0, 1.0)
    tpad0.SetBorderMode(0)
    tpad1.SetBorderMode(0)
    tpad0.SetBorderSize(0)
    tpad1.SetBorderSize(0)
    
    tpad0.Draw()
    tpad1.Draw()


    #######################    #######################    ######################
    
    rootlist   = []
    wcounter   = 0
    memdeltas  = []
    memcounter = 0
    for wmemory in colors:
        if wmemory:
            memdeltas.append([])
            memin      = wmemory[0][1]
            memax      = wmemory[-1][1]
            mdiff      = memax - memin
            memname    = wmemory[0][2]
            memdeltas[memcounter].append((mdiff, memname))
            memcounter = memcounter + 1        
            rootlist.append([])
            rootlist[wcounter] = ROOT.TH1F(wmemory[0][2], wmemory[0][2], 100000,
                                           0, 1)
            pcounter = 0
            for point in wmemory:
                rootlist[wcounter].Fill(float(point[0])/globalmax, float(point[1]))
                pcount     = pcounter + 1
            wcounter       = wcounter + 1
        
    ####################### THIS IS THE SUMMARY HISTOGRAM ##########################
    tpad0.cd()
    histobins    = len(memdeltas) 
    # print histobins
    sumhist      = ROOT.TH1F('memsummary', '', histobins, 0, histobins)
    sumhistcount = 0
    for summary in memdeltas:
        sumhist.Fill(summary[0][1], summary[0][0])
    maxsumbin = sumhist.GetMaximumBin()
    maxsumval = sumhist.GetBinContent(maxsumbin)
    sumhist.SetStats(0)
    #sumhist.SetMaximum(1.5*maxsumval)
    sumhist.SetMaximum(3)
    sumhist.GetYaxis().SetTitle("% Available Memory Used")
    sumhist.GetYaxis().SetTitleSize(.04)
    sumhist.GetYaxis().CenterTitle()
    sumhist.GetXaxis().SetLabelSize(0.03)
    sumhist.Draw("hist")
    
    latex = ROOT.TLatex()
    latex.SetTextAlign(12)
    latex.SetTextSize(0.03)
    latex.SetNDC()
    latex.DrawLatex(0.19, 0.97, plotnames)
  
    can.cd()
    latex3 = ROOT.TLatex()
    latex3.SetTextAlign(12)
    latex3.SetTextSize(0.025)
    latex3.SetNDC()
    latex3.DrawLatex(0.65, 0.97, 'Macro: {0}'.format(commandlist[0].replace('\\', '')))
    
    latex4 = ROOT.TLatex()
    latex4.SetTextAlign(12)
    latex4.SetTextSize(0.025)
    latex4.SetNDC()
    latex4.DrawLatex(0.7, 0.90, 'Arguments:')
    
    latargs    = []
    argcounter = 0
    for arg in commandlist[1:]:
        arg = arg.replace('\\', '')
        if 'region' in arg:
                rargs  = arg.split(' ')
                rtitle = rargs[0]
                rregs  = rargs[1:-1]                
                latargs.append(ROOT.TLatex())
                latargs[argcounter].SetTextAlign(12)
                latargs[argcounter].SetTextSize(0.025)
                latargs[argcounter].SetNDC()
                latargs[argcounter].DrawLatex(0.7, 0.86 - 0.03*(1+argcounter),
                '--{0}'.format(rtitle))
                argcounter = argcounter + 1
                
                for regs in rregs:
                    latargs.append(ROOT.TLatex())
                    latargs[argcounter].SetTextAlign(12)
                    latargs[argcounter].SetTextSize(0.025)
                    latargs[argcounter].SetNDC()
                    latargs[argcounter].DrawLatex(0.75, 0.86 - 0.03*(1+argcounter),
                    '{0}'.format(regs.replace('\\','')))
                    argcounter = argcounter + 1
        else:
        
            latargs.append(ROOT.TLatex())
            latargs[argcounter].SetTextAlign(12)
            latargs[argcounter].SetTextSize(0.025)
            latargs[argcounter].SetNDC()
            latargs[argcounter].DrawLatex(0.7, 0.86 - 0.03*(1+argcounter),
            '--{0}'.format(arg))
            argcounter = argcounter + 1

    can.Modified()       
    can.Print("ResourceLogs/ResourcesSummary_{0}.root".format(pname))
    can.Print("ResourceLogs/ResourcesSummary_{0}.eps".format(pname))
    can.Clear()
    
    
    can2 = ROOT.TCanvas('can2', 'can2')
    #ROOT.SetOwnership(can, False)
    tpad2 = ROOT.TPad("0", 'plot pad', 0.0, 0.0, 0.7, 1.0)
    tpad3 = ROOT.TPad("1", "Info Pad", 0.7, 0.0, 1.0, 1.0)
    tpad2.SetBorderMode(0)
    tpad3.SetBorderMode(0)
    tpad2.SetBorderSize(0)
    tpad3.SetBorderSize(0)

    tpad2.Draw()
    tpad3.Draw()

    
    tpad2.cd()
    memuse = ROOT.TH1F('memuseage', "", 100000, 0, 1)
    for points in plotmem:
        memuse.Fill(float(points[0])/globalmax, float(points[1]))
    memuse.SetLineColor(1)
    memuse.SetLineWidth(2)
    memuse.SetStats(0)
    maxbin = memuse.GetMaximumBin()
    maxval = memuse.GetBinContent(maxbin)
    #memuse.SetMaximum(1.5*maxval)
    memuse.SetMaximum(10)
    memuse.GetXaxis().SetTitle("Fractional Duration Of Entire Process")
    memuse.GetXaxis().SetTitleSize(.04)
    memuse.GetXaxis().SetTitleOffset(1.5)
    memuse.GetXaxis().CenterTitle()
    memuse.GetYaxis().SetTitle("% Available Memory Used")
    memuse.GetYaxis().SetTitleSize(.04)
    memuse.GetYaxis().CenterTitle()
    memuse.GetXaxis().SetRangeUser(0, plotmem[-1][0])
    memuse.Draw("L")
    
    collist   = [2, 3, 5, 4, 6, 7, 8, 9, 12, ROOT.kPink -3, 29, ROOT.kRed + 2, 
                 ROOT.kMagenta - 3, ROOT.kCyan + 3, 46, 30, 49, 41, 43, 24]

    leg = ROOT.TLegend(-0.15,0.4,0.5,0.95)
    leg.SetFillColor(0)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.042)
    leg.AddEntry(memuse,"Memory","L")

        
    csettings = 0  
    for roothing in rootlist:
        roothing.SetLineColor(collist[csettings])
        roothing.SetLineWidth(2)
        roothing.Draw('L,Same')
        lname = roothing.GetTitle()
        leg.AddEntry(roothing, lname, "L")
        csettings = csettings + 1  
        if csettings > 20:
            print('ERROR: PALETTE OUT OF ENTRIES.')
            print('IF MORE THAN 20 WORKERS ARE BEING USED')
            print('A LARGER PALETTE MUST BE GENERATED IN THE')
            print('PLOTRESOURCES.PY MODULE')
            
    tpad3.cd()
    leg.Draw("Same")
    tpad2.cd()
    latex = ROOT.TLatex()
    latex.SetTextAlign(12)
    latex.SetTextSize(0.03)
    latex.SetNDC()
    latex.DrawLatex(0.18, 0.97, plotnames)
    
    latex2 = ROOT.TLatex()
    latex2.SetTextAlign(12)
    latex2.SetTextSize(0.03)
    latex2.SetNDC()
    latex2.DrawLatex(0.60, 0.89, 'Total Time: {0} [s]'.format(str(globalmax)))
        
    can2.cd()
    
    latex4 = ROOT.TLatex()
    latex4.SetTextAlign(12)
    latex4.SetTextSize(0.025)
    latex4.SetNDC()
    latex4.DrawLatex(0.65, 0.97, 'Macro: {0}'.format(commandlist[0].replace('\\', '')))
    
    latex5 = ROOT.TLatex()
    latex5.SetTextAlign(12)
    latex5.SetTextSize(0.02)
    latex5.SetNDC()
    latex5.DrawLatex(0.80, 0.92, 'Arguments:')
    
    latargs    = []
    argcounter = 0
    for arg in commandlist[1:]:
        arg = arg.replace('\\', '')
        if 'region' in arg:
                rargs  = arg.split(' ')
                rtitle = rargs[0]
                rregs  = rargs[1:-1]                
                latargs.append(ROOT.TLatex())
                latargs[argcounter].SetTextAlign(12)
                latargs[argcounter].SetTextSize(0.02)
                latargs[argcounter].SetNDC()
                latargs[argcounter].DrawLatex(0.80, 0.92 - 0.03*(1+argcounter),
                '--{0}'.format(rtitle))
                argcounter = argcounter + 1
                
                for regs in rregs:
                    latargs.append(ROOT.TLatex())
                    latargs[argcounter].SetTextAlign(12)
                    latargs[argcounter].SetTextSize(0.02)
                    latargs[argcounter].SetNDC()
                    latargs[argcounter].DrawLatex(0.83, 0.92 - 0.03*(1+argcounter),
                    '{0}'.format(regs.replace('\\','')))
                    argcounter = argcounter + 1
        else:
        
            latargs.append(ROOT.TLatex())
            latargs[argcounter].SetTextAlign(12)
            latargs[argcounter].SetTextSize(0.02)
            latargs[argcounter].SetNDC()
            latargs[argcounter].DrawLatex(0.80, 0.92 - 0.03*(1+argcounter),
            '--{0}'.format(arg))
            argcounter = argcounter + 1

    can2.Modified()       
    can2.Print("ResourceLogs/ResourcesPlot_{0}.root".format(pname))
    can2.Print("ResourceLogs/ResourcesPlot_{0}.eps".format(pname))
    
    return
