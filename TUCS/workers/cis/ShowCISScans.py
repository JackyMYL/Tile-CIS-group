# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# March 04, 2009
#

from src.GenericWorker import *
from src.oscalls import *
import src.MakeCanvas
import pickle
from ctypes import *

class ShowCISScans(GenericWorker):
    "Create postscript files with the CIS scans and diagnostic information"

    c1 = None

    def __init__(self, runType = 'CIS', all=False):
        self.runType = runType
        self.all = all
        self.nFail = 0

        if self.c1==None:
            self.c1 = src.MakeCanvas.MakeCanvas()
            print(self.c1)
            #self.c1.SetTitle("Put here a nice title")

        self.dir = os.path.join(getPlotDirectory(), "cis", "Investigate", 'CisScansLinearity')
        createDir(self.dir)

        createDir('%s/pmt_numbering/scans_fail_db_only' % self.dir)
        createDir('%s/pmt_numbering/scans_fail_qflag_only' % self.dir)
        createDir('%s/pmt_numbering/scans_fail_both' % self.dir)
        createDir('%s/pmt_numbering/scans_pass' % self.dir)

        createDir("%s/rms" % self.dir)
        
        createDir('%s/scans_fail_db_only' % self.dir)
        createDir('%s/scans_fail_qflag_only' % self.dir)
        createDir('%s/scans_fail_both' % self.dir)
        createDir('%s/scans_pass' % self.dir)

        if os.path.exists('%s/pmt_numbering/stats' % self.dir):
            os.unlink('%s/pmt_numbering/stats' % self.dir)
            
        if os.path.exists('%s/stats' % self.dir):
            os.unlink('%s/stats' % self.dir)
                        

    def ProcessStart(self):
        self.f_pmt = open('%s/pmt_numbering/stats' % self.dir, 'a')
        self.f_chan = open('%s/stats' % self.dir, 'a')
        

    def ProcessStop(self):
        print('Number of Uncalibrated: ', self.nFail)
        self.f_pmt.close()
        self.f_chan.close()
    
    def ProcessRegion(self, region):
        # Only look at each gain within some channel
        if 'gain' not in region.GetHash() or\
               region.GetEvents() == set():
            return

        foundCalibrated = False
        calibrated = False

        sevent = None # selected event; most recent run's good event

        for event in region.GetEvents():
            criteria = 'moreInfo'
            if event.run.runType == self.runType and criteria in event.data:
                if not event.data[criteria]:
                    calibrated = True
                foundCalibrated = True

                if sevent == None or sevent.run.runNumber < event.run.runNumber:
                    sevent = event

        if not foundCalibrated or (calibrated and not self.all):
            return

        self.nFail += 1
        
        self.c1.cd()

        dirstr = ''
        
        assert('CIS_problems' in sevent.data)
        
        problems = sevent.data['CIS_problems']

        assert('DB Deviation' in problems)
        assert('goodRegion' in event.data)
        
        if sevent.data['goodRegion']:
            dirstr = 'scans_pass'
        elif problems['DB Deviation'] and sevent.data['flag_progress'] >= 6:
            dirstr = 'scans_fail_db_only'
            self.f_chan.write('%s db variation more than 1 percent over last month\n' % region.GetHash())
            self.f_pmt.write('%s db variation more than 1 percent over last month\n' % region.GetHash(1))
        elif not problems['DB Deviation'] and sevent.data['flag_progress'] < 6:
            dirstr = 'scans_fail_qflag_only'
            self.f_chan.write('%s bad qflags over last month\n' % region.GetHash())
            self.f_pmt.write('%s bad qflags over last month\n' % region.GetHash(1))
        else:
            dirstr = 'scans_fail_both'
            self.f_chan.write('%s db variation more than 1 percent and bad qflags over last month\n' % region.GetHash())
            self.f_pmt.write('%s db variation more than 1 percent and bad qflags over last month\n' % region.GetHash(1))

        for event in region.GetEvents():
            runnum = event.run.runNumber

        self.c1.Print("%s/%s/uncalib_%s_%s_%i.png" % (self.dir, dirstr, self.runType,region.GetHash(), runnum))

        for event in region.GetEvents():
            if 'scan' in event.data:

                self.c1.Divide(1, 1)
                self.c1.Modified()
                
                scan = event.data['scan']
                scan.GetYaxis().SetRangeUser(0.0, 1000.0)
                scan.SetTitle("")
                scan.Draw("ALP")
                
                # xp,yp=ROOT.Double32_t(), ROOT.Double32_t()

                npoints=scan.GetN()
                for i in range(npoints):
                    xp = scan.GetPointX(i)
                    yp = scan.GetPointY(i)

                tl = ROOT.TLatex()
                tl.SetTextAlign(12)
                tl.SetTextSize(0.03)
                tl.SetNDC()

                cstr = region.GetHash()[8:]
                pstr = region.GetHash(1)[16:19]
                csplit = cstr.split('_')
                newstr = csplit[0] + csplit[1][1:] + ' ' + csplit[2] + '/' + pstr + ' ' + csplit[3]
                
                xoffset = 0.20

                tl.DrawLatex(xoffset,0.98, newstr)

                dy = 0.04
                location = 0.9

                tl.DrawLatex(xoffset,location,"Run %d" % event.run.runNumber)
                location -= dy

                tl.DrawLatex(xoffset,location,"Slope This Run: %f" % event.data['calibration'])
                location -= dy

                tl.DrawLatex(xoffset,location,"DB Slope: %f" % event.data['f_cis_db'])
                location -= dy

                if verbose:
                    tl.DrawLatex(xoffset,location,"DB Variation: %f %s" % (100*(event.data['calibration'] - event.data['f_cis_db'])/event.data['f_cis_db'], '%'))
                    location -= dy

                    tl.DrawLatex(xoffset,location,"CHI 2: %f %s" % (event.data['chi2'], ' '))
                    location-= dy

                    for problem, value in event.data['CIS_problems'].items():
                        # str(value)
                        if value:
                            flag = 'Fail'
                        else:
                            flag = 'Pass'
                        tl.DrawLatex(xoffset, location,"%s: %s" % (problem, flag))
                        location -= dy

                self.c1.Print("%s/%s/uncalib_%s_%s_%i.ps" % (self.dir, dirstr, self.runType,region.GetHash(), runnum))
                self.c1.Print("%s/%s/uncalib_%s_%s_%i.png" % (self.dir, dirstr, self.runType,region.GetHash(), runnum))

                if 'injections' in event.data:
                    self.c1.Clear()
                    if 'lowgain' in region.GetHash():
                        self.c1.Divide(4,5)
                    else:
                        self.c1.Divide(3,4)
                    self.c1.Modified()
                    i_canvas = 1
                    tl.SetTextSize(0.08)
                    number = region.GetNumber(1)
                    
                    inj_hists = event.data['injections']
                    for x, y in inj_hists.items():
                        if 'lowgain' in region.GetHash():
                            pass#self.c1.cd(i_canvas+4)
                        else:
                            pass#self.c1.cd(i_canvas+3)
                        i_canvas += 1

                        y.GetXaxis().SetTitle('ADC counts')
                        #y.SetLineWidth(6)
                        y.Draw()
                        tl.DrawLatex(xoffset,0.95, "%0.2f pC, RMS %0.2f" % (x, y.GetRMS()))
                        self.c1.Print("%s/rms/rms_%0.2f_%0.2f.png" % (self.dir, x, y.GetRMS()))
                        #tl.DrawLatex(xoffset,0.85, "RMS %f" % y.GetRMS())
                        

                    self.c1.cd()
                    tl.SetTextSize(0.03)
                    tl.DrawLatex(0.10, 0.97, "Fixed-charge Distribution run %d %s" % (event.run.runNumber, region.GetHash()[8:]))

                    self.c1.Print("%s/%s/uncalib_%s_%s_%i.png" % (self.dir, dirstr, self.runType,region.GetHash(), runnum))
                    self.c1.Divide(1, 1,)
                    self.c1.Modified()

                if 'samples' in event.data:
                    #a = ROOT.gStyle.GetPadBorderSize()
                    #b = ROOT.gStyle.GetFrameBorderSize()
                    ROOT.gStyle.SetPadBorderSize(0)
                    ROOT.gStyle.SetFrameBorderSize(0)
                    ROOT.gStyle.SetOptStat(0)

                    hists = event.data['samples']

                    x_dac = 16
                    y_phase = 16
                    self.c1.Divide(x_dac, y_phase)
                    for i in range(event.data['maxphase']):
                        for j in range(event.data['maxdac']):
                            if len(hists[i][j]) != 4:
                                print(len(hists[i][j]) , 'ouch', i, j)

                            self.c1.cd((i+1)*x_dac + (j+1) + 1)
                            for x in range(4):
                                print(hists[i][j][x])
                            hists[i][j][0].GetXaxis()
                            hists[i][j][0].SetMinimum(0)
                            hists[i][j][0].SetMaximum(1023)
                            hists[i][j][0].Draw('')
                            hists[i][j][1].SetLineColor(ROOT.kRed)
                            hists[i][j][1].Draw('SAME')
                            hists[i][j][2].SetLineColor(ROOT.kBlue)
                            hists[i][j][2].Draw('SAME')
                            hists[i][j][3].SetLineColor(ROOT.kGreen)
                            hists[i][j][3].Draw('SAME')
                            
                            
                    self.c1.Modified()
                    self.c1.cd(0)
                    
                    tl1 = ROOT.TLatex(0.10, 0.03, "Injected Charge")
                    tl2 = ROOT.TLatex(0.03, 0.10, "Phase")
                    tl3 = ROOT.TLatex(0.10, 0.97, "Fit-Range Samples run %d %s" % (event.run.runNumber, region.GetHash()[8:]))
                    
                    tl2.SetTextAngle(90)
                    for tl in [tl1, tl2, tl3]:
                        tl.SetTextAlign(12)
                        tl.SetTextSize(0.06)
                        tl.SetNDC()
                        tl.Draw()
                        
                    self.c1.Print("%s/%s/uncalib_%s_%s_%i.png" % (self.dir, dirstr, self.runType,region.GetHash(), runnum))
                    
                    self.c1.Clear()
                    self.c1.Divide(1, 1)
                    self.c1.Modified()
                    #ROOT.gStyle.SetPadBorderSize(a)
                    #ROOT.gStyle.SetFrameBorderSize(b)

        

        self.c1.Print("%s/%s/uncalib_%s_%s_%i.png" % (self.dir, dirstr, self.runType,region.GetHash(), runnum))
        if os.path.exists("%s/pmt_numbering/%s/uncalib_%s_%s_%i.png" % (self.dir, dirstr, self.runType,region.GetHash(1), runnum)):
            os.unlink("%s/pmt_numbering/%s/uncalib_%s_%s_%i.png" % (self.dir, dirstr, self.runType,region.GetHash(1), runnum))
            
        os.symlink("../../%s/uncalib_%s_%s_%i.png" % (dirstr, self.runType,region.GetHash(), runnum),\
                   "%s/pmt_numbering/%s/uncalib_%s_%s_%i.png" % (self.dir, dirstr, self.runType,region.GetHash(1), runnum))


        if 'goodRegion' in sevent.data and 'calibratableRegion' in sevent.data:
            if sevent.data['goodRegion'] and sevent.data['calibratableRegion']:
                gcstr = "Pg_Pc"
            elif sevent.data['goodRegion'] and not sevent.data['calibratableRegion']:
                gcstr = "Pg_Fc"
            elif not sevent.data['goodRegion'] and sevent.data['calibratableRegion']:
                gcstr = "Fg_Pc"
            elif not sevent.data['goodRegion'] and not sevent.data['calibratableRegion']:
                gcstr = "Fg_Fc"
                                
            createDir('%s/%s' % (self.dir, gcstr))

            if os.path.exists("%s/%s/uncalib_%s_%s_%i.png" % (self.dir, gcstr, self.runType,region.GetHash(0), runnum)):
                os.unlink("%s/%s/uncalib_%s_%s_%i.png" % (self.dir, gcstr, self.runType,region.GetHash(0), runnum))

            os.symlink("../%s/uncalib_%s_%s_%i.png" % (dirstr, self.runType,region.GetHash(), runnum),\
                       "%s/%s/uncalib_%s_%s_%i.png" % (self.dir, gcstr, self.runType,region.GetHash(0), runnum))
            
        if 'recalib_progress' in sevent.data:
            createDir('%s/recalib%d' % (self.dir, sevent.data['recalib_progress']))
            if os.path.exists("%s/recalib%d/uncalib_%s_%s_%i.png" % (self.dir, sevent.data['recalib_progress'], self.runType,region.GetHash(0), runnum)):
                os.unlink("%s/recalib%d/uncalib_%s_%s_%i.png" % (self.dir, sevent.data['recalib_progress'], self.runType,region.GetHash(0), runnum))
                            
            os.symlink("../%s/uncalib_%s_%s_%i.png" % (dirstr, self.runType,region.GetHash(), runnum),\
                       "%s/recalib%d/uncalib_%s_%s_%i.png" % (self.dir, sevent.data['recalib_progress'], self.runType,region.GetHash(0), runnum))
            
                      
        if 'flag_progress' in sevent.data:
            createDir('%s/flag%d' % (self.dir, sevent.data['flag_progress']))
            if os.path.exists("%s/flag%d/uncalib_%s_%s_%i.png" % (self.dir, sevent.data['flag_progress'], self.runType,region.GetHash(0), runnum)):
                os.unlink("%s/flag%d/uncalib_%s_%s_%i.png" % (self.dir, sevent.data['flag_progress'], self.runType,region.GetHash(0), runnum))
                
            os.symlink("../%s/uncalib_%s_%s_%i.png" % (dirstr, self.runType,region.GetHash(), runnum),\
                       "%s/flag%d/uncalib_%s_%s_%i.png" % (self.dir, sevent.data['flag_progress'], self.runType,region.GetHash(0), runnum))

        if 'comp_chi_rms' in sevent.data:
            [pass_chirms, pass_qflag] = event.data['comp_chi_rms']
            name = 'compare_%s_chirms_%s_qflag' % (str(pass_chirms), str(pass_qflag))
            
            createDir('%s/%s' % (self.dir, name))
            if os.path.exists("%s/%s/uncalib_%s_%s_%i.png" % (self.dir, name, self.runType,region.GetHash(0), runnum)):
                os.unlink("%s/%s/uncalib_%s_%s_%i.png" % (self.dir, name, self.runType,region.GetHash(0), runnum))
                
            os.symlink("../%s/uncalib_%s_%s_%i.png" % (dirstr, self.runType,region.GetHash(), runnum),\
                       "%s/%s/uncalib_%s_%s_%i.png" % (self.dir, name, self.runType,region.GetHash(0), runnum))
                                                            
                                                            
        
        
        
        
        
