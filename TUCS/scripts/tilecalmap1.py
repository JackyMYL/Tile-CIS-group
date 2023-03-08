try:
    import ROOT
except:
    print "Failed to load root"
from array import array

import math

def xateta(y,eta):
    return y/math.tan(2*math.atan(math.exp(-eta)))

def yateta(x,eta):
    return x*math.tan(2*math.atan(math.exp(-eta)))

zaxis=ROOT.TArrow(-100,0,8000,0,0.01,"|>")
yaxis=ROOT.TArrow(0,-100,0,5600,0.01,"|>")
latex =ROOT.TLatex()
rand = ROOT.TRandom(1000)

def draw_atlas_text(half=False):
    latex.SetTextColor(1)
    latex.SetTextFont(62)
    latex.SetTextSize(0.05)
    latex.SetTextAlign(22)
    if half:
        latex.DrawLatex(2200.,2000.,'ATLAS Preliminary');
        latex.DrawLatex(2200.,1700.,'Tile Calorimeter');
    else:
        latex.DrawLatex(-6500.,1000.,'ATLAS Preliminary');
        latex.DrawLatex(-6500.,700.,'Tile Calorimeter');

def draw_axis():
    latex.SetTextColor(1)
    latex.SetTextAlign(33)  
    latex.SetTextFont(43)
    latex.SetTextSize(20)

    zaxis.SetLineStyle(8)
    zaxis.Draw()
    latex.DrawLatex(8000,300,"z")

    yaxis.SetLineStyle(8)
    yaxis.Draw()
    latex.DrawLatex(200,5600,"r")

def draw_sides(x=3400, y=1700):
    latex.SetTextColor(1)
    latex.SetTextFont(43)
    latex.SetTextSize(40)
    latex.SetTextAlign(32)  
    latex.DrawLatex(x,y,'A side');
    latex.SetTextAlign(12)  
    latex.DrawLatex(-x,y,'C side');

def draw_cell_names(draw_cell_boundary=True, half=False):
    if half:
        cells = half_lb_cells + half_eb_cells + half_e_cells
    else:
        cells = lb_cells + eb_cells + e_cells
        
    for cell in cells:
        full_name = cell.GetName()
        if not full_name == "D0" and not half:
            short_name = full_name[:-1]
        else:
            short_name = full_name
        
        x=(cell.GetX()[0]+cell.GetX()[1])/2.
        y=(cell.GetY()[1]+cell.GetY()[2])/2.
    
        if short_name in ["C10", "E1", "E2", "E3", "E4"]:
            x = x - math.copysign(200.,x)
    
        latex.SetTextAlign(22)  
        latex.SetTextFont(43)
        latex.SetTextSize(15)
        latex.DrawLatex( x,y, short_name )
        if draw_cell_boundary:
            cell.Draw("same")      
#
##  Lines for the pseudo rapidity
# 

y1 = 2850 # Y at bottom of the eta lines [-1, 1.]
y2 = 5100 # Y at top of the eta lines [-1.2, 1.2]
x1 = 4400 # X at start of eta line [1.1, -1.6]
x2 = 8300 # X at end ot the eta line [1.3, 1.6]


lines=[ ROOT.TLine(-x1, yateta(-x1, -1.6), -x2, yateta(-x2, -1.6)),
        ROOT.TLine(-x1, yateta(-x1, -1.5), -x2, yateta(-x2, -1.5)),
        ROOT.TLine(-x1, yateta(-x1, -1.4), -x2, yateta(-x2, -1.4)),
        ROOT.TLine(-x1, yateta(-x1, -1.3), -x2, yateta(-x2, -1.3)),
        ROOT.TLine(-x1, yateta(-x1, -1.2), xateta(y2, -1.2), y2),
        ROOT.TLine(-x1, yateta(-x1, -1.1), xateta(y2, -1.1), y2),
        ROOT.TLine(xateta(y1, -1.0), y1, xateta(y2, -1.0), y2),
        ROOT.TLine(xateta(y1, -0.9), y1, xateta(y2, -0.9), y2),
        ROOT.TLine(xateta(y1, -0.8), y1, xateta(y2, -0.8), y2),
        ROOT.TLine(xateta(y1, -0.7), y1, xateta(y2, -0.7), y2),
        ROOT.TLine(xateta(y1, -0.6), y1, xateta(y2, -0.6), y2),
        ROOT.TLine(xateta(y1, -0.5), y1, xateta(y2, -0.5), y2),
        ROOT.TLine(xateta(y1, -0.4), y1, xateta(y2, -0.4), y2),
        ROOT.TLine(xateta(y1, -0.3), y1, xateta(y2, -0.3), y2),
        ROOT.TLine(xateta(y1, -0.2), y1, xateta(y2, -0.2), y2),
        ROOT.TLine(xateta(y1, -0.1), y1, xateta(y2, -0.1), y2),
        ROOT.TLine(xateta(y1, 0.1), y1, xateta(y2, 0.1), y2),
        ROOT.TLine(xateta(y1, 0.2), y1, xateta(y2, 0.2), y2),
        ROOT.TLine(xateta(y1, 0.3), y1, xateta(y2, 0.3), y2),
        ROOT.TLine(xateta(y1, 0.4), y1, xateta(y2, 0.4), y2),
        ROOT.TLine(xateta(y1, 0.5), y1, xateta(y2, 0.5), y2),
        ROOT.TLine(xateta(y1, 0.6), y1, xateta(y2, 0.6), y2),
        ROOT.TLine(xateta(y1, 0.7), y1, xateta(y2, 0.7), y2),
        ROOT.TLine(xateta(y1, 0.8), y1, xateta(y2, 0.8), y2),
        ROOT.TLine(xateta(y1, 0.9), y1, xateta(y2, 0.9), y2),
        ROOT.TLine(xateta(y1, 1.0), y1, xateta(y2, 1.0), y2),
        ROOT.TLine(x1, yateta(x1, 1.1), xateta(y2, 1.1), y2),
        ROOT.TLine(x1, yateta(x1, 1.2), xateta(y2, 1.2), y2),
        ROOT.TLine(x1, yateta(x1, 1.3), x2, yateta(x2, 1.3)),
        ROOT.TLine(x1, yateta(x1, 1.4), x2, yateta(x2, 1.4)),
        ROOT.TLine(x1, yateta(x1, 1.5), x2, yateta(x2, 1.5)),
        ROOT.TLine(x1, yateta(x1, 1.6), x2, yateta(x2, 1.6)) ]

def draw_eta_lines(half=False):
    xetalables = 8500
    yetalables = 5200

    if half:
        mylines = lines[16:]    
    else:
        mylines = lines
        
    for line in mylines:
        line.SetLineStyle(2)
        line.SetLineColor(2)
        line.Draw()

    # lables formating for eta values.
    latex.SetTextColor(2)
    latex.SetTextAlign(22)  
    latex.SetTextFont(43)
    latex.SetTextSize(15)


    latex.DrawLatex(0,yetalables,"#eta = 0.0")

    for eta in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2]:
        latex.DrawLatex(xateta(yetalables,eta),yetalables,"%4.1f"%eta)
        if not half:
            latex.DrawLatex(xateta(yetalables,-eta),yetalables,"%4.1f"%-eta)

    for eta in [1.3, 1.4, 1.5, 1.6]:
        latex.DrawLatex(xetalables,yateta(xetalables,eta),"%4.1f"%eta)
        if not half:
            latex.DrawLatex(-xetalables,yateta(-xetalables,-eta),"%4.1f"%eta)

lb_cells = []
eb_cells =[]
e_cells =[]

half_lb_cells = []
half_eb_cells =[]
half_e_cells =[]


lbAyCoord = array('f',[3383,3383,2983,2983,3383])
lbBCyCoord = array('f',[4528,4528,3908,3908,3383,3383,3908,3908,4528])
lbDyCoord = array('f',[5043,5043,4528,4528,5043])
ebAyCoord = array('f',[3373,3373,2953,2953,3373])
ebByCoord = array('f',[4098,4098,3373,3373,4098])
ebDyCoord = array('f',[5013,5013,4098,4098,5013])

# Long barrel D cells
D0 = ROOT.TGraph(5, array('f',[-500,500,500,-500,-500]), lbDyCoord)
D0.SetName("D0")
lb_cells.append(D0)
hD0 = ROOT.TGraph(4, array('f',[0,500,500,0]), lbDyCoord)
hD0.SetName("D0")
half_lb_cells.append(hD0)



D1A = ROOT.TGraph(5, array('f',[500,1475,1475,500,500]), lbDyCoord)
D1A.SetName("D1A")
lb_cells.append(D1A)

D2A = ROOT.TGraph(5, array('f',[1475,2500,2500,1475,1475]), lbDyCoord)
D2A.SetName("D2A")
lb_cells.append(D2A)

D3A = ROOT.TGraph(5, array('f',[2500,3705,3705,2500,2500]), lbDyCoord)
D3A.SetName("D3A")
lb_cells.append(D3A)

D1C = ROOT.TGraph(5, array('f',[-500,-1475,-1475,-500,-500]), lbDyCoord)
D1C.SetName("D1C")
lb_cells.append(D1C)

D2C = ROOT.TGraph(5, array('f',[-1475,-2500,-2500,-1475,-1475]), lbDyCoord)
D2C.SetName("D2C")
lb_cells.append(D2C)

D3C = ROOT.TGraph(5, array('f',[-2500,-3705,-3705,-2500,-2500]), lbDyCoord)
D3C.SetName("D3C")
lb_cells.append(D3C)

# Long barrel A cells A side 

A1A = ROOT.TGraph(5, array('f',[0,345,345,0,0]), lbAyCoord)
A1A.SetName("A1A")
lb_cells.append(A1A)

A2A = ROOT.TGraph(5, array('f',[345,660,660,345,345]), lbAyCoord)
A2A.SetName("A2A")
lb_cells.append(A2A)

A3A = ROOT.TGraph(5,array('f',[660,1000,1000,660,660]), lbAyCoord)
A3A.SetName("A3A")
lb_cells.append(A3A)

A4A = ROOT.TGraph(5,array('f',[1000,1345,1345,1000,1000]), lbAyCoord)
A4A.SetName("A4A")
lb_cells.append(A4A)

A5A = ROOT.TGraph(5, array('f',[1345,1710,1710,1345,1345]), lbAyCoord)
A5A.SetName("A5A")
lb_cells.append(A5A)

A6A = ROOT.TGraph(5,array('f',[1710,2080,2080,1710,1710]), lbAyCoord)
A6A.SetName("A6A")
lb_cells.append(A6A)

A7A = ROOT.TGraph(5,array('f',[2080,2450,2450,2080,2080]), lbAyCoord)
A7A.SetName("A7A")
lb_cells.append(A7A)

A8A = ROOT.TGraph(5,array('f',[2450,2885,2885,2450,2450]), lbAyCoord)
A8A.SetName("A8A")
lb_cells.append(A8A)

A9A = ROOT.TGraph(5, array('f',[2885,3330,3330,2885,2885]), lbAyCoord)
A9A.SetName("A9A")
lb_cells.append(A9A)

A10A = ROOT.TGraph(5, array('f',[3330,3705,3705,3330,3330]), lbAyCoord)
A10A.SetName("A10A")
lb_cells.append(A10A)

# Long barrel A cells C side

A1C = ROOT.TGraph(5, array('f',[0,-345,-345,0,0]), lbAyCoord)
A1C.SetName("A1C")
lb_cells.append(A1C)

A2C = ROOT.TGraph(5, array('f',[-345,-660,-660,-345,-345]), lbAyCoord)
A2C.SetName("A2C")
lb_cells.append(A2C)

A3C = ROOT.TGraph(5, array('f',[-660,-1000,-1000,-660,-660]), lbAyCoord)
A3C.SetName("A3C")
lb_cells.append(A3C)

A4C = ROOT.TGraph(5, array('f',[-1000,-1345,-1345,-1000,-1000]),lbAyCoord)
A4C.SetName("A4C")
lb_cells.append(A4C)

A5C = ROOT.TGraph(5, array('f',[-1345,-1710,-1710,-1345,-1345]), lbAyCoord)
A5C.SetName("A5C")
lb_cells.append(A5C)

A6C = ROOT.TGraph(5, array('f',[-1710,-2080,-2080,-1710,-1710]), lbAyCoord)
A6C.SetName("A6C")
lb_cells.append(A6C)

A7C = ROOT.TGraph(5, array('f',[-2080,-2450,-2450,-2080,-2080]), lbAyCoord)
A7C.SetName("A7C")
lb_cells.append(A7C)

A8C = ROOT.TGraph(5, array('f',[-2450,-2885,-2885,-2450,-2450]), lbAyCoord)
A8C.SetName("A8C")
lb_cells.append(A8C)

A9C = ROOT.TGraph(5, array('f',[-2885,-3330,-3330,-2885,-2885]), lbAyCoord)
A9C.SetName("A9C")
lb_cells.append(A9C)

A10C = ROOT.TGraph(5, array('f',[-3330,-3705,-3705,-3330,-3330]), lbAyCoord)
A10C.SetName("A10C")
lb_cells.append(A10C)

# Long barrel BC and B cells A side

BC1A =  ROOT.TGraph(9, array('f',[0,435,435,390,390,0,0,0,0]), lbBCyCoord)
BC1A.SetName("BC1A")
lb_cells.append(BC1A)


BC2A =  ROOT.TGraph(9, array('f',[435,870,870,770,770,390,390,435,435]), lbBCyCoord)
BC2A.SetName("BC2A")
lb_cells.append(BC2A)

BC3A =  ROOT.TGraph(9, array('f',[870,1305,1305,1135,1135,770,770,870,870]), lbBCyCoord)
BC3A.SetName("BC3A")
lb_cells.append(BC3A)

BC4A =  ROOT.TGraph(9, array('f',[1305,1755,1755,1530,1530,1135,1135,1305,1305]), lbBCyCoord)
BC4A.SetName("BC4A")
lb_cells.append(BC4A)

BC5A =  ROOT.TGraph(9, array('f',[1755,2215,2215,1925,1925,1530,1530,1755,1755]), lbBCyCoord)
BC5A.SetName("BC5A")
lb_cells.append(BC5A)

BC6A =  ROOT.TGraph(9, array('f',[2215,2705,2705,2360,2360,1925,1925,2215,2215]), lbBCyCoord)
BC6A.SetName("BC6A")
lb_cells.append(BC6A)

BC7A =  ROOT.TGraph(9, array('f',[2705,3230,3230,2810,2810,2360,2360,2705,2705]), lbBCyCoord)
BC7A.SetName("BC7A")
lb_cells.append(BC7A)

BC8A =  ROOT.TGraph(9, array('f',[3230,3705,3705,3295,3295,2810,2810,3230,3230]), lbBCyCoord)
BC8A.SetName("BC8A")
lb_cells.append(BC8A)

B9A =  ROOT.TGraph(5, array('f',[3295,3705,3705,3295,3295]), array('f',[3383,3383,3908,3908,3383]))
B9A.SetName("B9A")
lb_cells.append(B9A)

# Long barrel BC and B cells C side

BC1C =  ROOT.TGraph(9, array('f',[0,-435,-435,-390,-390,0,0,0,0]), lbBCyCoord)
BC1C.SetName("BC1C")
lb_cells.append(BC1C)

BC2C =  ROOT.TGraph(9, array('f',[-435,-870,-870,-770,-770,-390,-390,-435,-435]), lbBCyCoord)
BC2C.SetName("BC2C")
lb_cells.append(BC2C)

BC3C =  ROOT.TGraph(9, array('f',[-870,-1305,-1305,-1135,-1135,-770,-770,-870,-870]), lbBCyCoord)
BC3C.SetName("BC3C")
lb_cells.append(BC3C)

BC4C =  ROOT.TGraph(9, array('f',[-1305,-1755,-1755,-1530,-1530,-1135,-1135,-1305,-1305]), lbBCyCoord)
BC4C.SetName("BC4C")
lb_cells.append(BC4C)

BC5C =  ROOT.TGraph(9, array('f',[-1755,-2215,-2215,-1925,-1925,-1530,-1530,-1755,-1755]), lbBCyCoord)
BC5C.SetName("BC5C")
lb_cells.append(BC5C)

BC6C =  ROOT.TGraph(9, array('f',[-2215,-2705,-2705,-2360,-2360,-1925,-1925,-2215,-2215]), lbBCyCoord)
BC6C.SetName("BC6C")
lb_cells.append(BC6C)

BC7C =  ROOT.TGraph(9, array('f',[-2705,-3230,-3230,-2810,-2810,-2360,-2360,-2705,-2705]), lbBCyCoord)
BC7C.SetName("BC7C")
lb_cells.append(BC7C)

BC8C =  ROOT.TGraph(9, array('f',[-3230,-3705,-3705,-3295,-3295,-2810,-2810,-3230,-3230]), lbBCyCoord)
BC8C.SetName("BC8C")
lb_cells.append(BC8C)

B9C =  ROOT.TGraph(5, array('f',[-3295,-3705,-3705,-3295,-3295]), array('f',[3383,3383,3908,3908,3383]))
B9C.SetName("B9C")
lb_cells.append(B9C)

# Extended Barrel A cells A side 

A12A = ROOT.TGraph(5, array('f',[4680,4900,4900,4680,4680]), ebAyCoord)
A12A.SetName("A12A")
eb_cells.append(A12A)

A13A = ROOT.TGraph(5, array('f',[4900,5500,5500,4900,4900]), ebAyCoord)
A13A.SetName("A13A")
eb_cells.append(A13A)

A14A = ROOT.TGraph(5, array('f',[5500,6170,6170,5500,5500]), ebAyCoord)
A14A.SetName("A14A")
eb_cells.append(A14A)

A15A = ROOT.TGraph(5, array('f',[6170,6900,6900,6170,6170]), ebAyCoord)
A15A.SetName("A15A")
eb_cells.append(A15A)

A16A = ROOT.TGraph(5, array('f',[6900,8060,8060,6900,6900]), ebAyCoord)
A16A.SetName("A16A")
eb_cells.append(A16A)

# Extended Barrel B cells A side 

B11A = ROOT.TGraph(5, array('f',[4680,5010,5010,4680,4680]), ebByCoord)
B11A.SetName("B11A")
eb_cells.append(B11A)

B12A = ROOT.TGraph(5, array('f',[5010,5692,5692,5010,5010]), ebByCoord)
B12A.SetName("B12A")
eb_cells.append(B12A)

B13A = ROOT.TGraph(5, array('f',[5692,6440,6440,5692,5692]), ebByCoord)
B13A.SetName("B13A")
eb_cells.append(B13A)

B14A = ROOT.TGraph(5, array('f',[6440,7215,7215,6440,6440]), ebByCoord)
B14A.SetName("B14A")
eb_cells.append(B14A)

B15A = ROOT.TGraph(5, array('f',[7215,8060,8060,7215,7215]), ebByCoord)
B15A.SetName("B15A")
eb_cells.append(B15A)

# Extended Barrel C cell A side 

C10A = ROOT.TGraph(5, array('f',[4545,4650,4650,4545,4545]), array('f',[4513,4513,3903,3903,4513]))
C10A.SetName("C10A")
eb_cells.append(C10A)

# Extended Barrel D cells A side 

D4A = ROOT.TGraph(5, array('f',[4245,4655,4655,4245,4245]), array('f',[5013,5013,4518,4518,5013]))
D4A.SetName("D4A")
eb_cells.append(D4A)

D5A = ROOT.TGraph(5, array('f',[4680,6250,6250,4680,4680]), ebDyCoord)
D5A.SetName("D5A")
eb_cells.append(D5A)

D6A = ROOT.TGraph(5, array('f',[6250,8060,8060,6250,6250]), ebDyCoord)
D6A.SetName("D6A")
eb_cells.append(D6A)

# Extended Barrel A cells C side 

A12C = ROOT.TGraph(5, array('f',[-4680,-4900,-4900,-4680,-4680]), ebAyCoord)
A12C.SetName("A12C")
eb_cells.append(A12C)

A13C = ROOT.TGraph(5, array('f',[-4900,-5500,-5500,-4900,-4900]), ebAyCoord)
A13C.SetName("A13C")
eb_cells.append(A13C)

A14C = ROOT.TGraph(5, array('f',[-5500,-6170,-6170,-5500,-5500]), ebAyCoord)
A14C.SetName("A14C")
eb_cells.append(A14C)

A15C = ROOT.TGraph(5, array('f',[-6170,-6900,-6900,-6170,-6170]), ebAyCoord)
A15C.SetName("A15C")
eb_cells.append(A15C)

A16C = ROOT.TGraph(5, array('f',[-6900,-8060,-8060,-6900,-6900]), ebAyCoord)
A16C.SetName("A16C")
eb_cells.append(A16C)

# Extended Barrel B cells C side 

B11C = ROOT.TGraph(5, array('f',[-4680,-5010,-5010,-4680,-4680]), ebByCoord)
B11C.SetName("B11C")
eb_cells.append(B11C)

B12C = ROOT.TGraph(5, array('f',[-5010,-5692,-5692,-5010,-5010]), ebByCoord)
B12C.SetName("B12C")
eb_cells.append(B12C)

B13C = ROOT.TGraph(5, array('f',[-5692,-6440,-6440,-5692,-5692]), ebByCoord)
B13C.SetName("B13C")
eb_cells.append(B13C)

B14C = ROOT.TGraph(5, array('f',[-6440,-7215,-7215,-6440,-6440]), ebByCoord)
B14C.SetName("B14C")
eb_cells.append(B14C)

B15C = ROOT.TGraph(5, array('f',[-7215,-8060,-8060,-7215,-7215]), ebByCoord)
B15C.SetName("B15C")
eb_cells.append(B15C)

# Extended Barrel C cell C side 

C10C = ROOT.TGraph(5, array('f',[-4545,-4650,-4650,-4545,-4545]), array('f',[4513,4513,3903,3903,4513]))
C10C.SetName("C10C")
eb_cells.append(C10C)

# Extended Barrel D cells C side 

D4C = ROOT.TGraph(5, array('f',[-4245,-4655,-4655,-4245,-4245]), array('f',[5013,5013,4518,4518,5013]))
D4C.SetName("D4C")
eb_cells.append(D4C)

D5C = ROOT.TGraph(5, array('f',[-4680,-6250,-6250,-4680,-4680]), ebDyCoord)
D5C.SetName("D5C")
eb_cells.append(D5C)

D6C = ROOT.TGraph(5, array('f',[-6250,-8060,-8060,-6250,-6250]), ebDyCoord)
D6C.SetName("D6C")
eb_cells.append(D6C)
 
# E cells A-side

E1A = ROOT.TGraph(5, array('f',[4585,4630,4630,4585,4585]), array('f',[3893,3893,3458,3458,3893]))
E1A.SetName("E1A")
e_cells.append(E1A)

E2A = ROOT.TGraph(5, array('f',[4585,4630,4630,4585,4585]), array('f',[3433,3433,3003,3003,3433]))
E2A.SetName("E2A")
e_cells.append(E2A)

E3A = ROOT.TGraph(5, array('f',[4585,4630,4630,4585,4585]), array('f',[2994,2994,2368,2368,2994]))
E3A.SetName("E3A")
e_cells.append(E3A)

E4A = ROOT.TGraph(5, array('f',[4585,4630,4630,4585,4585]), array('f',[2356,2356,1891,1891,2356]))
E4A.SetName("E4A")
e_cells.append(E4A)
                   
# E cells C-side

E1C = ROOT.TGraph(5, array('f',[-4585,-4630,-4630,-4585,-4585]), array('f',[3893,3893,3458,3458,3893]))
E1C.SetName("E1C")
e_cells.append(E1C)

E2C = ROOT.TGraph(5, array('f',[-4585,-4630,-4630,-4585,-4585]), array('f',[3433,3433,3003,3003,3433]))
E2C.SetName("E2C")
e_cells.append(E2C)

E3C = ROOT.TGraph(5, array('f',[-4585,-4630,-4630,-4585,-4585]), array('f',[2994,2994,2368,2368,2994]))
E3C.SetName("E3C")
e_cells.append(E3C)

E4C = ROOT.TGraph(5, array('f',[-4585,-4630,-4630,-4585,-4585]), array('f',[2356,2356,1891,1891,2356]))
E4C.SetName("E4C")
e_cells.append(E4C)

for i in lb_cells[1:]:
    if i.GetX()[0]+i.GetX()[1]>0.:
        hi = ROOT.TGraph(i)
        hi.SetName(i.GetName()[:-1])
        half_lb_cells.append(hi)
for i in eb_cells:
    if i.GetX()[0]+i.GetX()[1]>0.:
        hi = ROOT.TGraph(i)
        hi.SetName(i.GetName()[:-1])
        half_eb_cells.append(hi)
for i in e_cells:
    if i.GetX()[0]+i.GetX()[1]>0.:
        hi = ROOT.TGraph(i)
        hi.SetName(i.GetName()[:-1])
        half_e_cells.append(hi)
#
## # Create the Tile maps
# 

#h1 = ROOT.TH2Poly()
h1 = ROOT.TH2Poly("Half Tilecal","",-220,8700,0,5700)
for i in half_lb_cells+half_eb_cells+half_e_cells:
    h1.AddBin(i)

h2 = ROOT.TH2Poly()
for i in lb_cells+eb_cells+e_cells:
    h2.AddBin(i)

# Fill the Tile map
for i in half_lb_cells+half_eb_cells+half_e_cells:
    h1.Fill(i.GetName(),rand.Gaus(100.,5.))

for i in lb_cells+eb_cells+e_cells:
    h2.Fill(i.GetName(),rand.Gaus(100.,5.))


#
#### And now the graphics For Half Tilecal
#
width = 1100
height= 600
c1 = ROOT.TCanvas("HalfTilecal", "Tile Calorimeter", width, height)
x0 = -500.
y0 = -300. 
c1.cd(0).Range(x0,y0,x0+10.*width, y0+10.*height)
ROOT.gStyle.SetPalette(ROOT.kBlackBody) # kLightTemperature=87 #Rainbow=55 kBlackBody=

ROOT.gStyle.SetTitleAlign(33)
ROOT.gStyle.SetTitleX(.99)
h1.SetTitle("My title comes here")

ROOT.gStyle.SetPaintTextFormat("4.1f")
h1.SetBarOffset(0.1)

h1.SetStats(0)

#h2.Draw("TEXT,COLZA")
h1.Draw("COLZA")
c1.SetFrameLineColor(0)
ROOT.gPad.Update()

# Move the color scale to the right, has to be after the Draw() 
palette = h1.GetListOfFunctions().FindObject("palette")
palette.SetX1(9000.);
palette.SetY1(00.);
palette.SetX2(9250.);
palette.SetY2(5000.);


draw_eta_lines(half=True)
#
## Z and R axis 
#
draw_axis()

draw_atlas_text(half=True)

draw_cell_names(half=True)
c1.cd(0).Range(x0,y0,x0+10.*width, y0+10.*height)
c1.Modified()
c1.Update()
    
#
#### And now the graphics
#
width = 1900
height= 600   
c2 = ROOT.TCanvas("Tilecal", "Tile Calorimeter", width, height)
x0 = -9000.
y0 = -300. 

c2.cd(0).Range(x0, y0, x0+10.*width, y0+10.*height)
ROOT.gStyle.SetPalette(ROOT.kDarkBodyRadiator) # kLightTemperature=87 #Rainbow=55

ROOT.gStyle.SetTitleAlign(13)
ROOT.gStyle.SetTitleX(.01)
h2.SetTitle("My title comes here")

ROOT.gStyle.SetPaintTextFormat("4.1f")
h2.SetBarOffset(0.1)

h2.SetStats(0)

#h2.Draw("TEXT,COLZA")
h2.Draw("COLZA")
c2.SetFrameLineColor(0)
ROOT.gPad.Update()

# Move the color scale to the right, has to be after the Draw() 
palette = h2.GetListOfFunctions().FindObject("palette")
palette.SetX1(9000.);
palette.SetX2(9500.);

draw_eta_lines()

#
## Z and R axis 
#
draw_axis()

draw_atlas_text()

draw_sides()

draw_cell_names()
c2.cd(0).Range(x0, y0, x0+10.*width, y0+10.*height)
c2.Modified()
c2.Update()


a = raw_input('wait here (q to exit):')
if a.find("q")!=-1:
    exit()

#
## Root color maps
#
# kDeepSea=51,          kGreyScale=52,    kDarkBodyRadiator=53,
# kBlueYellow= 54,      kRainBow=55,      kInvertedDarkBodyRadiator=56,
# kBird=57,             kCubehelix=58,    kGreenRedViolet=59,
# kBlueRedYellow=60,    kOcean=61,        kColorPrintableOnGrey=62,
# kAlpine=63,           kAquamarine=64,   kArmy=65,
# kAtlantic=66,         kAurora=67,       kAvocado=68,
# kBeach=69,            kBlackBody=70,    kBlueGreenYellow=71,
# kBrownCyan=72,        kCMYK=73,         kCandy=74,
# kCherry=75,           kCoffee=76,       kDarkRainBow=77,
# kDarkTerrain=78,      kFall=79,         kFruitPunch=80,
# kFuchsia=81,          kGreyYellow=82,   kGreenBrownTerrain=83,
# kGreenPink=84,        kIsland=85,       kLake=86,
# kLightTemperature=87, kLightTerrain=88, kMint=89,
# kNeon=90,             kPastel=91,       kPearl=92,
# kPigeon=93,           kPlum=94,         kRedBlue=95,
# kRose=96,             kRust=97,         kSandyTerrain=98,
# kSienna=99,           kSolar=100,       kSouthWest=101,
# kStarryNight=102,     kSunset=103,      kTemperatureMap=104,
# kThermometer=105,     kValentine=106,   kVisibleSpectrum=107,
# kWaterMelon=108,      kCool=109,        kCopper=110,
# kGistEarth=111,       kViridis=112,     kCividis=113
