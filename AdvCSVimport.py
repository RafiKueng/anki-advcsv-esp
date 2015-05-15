#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Allows advanced CSV file import.
#
# This is based on multiimport addon
#
# Rafael Küng <rafael.kueng@uzh.ch>
# Version : 0.1-2015-04-03

###############################################################################
# SETTINGS

deck_name = "SpanishGerman" # which deck to add the cards to

N_HEADER_LINES=2 # how many lines to skip at beginning


###############################################################################

SYMBOLS = {
    "verb": "V",
    "nom":  "N",
    "adj":  "ADJ",
    "wend": "...",
    "adv":  "ADV",
    "prep": "PRP",
    "rule": "R",
    "pron": "PN"
    }


print('='*80)

# import standart modules
import csv
import re
import codecs

# import the main window object (mw) from ankiqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo, getFile, showText, askUser
# import all of the Qt GUI library
from aqt.qt import *


# import the tool for TSV import
from anki.importing import TextImporter


def LogFn(*_):
    for s in _:
        print s,
    print ""

if debug:
    Log = LogFn
else:
    Log = lambda *x: None


# Check that deck actually exists
def verify_deck(deck):
    if not deck in mw.col.decks.allNames():
	return False
    return True

 
# Check that model actually exists
def verify_model(model):
    if not model in mw.col.models.allNames():
        return False
    return True


def fix_lparts(lparts, modellen):
    while len(lparts) >= modellen+1 and lparts[-1] == "":
        lparts.pop(-1)
    if len(lparts) == modellen+1 and lparts[-1] == "":
        lparts.pop(-1)
    return lparts


def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]


def advimport():
    Log('-'*80)

    filename = getFile(mw, "Select file to import", None, key="import")
    
    if len(filename) == 0:
        showText("invalid filename", mw, type="text", run=True)
        return 
    
    lines = []
    n = 0
    
    with open(filename) as f:
        reader = unicode_csv_reader(f)
        
        for i in range(N_HEADER_LINES):
            n += 1
            reader.next()
            
        for row in reader:
            #print row
            n += 1
            lines.append((n, row))


    for n, line in lines:
        
        #Log("--"*5)

        data = []
        
        _chapt = line[0]
        _sect = line[1]
        _keywords = line[2]
        _question = line[3]
        _solution = line[4]
        
        _type = line[5]
        _subtype = line[6]
        _symb = SYMBOLS.get(_type, "")
        
        _rests = line[7:]
        
        print "L%03i:"%n,
        
        if not _type:
            print "!!! No type, skipping"
            continue


        elif _type == u"rule":
            print "   Rule",
            
            model = "Rule"
            key = _question
            
            data = [key, _question, _solution, _chapt, _sect, _type, _symb]


        elif _type == u"pron":
            print "   Pronoun",
            
            model = "Simple"
            key = _solution
            
            data = [key, _question, _solution, _chapt, _sect, _type, _symb]


        elif _type == u"wend":
            print "   Sentence",
            
            model = "Simple"
            key = _solution
            
            data = [key, _question, _solution, _chapt, _sect, _type, _symb]
            

        elif _type == u"prep":
            print "   Preposition",
            
            model = "Simple"
            key = _solution
            
            data = [key, _question, _solution, _chapt, _sect, _type, _symb]


        elif _type == u"adv":
            print "   Adverb",
            
            model = "Simple"
            key = _solution
            
            data = [key, _question, _solution, _chapt, _sect, _type, _symb]


        elif _type == u"nom": # Noun
            print "   Noun",
            
            model = "Noun"
            
            key = _solution
            
            lst = _solution.split(' ')
            
            art = lst.pop(0)
            noun = " ".join(lst)
            
            
            if not _subtype or _subtype == u"":
                if   art == "el":    _subtype = u"♂"
                elif art == "la":    _subtype = u"♀"
                elif art == "los":   _subtype = u"♂♂/♂♀"
                elif art == "las":   _subtype = u"♀♀"
                elif art == "el/la": _subtype = u"♂/♀"
            elif _subtype[0] in ["F", "f"]: _subtype = u"♀"
            elif _subtype[0] in ["M", "m"]: _subtype = u"♂"
            
            data = [key, _question, _solution, _chapt, _sect, _type, _subtype, _symb]

            
        elif _type == u"verb":
            print "   Verb", 
            
            modus = _rests[0]
            temp = _rests[1]
            forms = _rests[2:]
            
            for ii, f in enumerate(forms):
                _ = f.split('|')
                if len(_)==2:
                    for i, (c, e) in enumerate(zip(["stem", "ext"], _)):
                        _[i] = '<span class="%s">%s</span>' % (c, e)
                
                for i, x in enumerate(_):
                    _[i] = _[i].replace("[", '<span class="irr">')
                    _[i] = _[i].replace("]", '</span>')
                    
                forms[ii] = "".join(_)
            
            model = "Verb"
            key = "%s (%s; %s)" % (_solution, modus, temp)
            jsforms = '''{'sg1':'%s','sg2':'%s','sg3':'%s','pl1':'%s','pl2':'%s','pl3':'%s'}''' % tuple(forms)
            #Log("JSF", jsforms)

            _question = _question.replace("[", '<span class="prp">')
            _question = _question.replace("]", '</span>')
            _solution = _solution.replace("[", '<span class="prp">')
            _solution = _solution.replace("]", '</span>')
            
            print _question

            data = [key, _question, _solution, _chapt, _sect, _type, _subtype, _symb, modus, temp, jsforms]
          
          
        elif _type == u"adj":
            print "   Adjective",
            
            s = _solution
            
            def decline(stem, exts=['_o', '_a', '_os', '_as'], wrap=('<b>', '</b>')):
                return [stem+wrap[0]+_+wrap[1] for _ in exts]
            
            if '[' in s:
                _subtype = 'IRR'
                i = s.find('[')
                stem = s[:i]
                exts = s[i+1:s.find(']')].split('|')
                #Log("ir1: ", i, stem, exts, len(exts))
                
                if len(exts)==4:
                    pass
                elif len(exts)==2:
                    exts = [exts[0], exts[0], exts[1], exts[1]]
                elif len(exts)==3:
                    exts = [exts[0], exts[1], exts[2], exts[2]]
                else:
                    #TODO
                    exts = ['???']*4
                    
            elif '|' in s:
                _subtype = 'IRR'
                stem = ''
                exts = s.split('|')

                if len(exts)==4:
                    pass
                elif len(exts)==2:
                    exts = [exts[0], exts[0], exts[1], exts[1]]
                elif len(exts)==3:
                    exts = [exts[0], exts[1], exts[2], exts[2]]
                else:
                    exts = ['???']*4
                
            elif s[-1]=='o':
                _subtype = '-o'
                stem = s[:-1]
                exts = ['_o', '_a', '_os', '_as']

            elif s[-1]=='e':
                _subtype = '-e'
                stem = s[:-1]
                exts = ['e', 'e', '_es', '_es']
                
            elif s[-4:]=='ista':
                _subtype = '-ista'
                stem = s[:-4]
                exts = ['ist_a', 'ist_a', 'ist_as', 'ist_as']
            
            elif s[-2:] == u'ón':
                _subtype = '-ón'
                stem = s[:-2]
                exts = [u'*ón_', '*on_a', '*on_es', '*on_as']

            elif s[-5:] == 'erior':
                _subtype = '-erior'
                stem = s[:-5]
                exts = [u'erior', 'erior', 'erior_s', 'erior_s']

            elif s[-2:] == u'or':
                _subtype = '-or'
                stem = s[:-2]
                exts = [u'or', 'or_a', 'or_es', 'or_as']
                
            elif s[-1] == 'z':
                _subtype = '-z'
                stem = s[:-1]
                exts = [u'*z', '*z', '*c_es', '*c_es']
                
            else: # consonant at end:
                _subtype = '-CONS'
                stem = s
                exts = ['', '', '_es', '_es']
                print '!!!! >> check this:', stem, exts
                
                
            #decl = decline(stem, exts, wrap=('<span class="ext">', '</span>'))
            decl = decline(stem, exts, wrap=('', ''))
            #decl = [_.replace('_', '') for _ in decl]
            
            for i, d in enumerate(decl):
                while d.find('*')>=0:
                    fi = d.find('*')
                    #print fi, d
                    d = d[:fi] + '<span class="irr">' + d[fi+1] + '</span>' + d[fi+2:]
                if '_' in d:
                    d = d.replace('_', '<span class="ext">') + '</span>'
                decl[i] = d
            #print decl
            
            #Log(stem, exts, decl)
                
            model = "Adjectiv"
            key = stem + exts[0] # use masculine form sg as key
            key = key.replace('*', '').replace('_','')
            jsforms = '''{'MSg':'%s','FSg':'%s','MPl':'%s','FPl':'%s'}''' % tuple(decl)
            
            data = [key, _question, key, _chapt, _sect, _type, _subtype, _symb, jsforms]
        
        
        else:
            print "!!! Unknown type, skipping"
            continue
        
        
        
        if len(data) > 0:
            print data[1], data[2]
            with codecs.open('multiimport.tsv', 'w', encoding='utf-8') as f:
                s = "\t".join(data)
                f.write(s)
                #print s
            
            did = mw.col.decks.byName(deck_name)['id']
            mw.col.decks.select(did)

            m = mw.col.models.byName(model)
            mw.col.conf['curModel'] = m['id']
            cdeck = mw.col.decks.current()
            cdeck['mid'] = m['id']
            mw.col.decks.save(cdeck)
            mw.col.models.setCurrent(m)
            m['did'] = did
            mw.col.models.save(m)
            mw.reset()
            
            ti = TextImporter(mw.col,'multiimport.tsv')
            ti.delimiter = '\t'
            ti.allowHTML = True
            ti.initMapping()
            ti.run()
            #os.remove('multiimport.tsv')

      
    print('-'*80)

# Add function to multiimport
action = QAction("AdvCSVimport", mw)
mw.connect(action, SIGNAL("triggered()"), advimport)
mw.form.menuTools.addAction(action)

print('='*80)



