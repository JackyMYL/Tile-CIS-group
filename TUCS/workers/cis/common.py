'''Common tools for CIS workers.

Public variables:

    DEF_CALIB[gain]
        Dictionary of default CIS calibrations, keyed by ``highgain`` and
        ``lowgain``.

    CELLDICT[cell]
        Dictionary to translate cells -> channel numbers.

    PULSE_SHAPE[gain]
        List of tuples representing (x, y) coordinates of the CIS pulse shape.
        Data from  TileCalorimeter/TileConditions/share/pulse*_100.dat.

    LEAK_SHAPE[gain]
        List of tuples representing (x, y) coordinates of the leak effect.
        Data from TileCalorimeter/TileConditions/share/leak*_100.dat.
'''
import re
import itertools
from src.oscalls import *


# common CIS methods

def get_index(ros, mod, chan, gain):
    "flatten channel coordinates into a 1D index"
    return (ros * 64 * 48 * 2
            + mod * 48 * 2
            + chan * 2
            + gain)


def is_instrumented(ros,drawer, pmt):
    "This takes ros [0-3], drawer [0-63], !!pmt [1-48]!!, gain numbers" 
    chan2PMT_Special=[-1,-2,-3,-4,5,6,7,8,9,10, 
          11,12,13,14,15,16,17,18, 19, 20, 
          21,22,23,24,-27,-26,-25,-31,-32,-28, 
          33,29,30,-36,-35,34,44,38,37,43,42, 
          41,-45,-39,-40,-48,-47,-46]

    chan2PMT_LB=[1,2,3,4,5,6,7,8,9,10,
                 11,12,13,14,15,16,17,18,19,20,
                 21,22,23,24,27,26,25,30,29,28,
                 -33,-32,31,36,35,34,39,38,37,42,41,
                 40,45,-44,43,48,47,46]
    
    chan2PMT_EB=[1,2,3,4,5,6,7,8,9,10,
                 11,12,13,14,15,16,17,18,-19,-20,
                 21,22,23,24,-25,-26,-27,-28,-31,-32,
                 33,29,30,-35,-36,34,44,38,37,43,42,
                 41,-39,-40,-45,-46,-47,-48]

    if ros == 2 and drawer == 14:
        if pmt in chan2PMT_Special:
            return True
        else:
            return False
    elif ros == 3 and drawer == 17:
        if pmt in chan2PMT_Special:
            return True
        else:
            return False            
    elif ros <= 1 and pmt in chan2PMT_LB: 
        return True
    elif ros > 1 and pmt in chan2PMT_EB: 
        return True
    else:
        return False

def GetNumber(hash):
    "This produces part [1-4], module[1-64], chan [0-47] and gain strings"
    
    split = hash.split('_')[1:]
    number = []
    if len(split) >= 1:
        if   split[0] == 'LBA': number.append(1)
        elif split[0] == 'LBC': number.append(2)
        elif split[0] == 'EBA': number.append(3)
        elif split[0] == 'EBC': number.append(4)
        else:
            number.append(-1)
    if len(split) >= 2:
        number.append(int(split[1][1:]))
    if len(split) >= 3:
        number.append(int(split[2][1:]))
    if len(split) >= 4:
        if   split[3] == 'lowgain':  number.append(0)
        elif split[3] == 'highgain': number.append(1)
        else:
            number.append(-1)

    return number

def get_PMT_index(ros,drawer,chan):
    "This takes ros [0-3], drawer [0-63], chan [0-47], gain numbers"     
    chan2PMT_Special=[-1,-2,-3,-4,5,6,7,8,9,10, 
          11,12,13,14,15,16,17,18, 19, 20, 
          21,22,23,24,-27,-26,-25,-31,-32,-28, 
          33,29,30,-36,-35,34,44,38,37,43,42, 
          41,-45,-39,-40,-48,-47,-46]

    chan2PMT_LB=[1,2,3,4,5,6,7,8,9,10,
                 11,12,13,14,15,16,17,18,19,20,
                 21,22,23,24,27,26,25,30,29,28,
                 -33,-32,31,36,35,34,39,38,37,42,41,
                 40,45,-44,43,48,47,46]
    
    chan2PMT_EB=[1,2,3,4,5,6,7,8,9,10,
                 11,12,13,14,15,16,17,18,-19,-20,
                 21,22,23,24,-25,-26,-27,-28,-31,-32,
                 33,29,30,-35,-36,34,44,38,37,43,42,
                 41,-39,-40,-45,-46,-47,-48]

    if ros == 2 and drawer == 14:
        return chan2PMT_Special[chan]

    if ros == 3 and drawer == 17:
        return chan2PMT_Special[chan]

    if ros <= 1: 
        chan = chan2PMT_LB[chan]
    else:
        chan = chan2PMT_EB[chan]

    return chan


# The default calibrations for high and low gain
DEF_CALIB = {'lowgain': 1.27874994278,
             'highgain': 81.8399963379}



## Cell2Chan tools

# XXX: this works fine, but someone should look into using the ``cell2chan``
# dict found in src/region.py
CELLDICT = dict([('_cD0', ('_c00', 'LB')), ('_cA1-L', ('_c01', 'LB')),
                 ('_cBC1-R', ('_c02', 'LB')), ('_cBC1-L', ('_c03', 'LB')),
                 ('_cA1-R', ('_c04', 'LB')), ('_cA2-L', ('_c05', 'LB')),
                 ('_cBC2-R', ('_c06', 'LB')), ('_cBC2-L', ('_c07', 'LB')),
                 ('_cA2-R', ('_c08', 'LB')), ('_cA3-L', ('_c09', 'LB')),
                 ('_cA3-R', ('_c10', 'LB')), ('_cBC3-L', ('_c11', 'LB')),
                 ('_cBC3-R', ('_c12', 'LB')), ('_cD1-L', ('_c13', 'LB')),
                 ('_cD1-R', ('_c14', 'LB')), ('_cA4-L', ('_c15', 'LB')),
                 ('_cBC4-R', ('_c16', 'LB')), ('_cBC4-L', ('_c17', 'LB')),
                 ('_cA4-R', ('_c18', 'LB')), ('_cA5-L', ('_c19', 'LB')),
                 ('_cA5-R', ('_c20', 'LB')), ('_cBC5-L', ('_c21', 'LB')),
                 ('_cBC5-R', ('_c22', 'LB')), ('_cA6-L', ('_c23', 'LB')),
                 ('_cD2-R', ('_c24', 'LB')), ('_cD2-L', ('_c25', 'LB')),
                 ('_cA6-R', ('_c26', 'LB')), ('_cBC6-L', ('_c27', 'LB')),
                 ('_cBC6-R', ('_c28', 'LB')), ('_cA7-L', ('_c29', 'LB')),
                 ('_cA7-R', ('_c32', 'LB')), ('_cBC7-L', ('_c33', 'LB')),
                 ('_cBC7-R', ('_c34', 'LB')), ('_cA8-L', ('_c35', 'LB')),
                 ('_cA9-R', ('_c36', 'LB')), ('_cA9-L', ('_c37', 'LB')),
                 ('_cA8-R', ('_c38', 'LB')), ('_cBC8-L', ('_c39', 'LB')),
                 ('_cBC8-R', ('_c40', 'LB')), ('_cD3-L', ('_c41', 'LB')),
                 ('_cB9-R', ('_c42', 'LB')), ('_cD3-R', ('_c44', 'LB')),
                 ('_cA10-L', ('_c45', 'LB')), ('_cA10-R', ('_c46', 'LB')),
                 ('_cB9-L', ('_c47', 'LB')), ('_cE3', ('_c00', 'EB')),
                 ('_cE4', ('_c01', 'EB')), ('_cD4-R', ('_c02', 'EB')),
                 ('_cD4-L', ('_c03', 'EB')), ('_cC10-R', ('_c04', 'EB')),
                 ('_cC10-L', ('_c05', 'EB')), ('_cA12-R', ('_c06', 'EB')),
                 ('_cA12-L', ('_c07', 'EB')), ('_cB11-R', ('_c08', 'EB')),
                 ('_cB11-L', ('_c09', 'EB')), ('_cA13-R', ('_c10', 'EB')),
                 ('_cA13-L', ('_c11', 'EB')), ('_cE1', ('_c12', 'EB')),
                 ('_cE2', ('_c13', 'EB')), ('_cB12-R', ('_c14', 'EB')),
                 ('_cB12-L', ('_c15', 'EB')), ('_cD5-R', ('_c16', 'EB')),
                 ('_cD5-L', ('_c17', 'EB')), ('_cA14-R', ('_c20', 'EB')),
                 ('_cA14-L', ('_c21', 'EB')), ('_cB13-R', ('_c22', 'EB')),
                 ('_cB13-L', ('_c23', 'EB')), ('_cB14-R', ('_c30', 'EB')),
                 ('_cA15-R', ('_c31', 'EB')), ('_cA15-L', ('_c32', 'EB')),
                 ('_cB14-L', ('_c35', 'EB')), ('_cB15-L', ('_c36', 'EB')),
                 ('_cD6-L', ('_c37', 'EB')), ('_cD6-R', ('_c38', 'EB')),
                 ('_cB15-R', ('_c39', 'EB')), ('_cA16-L', ('_c40', 'EB')),
                 ('_cA16-R', ('_c41', 'EB'))])

WCELLDICT = dict([('_cA1', ('_cA1-L', '_cA1-R')), ('_cBC1', ('_cBC1-R', '_cBC1-L')),
                  ('_cA2', ('_cA2-L', '_cA2-R')), ('_cBC2', ('_cBC2-R', '_cBC2-L')),
                  ('_cA3', ('_cA3-L', '_cA3-R')), ('_cBC3', ('_cBC3-L', '_cBC3-R')),
                  ('_cD1', ('_cD1-L', '_cD1-R')), ('_cA4', ('_cA4-L', '_cA4-R')),
                  ('_cBC4', ('_cBC4-R', '_cBC4-L')), ('_cA5', ('_cA5-L', '_cA5-R')),
                  ('_cBC5', ('_cBC5-L', '_cBC5-R')), ('_cA6', ('_cA6-L', '_cA6-R')),
                  ('_cD2', ('_cD2-R', '_cD2-L')), ('_cBC6', ('_cBC6-L', '_cBC6-R')),
                  ('_cA7', ('_cA7-L', '_cA7-R')), ('_cBC7', ('_cBC7-L', '_cBC7-R')),
                  ('_cA8', ('_cA8-L', '_cA8-R')), ('_cA9', ('_cA9-L', '_cA9-R')),
                  ('_cBC8', ('_cBC8-L', '_cBC8-R')), ('_cD3', ('_cD3-L', '_cD3-R')),
                  ('_cB9', ('_cB9-R', '_cB9-L')), ('_cA10', ('_cA10-L', '_cA10-R')),
                  ('_cD4', ('_cD4-R', '_cD4-L')), ('C10', ('C10-R', 'C10-L')),
                  ('_cA12', ('_cA12-R', '_cA12-L')), ('_cB11', ('_cB11-R', '_cB11-L')),
                  ('_cA13', ('_cA13-R', '_cA13-L')), ('_cB12', ('_cB12-R', '_cB12-L')),
                  ('_cD5', ('_cD5-R', '_cD5-L')), ('_cA14', ('_cA14-R', '_cA14-L')),
                  ('_cB13', ('_cB13-R', '_cB13-L')), ('_cB14', ('_cB14-R', '_cB14-L')),
                  ('_cA15', ('_cA15-R', '_cA15-L')), ('_cB15', ('_cB15-L', '_cB15-R')),
                  ('_cD6', ('_cD6-R', '_cD6-L')), ('_cA16', ('_cA16-L', '_cA16-R'))])

def cell_to_chans(cell):

    if 'E' in cell or cell == '_cD0':
        sides = [cell]
    else:
        sides = (cell + '-L', cell + '-R')
        
    return [CELLDICT[side] for side in sides]



def match(selected, region):
    "Test if selected is in region"
    cellp = any('_c%s' % layer in selected for layer in ['A', 'B', 'D', 'E'])

    if not cellp:
        return (selected in region)

    m = re.match(r'(?P<partition>(E|L)B(A|C))?(?P<module>_m[0-9]{2})?(?P<cell>_c([A-E]+)?[0-9]+(-(?P<side>L|R))?)?',
                 selected)
    part = m.group('partition') if m.group('partition') else ''
    mod = m.group('module') if m.group('module') else ''
    cell = m.group('cell')
    sides = [m.group('side')] if m.group('side') else []

    if ''.join([part, mod]) not in region:
        return False

    chans = cell_to_chans(cell)

    if not part:
        # If part is not specified, we need to check that we're in the right
        # barrel first
        barrel = chans[0][1]

        if barrel not in region:
            return False

    return any(chan[0] in region for chan in chans)

## Pulse shape information

def _scrape_pulse_shapes(filename, target, gain):
    "An ouroborotic function to maintain the pulse shapes."
    points = []
    with open(filename, 'r') as shape_file:
        for line in shape_file:
            points.append(tuple(line.split()))

    with open(os.path.join(getResultDirectory(),'common.py'), 'a') as self:
        self.write('\n')
        self.write("{target}['{gain}'] = {points}".format(target=target,
                                                        gain=gain,
                                                        points=points))
        self.write('\n')

PULSE_SHAPE = {}
LEAK_SHAPE = {}

PULSE_SHAPE['highgain'] = [('-100', '-0.000479447'), ('-98', '0.00109641'),
                           ('-96', '-0.000822408'), ('-94', '-0.000453811'),
                           ('-92', '0.000344784'), ('-90', '-0.000319388'),
                           ('-88', '0.000156408'), ('-86', '-5.29837e-05'),
                           ('-84', '-0.00020737'), ('-82', '0.000335026'),
                           ('-80', '-8.54043e-05'), ('-78', '0.000197219'),
                           ('-76', '0.000640976'), ('-74', '0.000422932'),
                           ('-72', '-7.8888e-06'), ('-70', '-0.000118749'),
                           ('-68', '-0.000331324'), ('-66', '-0.000149454'),
                           ('-64', '0.000523382'), ('-62', '0.00063313'),
                           ('-60', '0.000883443'), ('-58', '0.00124788'),
                           ('-56', '0.000375471'), ('-54', '0.000809225'),
                           ('-52', '0.00230345'), ('-50', '0.00470068'),
                           ('-48', '0.00796847'), ('-46', '0.014374'),
                           ('-44', '0.0217788'), ('-42', '0.0353019'),
                           ('-40', '0.0554836'), ('-38', '0.080725'),
                           ('-36', '0.109734'), ('-34', '0.145935'),
                           ('-32', '0.188853'), ('-30', '0.238413'),
                           ('-28', '0.293723'), ('-26', '0.357135'),
                           ('-24', '0.42371'), ('-22', '0.490681'),
                           ('-20', '0.558463'), ('-18', '0.634003'),
                           ('-16', '0.699994'), ('-14', '0.767802'),
                           ('-12', '0.826421'), ('-10', '0.881983'),
                           ('-8', '0.919545'), ('-6', '0.954357'),
                           ('-4', '0.981399'), ('-2', '0.996243'),
                           ('0', '1'), ('2', '0.994969'), ('4', '0.980069'),
                           ('6', '0.959204'), ('8', '0.926133'),
                           ('10', '0.88498'), ('12', '0.837087'),
                           ('14', '0.791068'), ('16', '0.73673'),
                           ('18', '0.681117'), ('20', '0.625784'),
                           ('22', '0.570461'), ('24', '0.513062'),
                           ('26', '0.460032'), ('28', '0.410152'),
                           ('30', '0.363786'), ('32', '0.31588'),
                           ('34', '0.27561'), ('36', '0.237185'),
                           ('38', '0.203086'), ('40', '0.173331'),
                           ('42', '0.149382'), ('44', '0.126924'),
                           ('46', '0.10938'), ('48', '0.0933091'),
                           ('50', '0.0801473'), ('52', '0.0689132'),
                           ('54', '0.0604059'), ('56', '0.0532822'),
                           ('58', '0.0482683'), ('60', '0.0419099'),
                           ('62', '0.0376469'), ('64', '0.0334672'),
                           ('66', '0.0296903'), ('68', '0.0264527'),
                           ('70', '0.0227303'), ('72', '0.0200654'),
                           ('74', '0.01642'), ('76', '0.0125352'),
                           ('78', '0.00962615'), ('80', '0.00758667'),
                           ('82', '0.00463174'), ('84', '0.00171459'),
                           ('86', '-0.001383'), ('88', '-0.00415431'),
                           ('90', '-0.0066628'), ('92', '-0.00894359'),
                           ('94', '-0.0100773'), ('96', '-0.0106223'),
                           ('98', '-0.0116537')]

PULSE_SHAPE['lowgain'] = [('-100', '9.30582e-05'), ('-98', '-2.67343e-05'),
                          ('-96', '3.81307e-05'), ('-94', '-1.94605e-05'),
                          ('-92', '2.47631e-05'), ('-90', '-3.93613e-06'),
                          ('-88', '8.17493e-06'), ('-86', '-5.12483e-05'),
                          ('-84', '9.27413e-07'), ('-82', '-0.000359197'),
                          ('-80', '0.000193595'), ('-78', '5.82078e-06'),
                          ('-76', '4.18844e-05'), ('-74', '-2.56895e-05'),
                          ('-72', '0.000174569'), ('-70', '0.000215323'),
                          ('-68', '0.000219875'), ('-66', '1.32398e-05'),
                          ('-64', '-0.00030473'), ('-62', '0.00110573'),
                          ('-60', '0.00119735'), ('-58', '0.00182412'),
                          ('-56', '0.00194675'), ('-54', '0.00128723'),
                          ('-52', '0.00207512'), ('-50', '0.00579654'),
                          ('-48', '0.0106985'), ('-46', '0.0176858'),
                          ('-44', '0.0279536'), ('-42', '0.0426821'),
                          ('-40', '0.0607245'), ('-38', '0.0837454'),
                          ('-36', '0.110564'), ('-34', '0.143022'),
                          ('-32', '0.178296'), ('-30', '0.222959'),
                          ('-28', '0.284425'), ('-26', '0.352843'),
                          ('-24', '0.422571'), ('-22', '0.491057'),
                          ('-20', '0.559419'), ('-18', '0.630455'),
                          ('-16', '0.699524'), ('-14', '0.767641'),
                          ('-12', '0.826875'), ('-10', '0.879435'),
                          ('-8', '0.921957'), ('-6', '0.956372'),
                          ('-4', '0.980698'), ('-2', '0.995457'), ('0', '1'),
                          ('2', '0.994158'), ('4', '0.978892'),
                          ('6', '0.955017'), ('8', '0.922557'),
                          ('10', '0.883525'), ('12', '0.835942'),
                          ('14', '0.784166'), ('16', '0.730406'),
                          ('18', '0.675356'), ('20', '0.619144'),
                          ('22', '0.562278'), ('24', '0.507073'),
                          ('26', '0.451995'), ('28', '0.398998'),
                          ('30', '0.350304'), ('32', '0.305397'),
                          ('34', '0.265089'), ('36', '0.226066'),
                          ('38', '0.192186'), ('40', '0.162463'),
                          ('42', '0.137604'), ('44', '0.115819'),
                          ('46', '0.0974061'), ('48', '0.0810669'),
                          ('50', '0.067404'), ('52', '0.0562351'),
                          ('54', '0.0481968'), ('56', '0.0430497'),
                          ('58', '0.0403204'), ('60', '0.0378793'),
                          ('62', '0.033926'), ('64', '0.0290379'),
                          ('66', '0.0247562'), ('68', '0.0224962'),
                          ('70', '0.0210224'), ('72', '0.0184997'),
                          ('74', '0.0159961'), ('76', '0.0131848'),
                          ('78', '0.0103261'), ('80', '0.00748499'),
                          ('82', '0.00512891'), ('84', '0.00293263'),
                          ('86', '0.000482154'), ('88', '-0.00131265'),
                          ('90', '-0.00358801'), ('92', '-0.00561038'),
                          ('94', '-0.00722595'), ('96', '-0.00846367'),
                          ('98', '-0.0100816')]

LEAK_SHAPE['highgain'] = [('-100', '0'), ('-98', '-0.376648'),
                          ('-96', '-0.688451'), ('-94', '-0.940699'),
                          ('-92', '-1.14929'), ('-90', '-1.04169'),
                          ('-88', '-0.850866'), ('-86', '-0.466561'),
                          ('-84', '0.0103264'), ('-82', '0.274588'),
                          ('-80', '0.354237'), ('-78', '0.359666'),
                          ('-76', '0.168171'), ('-74', '-0.379086'),
                          ('-72', '-1.28507'), ('-70', '-2.21314'),
                          ('-68', '-2.93947'), ('-66', '-3.51042'),
                          ('-64', '-3.65376'), ('-62', '-3.12152'),
                          ('-60', '-1.91369'), ('-58', '-0.201782'),
                          ('-56', '0.72345'), ('-54', '4.10965'),
                          ('-52', '7.19089'), ('-50', '10.1133'),
                          ('-48', '14.1439'), ('-46', '19.6443'),
                          ('-44', '24.4391'), ('-42', '30.8437'),
                          ('-40', '37.1756'), ('-38', '43.2952'),
                          ('-36', '48.903'), ('-34', '54.6276'),
                          ('-32', '59.6593'), ('-30', '62.6287'),
                          ('-28', '64.6099'), ('-26', '65.1639'),
                          ('-24', '63.85'), ('-22', '60.7736'),
                          ('-20', '55.9524'), ('-18', '49.9001'),
                          ('-16', '42.473'), ('-14', '34.6157'),
                          ('-12', '25.7907'), ('-10', '15.5207'),
                          ('-8', '7.60957'), ('-6', '-1.00847'),
                          ('-4', '-10.5854'), ('-2', '-18.468'),
                          ('0', '-25.2176'), ('2', '-31.4248'),
                          ('4', '-37.3466'), ('6', '-41.4275'),
                          ('8', '-45.0907'), ('10', '-47.8468'),
                          ('12', '-49.1634'), ('14', '-50.3411'),
                          ('16', '-50.4471'), ('18', '-49.7303'),
                          ('20', '-48.2605'), ('22', '-46.4016'),
                          ('24', '-44.0636'), ('26', '-41.1154'),
                          ('28', '-37.8552'), ('30', '-34.1941'),
                          ('32', '-29.794'), ('34', '-25.9777'),
                          ('36', '-21.946'), ('38', '-17.5713'),
                          ('40', '-13.3559'), ('42', '-9.56317'),
                          ('44', '-5.94549'), ('46', '-3.23166'),
                          ('48', '-0.603581'), ('50', '1.46167'),
                          ('52', '3.10685'), ('54', '4.23471'),
                          ('56', '4.81912'), ('58', '4.505'),
                          ('60', '4.53509'), ('62', '3.76215'),
                          ('64', '3.03495'), ('66', '1.97612'),
                          ('68', '0.895712'), ('70', '0.0842953'),
                          ('72', '-1.38982'), ('74', '-2.00807'),
                          ('76', '-2.79225'), ('78', '-3.32582'),
                          ('80', '-4.09024'), ('82', '-4.95396'),
                          ('84', '-5.3022'), ('86', '-5.52474'),
                          ('88', '-5.70469'), ('90', '-6.24728'),
                          ('92', '-5.95028'), ('94', '-6.11264'),
                          ('96', '-6.04703'), ('98', '-5.97297')]

LEAK_SHAPE['lowgain'] = [('-100', '0'), ('-98', '-0.00849023'),
                         ('-96', '-0.0191028'), ('-94', '-0.0229482'),
                         ('-92', '-0.0243814'), ('-90', '-0.0235664'),
                         ('-88', '-0.0282492'), ('-86', '-0.033148'),
                         ('-84', '-0.0386869'), ('-82', '-0.0517972'),
                         ('-80', '-0.0694307'), ('-78', '-0.095847'),
                         ('-76', '-0.117715'), ('-74', '-0.143994'),
                         ('-72', '-0.170708'), ('-70', '-0.196446'),
                         ('-68', '-0.219561'), ('-66', '-0.228646'),
                         ('-64', '-0.227864'), ('-62', '-0.216566'),
                         ('-60', '-0.180882'), ('-58', '-0.116376'),
                         ('-56', '-0.0290481'), ('-54', '0.0743035'),
                         ('-52', '0.192569'), ('-50', '0.329455'),
                         ('-48', '0.481947'), ('-46', '0.639145'),
                         ('-44', '0.791158'), ('-42', '0.932041'),
                         ('-40', '1.05509'), ('-38', '1.14888'),
                         ('-36', '1.20672'), ('-34', '1.22675'),
                         ('-32', '1.20945'), ('-30', '1.15701'),
                         ('-28', '1.07465'), ('-26', '0.969747'),
                         ('-24', '0.850038'), ('-22', '0.717408'),
                         ('-20', '0.57258'), ('-18', '0.421184'),
                         ('-16', '0.269853'), ('-14', '0.121393'),
                         ('-12', '-0.0252383'), ('-10', '-0.169787'),
                         ('-8', '-0.309509'), ('-6', '-0.442792'),
                         ('-4', '-0.567219'), ('-2', '-0.67904'),
                         ('0', '-0.776743'), ('2', '-0.862032'),
                         ('4', '-0.932593'), ('6', '-0.98486'),
                         ('8', '-1.01875'), ('10', '-1.03754'),
                         ('12', '-1.04149'), ('14', '-1.03061'),
                         ('16', '-1.00424'), ('18', '-0.962283'),
                         ('20', '-0.907758'), ('22', '-0.843808'),
                         ('24', '-0.771853'), ('26', '-0.692215'),
                         ('28', '-0.607921'), ('30', '-0.521493'),
                         ('32', '-0.435123'), ('34', '-0.351889'),
                         ('36', '-0.274915'), ('38', '-0.205248'),
                         ('40', '-0.145793'), ('42', '-0.0963788'),
                         ('44', '-0.056306'), ('46', '-0.0264748'),
                         ('48', '-0.00635158'), ('50', '0.00524323'),
                         ('52', '0.00820421'), ('54', '0.00300748'),
                         ('56', '-0.00985297'), ('58', '-0.0294138'),
                         ('60', '-0.0547977'), ('62', '-0.0836748'),
                         ('64', '-0.112941'), ('66', '-0.140529'),
                         ('68', '-0.164786'), ('70', '-0.186127'),
                         ('72', '-0.204654'), ('74', '-0.220948'),
                         ('76', '-0.234807'), ('78', '-0.246042'),
                         ('80', '-0.255609'), ('82', '-0.264261'),
                         ('84', '-0.270052'), ('86', '-0.2722'),
                         ('88', '-0.27074'), ('90', '-0.266582'),
                         ('92', '-0.259853'), ('94', '-0.249533'),
                         ('96', '-0.23541'), ('98', '-0.218335')]