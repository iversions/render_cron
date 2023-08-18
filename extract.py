import json
import spacy
from spacy.tokens import DocBin
from tqdm import tqdm
import os
import glob
import pdfplumber
import pandas as pd
from tabulate import tabulate
import re
from string import ascii_lowercase
from itertools import groupby
from statistics import mean
# from checkdt import checkdate
import warnings
import datetime
import requests
warnings.filterwarnings('ignore')

#import statistics
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

lowcase = set(ascii_lowercase)

def find_regex(p):
    nvar = []
    for c in p:
        if c.isdigit():
            nvar.append("d")
        elif c.isalnum():
            nvar.append("w")
        elif c in lowcase:
            nvar.append("t")
        else:
            nvar.append(c)
    grp = groupby(nvar)
    return ''.join(f'\\{what}{{{how_many}}}'
                   if how_many>1 else f'\\{what}'
                   for what, how_many in ((g[0],len(list(g[1]))) for g in grp))


def checkdate(string):
    for format in ["%b %d, %Y", "%d-%b-%Y","%d-%m-%Y", "%m-%d-%Y", "%d-%b-%y","%d/%b/%Y", "%m/%d/%Y","%d-%m-%y","%d/%m/%y"]:
        try:
            return datetime.datetime.strptime(string, format).date()
        except ValueError:
             pass
    raise ValueError(string)


el = []

# filpath = '/home/shashi/Documents/WorkingFolder/venv/afcons/processed/Airtel_UAT_1.pdf'
# filpath = '/home/shashi/Documents/WorkingFolder/venv/afcons/processed/Airtel_UAT_2.pdf'
# filpath = '/home/shashi/Documents/WorkingFolder/venv/afcons/processed/Airtel_UAT_3.pdf'
# filpath = '/home/shashi/Documents/WorkingFolder/venv/afcons/processed/Airtel_UAT_3_P3.pdf'
# filpath = '/home/shashi/Documents/WorkingFolder/venv/afcons/processed/DSL_Bill_02214959697_wifi_HT2427I002116324_P3.pdf'
# filpath = '/home/shashi/Documents/WorkingFolder/venv/afcons/processed/MTNL.pdf'
# filpath = '/home/shashi/Documents/WorkingFolder/venv/afcons/processed/TaxInvoiceAD1222311AJ90443.pdf'
# filpath = '/home/shashi/Documents/WorkingFolder/venv/afcons/processed/TaxInvoiceMH1222311CE49554.pdf'
# filpath = '/home/shashi/Documents/WorkingFolder/venv/afcons/processed/Air Asia - 01.pdf'
# filpath = '/home/shashi/Documents/WorkingFolder/venv/afcons/processed/MH33-2223-033219.pdf'
# filpath = '/home/shashi/Documents/WorkingFolder/venv/afcons/processed/108510VIPINDUSTRIESLTD1032Jan_ Dmart.pdf'
# filpath = '/home/shashi/Documents/WorkingFolder/venv/afcons/processed/1064489SKYBAGSHYDERABDWHPO.pdf'
# filpath = '/home/shashi/Documents/WorkingFolder/venv/afcons/processed/2.pdf'
# filpath = '/home/shashi/Documents/WorkingFolder/venv/afcons/processed/Air India - 01.pdf'
# filpath = '/home/shashi/Documents/WorkingFolder/venv/afcons/processed/Air India - 02.pdf'
# filpath = '/home/shashi/Documents/WorkingFolder/venv/afcons/processed/O8RU4F_10723_1000770744.pdf'
# filpath = '/home/shashi/Documents/WorkingFolder/venv/afcons/NTT/Apr22_DC2MA_150820616_Ele Bill.pdf'
# filpath = '/home/shashi/Documents/WorkingFolder/venv/afcons/processed/INVOICE PROSARES SOLUTION MADAL 28235.pdf'
# filpath = '/home/shashi/Documents/WorkingFolder/venv/afcons/processed/IDNCE232406-879 - Prosa.pdf'

def invextract(path):
    with pdfplumber.open(path) as p0:
        firstpage = p0.pages[0]
        charst = firstpage.extract_words()
        f_ext_text = firstpage.extract_text()
        invc3 = firstpage.extract_table()

    training_params = []
    u = 0
    z = []
    for x in charst:
        w = charst[u]['text']
        u+=1
        z.append(w)
    K =':'
    while(K in z):
        z.remove(K)    
    # print('\n')
    z = [i.replace('\xad','-') for i in z ]

    date=[]
    nondate = []
    bvc = 0
    for i in z:
        try:
            checkdate(i)
            date.append(i)
        except ValueError:
            nondate.append(i)

    for i in z:
        u+=1
    az = 0
    for i in z:
        if z[az] == ':':
            z.remove(z[az])
        az+=1
    bn = 0
    for i in z:
        if ':' in z[bn]:
            dff = z[bn]
            z.remove(z[bn])
            if len(dff.split(':')[0])>0:
                z.insert(bn , dff.split(':')[0])
            else:
                asa=1
            if len(dff.split(':')[1])>0:
                z.insert(bn+1 , dff.split(':')[1])
            else:
                sas=1
        bn+=1

    u = 0

    z = [i for i in z if i not in date]

    gstregex = '\w{2}\w{5}\d{4}\w{4}'

    ghj = 0
    for i in z:
        if 'GSTNo:' in z[ghj]:
            z.append(z[ghj].split('GSTNo:')[1])
        ghj+=1
    # print('zz is',zz)

    glist = []
    for f in z:
        # print(f)
        if len(f) == 15:
            # print(f)
            glist.append(f)
    # print(glist)
    nglist = []
    for i in glist:
        gstcheck = re.findall(gstregex,i)
        # print(gstcheck[0])
        try:
            nglist.append(gstcheck[0])
        except IndexError:
            pass
    # print(nglist)

    companyName = []
    try:
        for i in nglist:
            url = f'http://sheet.gstincheck.co.in/check/2046e097577fd2efa1c721fc3d0f2948/{i}'
            frequest = requests.get(url=url)
            adata = frequest.json()
            cdata = adata['data']['lgnm']

            companyName.append(cdata+ ' and GST '+i)

    except Exception:
        companyName

    for i, w in enumerate(z):
        if ',' in w:
            z[i] = w.replace(',', '')

    r1 = '\d{2}\w{5}\d{4}\w\d\w{2}'  # GSTIN
    r2 = '\w\d{5}\w{2}\d{4}\w{3}\d{6}' # CIN
    r3 = '\d{2}\w{5}\d{4}\w\d\w\d' # GSTIN FALSE
    r5 = '\w{5}\d{4}\w' # PAN
        
    cv = 0
    for i in z:
        if (find_regex(z[cv])== '\d{2}\w{5}\d{4}\w\d\w{2}') or (find_regex(z[cv])== '\w\d{5}\w{2}\d{4}\w{3}\d{6}') or (find_regex(z[cv])== '\d{2}\w{5}\d{4}\w\d\w\d') or (find_regex(z[cv])== '\w{5}\d{4}\w'):
            z.remove(z[cv])
        cv+=1

    num = ['0','1' , '2' , '3' , '4' , '5' , '6' , '7' , '8' , '9']
    l3 = []
    hj = 0
    for i in z:
        jk = 0
        for j in num:
            if num[jk] in z[hj]:
                l3.append(z[hj])
            jk+=1
        hj+=1
    l3 = [*set(l3)]

    for i, w in enumerate(l3):
        if '.'  in w:
            l3[i] = w.replace('.', '')

    l4 = [i for i in l3 if len(i)> 6]

    inv = []
    g = 0
    for i in l4:
        x = l4[g].isnumeric()
        if x == False:
            inv.append(l4[g])
        g+=1
    ind = []
    d = 0
    for i in z:
        e = 0
        for i in inv:
            if z[d] == inv[e]:
                ind.append(d)
            e+=1
        d+=1
    try:
        dfg = ['invoice' , 'number' , 'inv' , 'no' , 'Invoice' , 'Number']
        inv_final =[]
        g = 0
        for i in ind:
            h = 0
            for j in dfg:
                if ind[g] <=10: 
                    if dfg[h] in z[0:ind[g]]:
                        inv_final.append(z[ind[g]])
                    else:
                        pass
                elif ind[g]>10:
                    if dfg[h] in z[ind[g]-10:ind[g]]:
                        inv_final.append(z[ind[g]])
                    else:
                        pass
                h+=1        
            g+=1

        qwer = 0
        for i in inv_final:
            if len(inv_final[qwer])>20:
                inv_final.remove(inv_final[qwer])
        # print('Inv Number is:', inv_final[0])
        invoiceNumber = inv_final[0]
        # print('Invoice Date is:', date[0])
        # invoiceDate = date[0]
    except IndexError:
        inv_final = ''
        invoiceNumber = inv_final


    try:
        finaldate = date[0]
        # print('Invoice Date is:', finaldate)
        invoiceDate = finaldate
    except IndexError:
        finaldate = ''
        invoiceDate = finaldate

    #----------------------------- TOTAL ---------------------------------------
    try:

        firstpage = p0.pages[0]
        charst = firstpage.extract_words()
        invc3 = firstpage.extract_table()

        training_params = []
        u = 0
        z1 = []
        for x in charst:
            w = charst[u]['text']
            u+=1
            z1.append(w)
        K =':'
        while(K in z1):
            z1.remove(K)    
        print('\n')
        cvb = 0
        for i in invc3:
            cvb+=1

        def num_there(s):
            return any(i.isdigit() for i in s)

        xyz = len(invc3)

        if xyz%2 == 0:
            len1 = (xyz/2)
        else:
            xyz+=1
            len1 = (xyz/2)

        z2 = sum(invc3[int(len1-1):], [])
        z2 = [i for i in z2 if i is not None]
        z2 = [i.replace(',','') for i in z2]
        z2 = [i.replace('\n','') for i in z2]
        newz = []
        cx=0
        for item in z2:
            if num_there(z2[cx]) == True:
                newz.append(z2[cx])
            cx+=1
        newz = [*set(newz)]

        for ele in newz:
            try:
                float(ele)
            except ValueError:
                newz.remove(ele)

        dataa = " ".join(str(i) for i in z1)    

        nlp_ner = spacy.load('/copy/model-best')

        docs = nlp_ner(dataa)
        ents1 = list(docs.ents)
        names_labels1 = list(map(lambda x: x.label_, ents1))

        def find_indices(list_to_check, item_to_find):
            indices = []
            for idx, value in enumerate(names_labels1):
                if value == item_to_find:
                    indices.append(idx)
            return indices

        y= find_indices(names_labels1, 'INVOICE NUMBER')

        names=[]
        for i in y:
            i= ents1[i]
            names.append(i)

        zxc = 0

        Dates =[]
        z= find_indices(names_labels1, 'INVOICE DATE')

        for i in z:
            i= ents1[i]
            Dates.append(i)

        zxc = 0

        el = []
        ii = 0
        invc3 = [[item.replace(u'\n', '') if isinstance(item, str) else item for item in items] for items in invc3]

        invc3 = [[item.replace(u'$', '') if isinstance(item, str) else item for item in items] for items in invc3]


        qw1 = len(invc3)

        for i in invc3:
            qw = 0
            for y in invc3[ii]:
                el.append(invc3[ii][qw])
                qw+=1
            ii+=1
        tuv = " ".join(str(i) for i in el)

        el2 = [i for i in el if i is not None]
        d1 = " ".join(str(i) for i in el2)

        cv = 0
        for t in el2:
            cv+=1

        res = []
        res2 = []
        for ele in newz:
            try:
                float(ele)
                res.append(ele)
            except ValueError:
                res2.append(ele)

        res2 = [item.replace(u',', '') if isinstance(item, str) else item for item in res2]
        test1 = []
        test2 = []
        c=0
        d=0
        for ele in res2:
            try:
                float(ele)
                res.append(ele)
            except ValueError:
                c=d

        res3 = [i for i in res if type(float(i)) is float]

        mn = 0
        for i in res3:
            if i == '0' or i =='1':
                res3.remove(i)
                mn+=1

        bnm = 0
        res6 = []
        for ii in res:
            if type(bnm) == int:
                res6.append(res[bnm])
            bnm+=1    
        mn = 0
        for i in res6:
            if i == '0' or i =='1':
                res6.remove(i)
                mn+=1

        er = 0
        for i in res6:
            if len(res6[er]) < 3:
                res6.remove(res6[er])
            er+=1


        er = 0
        for i in res3:
            if len(res3[er]) < 3:
                res3.remove(res3[er])
            er+=1
            
            
        res3 = [*set(res3)]
        res6 = [*set(res6)]

        bnm = 0
        for ii in res6:
            if type(res6[bnm]) != int:
                res6.remove(res6[bnm])
            bnm+=1   
        gh = 0
        for i in res6:
            if '.' or ','  in res6[gh]:
                res6.remove(res6[gh])
            gh+=0

        if res3 == res6:
            res5 = res3
        else:
            res4 = []
            res5 = []
            for ele in res3:
                try:
                    int(ele)
                    res4.append(ele)
                except ValueError:
                    res5.append(ele)
        if len(res5) == 0:
            zz = 0
            for i in res4:
                res4[zz] = int(res4[zz])
                zz+=1
            rrr = sorted(res4)
        else:
            zz = 0
            for i in res5:
                res5[zz] = float(res5[zz])
                zz+=1
            rrr = sorted(res5)

        # print('Total is:', rrr[-1])
        invoiceTotal = rrr[-1]
    except Exception:
        invoiceTotal = ''

    #-------------- TRY -----------

    # z1 = [i.replace(',','') for i in z1]

    # print()
    # print('\n')
    # tot = []
    # d = 0
    # for i in z1:
    #     e = 0
    #     for i in rrr:
    #         if (z1[d] == str(rrr[e])) or (z1[d] == (rrr[e])):
    #             tot.append(d)
    #         e+=1
    #     d+=1

    # dfg = ['total' , 'Total' , 'Final', 'Grand']
    # tot_final =[]
    # g = 0
    # for i in tot:
    #     h = 0
    #     for j in dfg:
    #         if tot[g] <=10: 
    #             if dfg[h] in z1[0:tot[g]]:
    #                 print('line 198' ,ind[g], z[0:ind[g]])
    #                 print('There are high chances of this being Invoice number',z[ind[g]])
    #                 print('\n')
    #                 tot_final.append(z1[tot[g]])
    #             else:
    #                 print('line 203' ,ind[g], z[0:ind[g]])
    #                 pass
    #         elif tot[g]>10:
    #             if dfg[h] in z1[tot[g]-10:tot[g]]:
    #                 print('line 208',ind[g], z[ind[g]-10:ind[g]])
    #                 print('There are high chances of this being Invoice number',z[ind[g]])
    #                 tot_final.append(z1[tot[g]])
    #             else:
    #                 print('line 213',ind[g], z[ind[g]-10:ind[g]])
    #                 print('Less Chance for else condition')
    #                 pass
    #         h+=1        
    #     g+=1


    # tot_final = sorted(tot_final)
    # print('tot_final is', sorted(tot_final))

    data = [
    {
        "Company Name": companyName,
        "Invoice Date": invoiceDate,
        "Invoice Number": invoiceNumber,
        "Invoice Total": invoiceTotal
    }
    ]
    
    jstring = json.dumps(data,indent=4)
    return(jstring)

callf=invextract(filpath)
print(callf)
