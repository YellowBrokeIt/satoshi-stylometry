"""British/American spelling markers used by 03_spelling.py.

* PAIRS: unambiguous spelling pairs, each category = (british_regex, american_regex).  Words where the 'American' spelling is also an
  ordinary different word (program, meter, check, tire, license, story, draft...) are deliberately NOT counted.
* BRITISHISMS: British-leaning words/idioms whose American partner is a normal general word ('while', 'among', 'learned'); only the
  British form is counted, and the American partner is counted alongside for context.
"""
import re

def rx(words):
    return re.compile(r'\b(?:' + '|'.join(sorted(map(re.escape, words), key=len, reverse=True)) + r')\b', re.I)

# --- -our / -or
OUR = [('colour','color'),('favour','favor'),('honour','honor'),('behaviour','behavior'),('neighbour','neighbor'),('labour','labor'),
       ('harbour','harbor'),('humour','humor'),('flavour','flavor'),('rumour','rumor'),('vapour','vapor'),('endeavour','endeavor'),
       ('armour','armor'),('savour','savor'),('tumour','tumor'),('parlour','parlor')]
OUR_SUF = ['', 's', 'ed', 'ing', 'ite', 'ites', 'able', 'ful', 'less', 'ist', 'ists', 'ings']
# --- -ise / -ize (stems written with the z)
IZE = ['optimiz','realiz','recogniz','organiz','authoriz','summariz','apologiz','characteriz','centraliz','minimiz','maximiz','utiliz',
       'specializ','emphasiz','criticiz','finaliz','normaliz','prioritiz','synchroniz','customiz','memoriz','generaliz','categoriz',
       'capitaliz','visualiz','standardiz','civiliz','legaliz','digitiz','monetiz','decentraliz','materializ','neutraliz','stabiliz',
       'initializ','randomiz','parameteriz','serializ','legitimiz','familiariz','harmoniz','itemiz','mobiliz','subsidiz','sympathiz',
       'theoriz','revolutioniz','popularis','globaliz','localiz','virtualiz','industrializ','internationaliz','rationaliz','commercializ',
       'computeriz','hypothesiz','idealiz','socializ','tokeniz','fertiliz','moderniz','patroniz','penaliz','polariz','scrutiniz','trivializ']
IZE = [s.replace('popularis', 'populariz') for s in IZE]
IZE_SUF = ['e', 'es', 'ed', 'ing', 'ation', 'ations', 'er', 'ers']
# --- -yse / -yze
YZE = ['analy','paraly','cataly']
YZE_SUF = ['se', 'ses', 'sed', 'sing', 'ser', 'sers']
# --- -re / -er
RE_ER = [('centre','center'),('centres','centers'),('centred','centered'),('centring','centering'),('centrepiece','centerpiece'),
         ('theatre','theater'),('theatres','theaters'),('fibre','fiber'),('fibres','fibers'),('calibre','caliber'),('litre','liter'),('litres','liters'),
         ('kilometre','kilometer'),('kilometres','kilometers'),('millimetre','millimeter'),('centimetre','centimeter'),('lustre','luster'),
         ('sombre','somber'),('spectre','specter')]
# --- -ence/-ense, -ogue/-og
ENCE = [('defence','defense'),('defences','defenses'),('defenceless','defenseless'),('offence','offense'),('offences','offenses'),('pretence','pretense')]
OGUE = [('catalogue','catalog'),('catalogues','catalogs'),('catalogued','cataloged')]
# --- doubled l
LL = [('travelled','traveled'),('travelling','traveling'),('traveller','traveler'),('travellers','travelers'),('cancelled','canceled'),
      ('cancelling','canceling'),('modelling','modeling'),('modelled','modeled'),('labelled','labeled'),('labelling','labeling'),
      ('fuelled','fueled'),('fuelling','fueling'),('signalling','signaling'),('signalled','signaled'),('counsellor','counselor'),
      ('levelled','leveled'),('levelling','leveling'),('marvellous','marvelous'),('jewellery','jewelry'),('totalled','totaled'),
      ('totalling','totaling'),('channelled','channeled'),('channelling','channeling'),('tunnelled','tunneled'),('tunnelling','tunneling'),
      ('rivalled','rivaled'),('equalled','equaled'),('equalling','equaling'),('dialled','dialed'),('dialling','dialing'),
      ('quarrelled','quarreled'),('shovelled','shoveled'),('woollen','woolen')]
# --- other unambiguous spelling variants
MISC = [('judgement','judgment'),('acknowledgement','acknowledgment'),('aluminium','aluminum'),('sceptic','skeptic'),('sceptics','skeptics'),
        ('sceptical','skeptical'),('scepticism','skepticism'),('artefact','artifact'),('artefacts','artifacts'),('fulfil','fulfill'),
        ('fulfilment','fulfillment'),('enrol','enroll'),('enrolment','enrollment'),('instalment','installment'),('skilful','skillful'),
        ('moustache','mustache'),('pyjamas','pajamas'),('cosy','cozy'),('manoeuvre','maneuver'),('aeroplane','airplane'),('sulphur','sulfur'),
        ('speciality','specialty'),('oestrogen','estrogen'),('anaemia','anemia'),('foetus','fetus'),('haemorrhage','hemorrhage'),
        ('encyclopaedia','encyclopedia'),('mediaeval','medieval'),('diarrhoea','diarrhea')]

def build():
    cats = {}
    b, a = [], []
    for x, y in OUR:
        b += [x+s for s in OUR_SUF]; a += [y+s for s in OUR_SUF]
    cats['-our / -or'] = (rx(b), rx(a), b, a)
    b = [z[:-1]+'s'+s for z in IZE for s in IZE_SUF]; a = [z+s for z in IZE for s in IZE_SUF]
    cats['-ise / -ize'] = (rx(b), rx(a), b, a)
    pairs = [(z+s, z+'z'+s[1:]) for z in YZE for s in YZE_SUF]
    pairs = [(x, y) for x, y in pairs if x not in ('analyses', 'paralyses', 'catalyses')]   # 'analyses' is also the American noun plural
    b = [x for x, _ in pairs]; a = [y for _, y in pairs]
    cats['-yse / -yze'] = (rx(b), rx(a), b, a)
    for name, lst in [('-re / -er', RE_ER), ('-ence / -ense', ENCE), ('-ogue / -og', OGUE), ('-ll- / -l-', LL), ('misc spellings', MISC)]:
        b = [x for x, _ in lst]; a = [y for _, y in lst]
        cats[name] = (rx(b), rx(a), b, a)
    return cats

# British-leaning words; (word-regex, american partner regex for context)
BRITISHISMS = {
    'whilst':    (rx(['whilst']), rx(['while'])),
    'amongst':   (rx(['amongst']), rx(['among'])),
    'learnt':    (rx(['learnt']), rx(['learned'])),
    'spelt/dreamt/burnt/spoilt/smelt/leapt': (rx(['spelt','dreamt','burnt','spoilt','smelt','leapt']), rx(['spelled','dreamed','burned','spoiled','smelled','leaped'])),
    'towards':   (rx(['towards']), rx(['toward'])),
    'afterwards/backwards/forwards': (rx(['afterwards','backwards','forwards']), rx(['afterward','backward','forward'])),
    'bloody':    (rx(['bloody']), rx(['damn','damned'])),
    'mum/maths': (rx(['mum','maths']), rx(['mom','math'])),
    'cheers':    (rx(['cheers']), rx(['thanks'])),
    'lorry/petrol/queue': (rx(['lorry','petrol','queue','queues','queued','queueing']), rx(['truck','gasoline','line'])),
    'rubbish/bloke/chap/bugger/bollocks': (rx(['rubbish','bloke','chap','bugger','bollocks','arse','sod off']), rx(['garbage','guy','dude'])),
}
