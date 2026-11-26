import csv, collections, sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from xml.sax.saxutils import escape as E

src, out = sys.argv[1], sys.argv[2]
F='/usr/share/fonts/dejavu-sans-fonts/'
pdfmetrics.registerFont(TTFont('D', F+'DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DB', F+'DejaVuSans-Bold.ttf'))
pdfmetrics.registerFont(TTFont('DI', F+'DejaVuSans-Oblique.ttf'))
pdfmetrics.registerFontFamily('D', normal='D', bold='DB', italic='DI', boldItalic='DB')

INK=colors.HexColor('#1f2933'); MUTED=colors.HexColor('#5b6770'); BLUE=colors.HexColor('#1d4f91')
LINE=colors.HexColor('#c9d1d9'); HEAD=colors.HexColor('#e8eef6'); WARN=colors.HexColor('#fff4d6')
def st(name, **k):
    base=dict(fontName='D', fontSize=9.5, leading=13.5, textColor=INK, alignment=TA_LEFT)
    base.update(k); return ParagraphStyle(name, **base)
S=dict(
 title=st('t', fontName='DB', fontSize=17, leading=22, textColor=BLUE, spaceAfter=3),
 sub=st('s', fontSize=9.5, textColor=MUTED, spaceAfter=10),
 h1=st('h1', fontName='DB', fontSize=13, leading=17, textColor=BLUE, spaceBefore=12, spaceAfter=6),
 h2=st('h2', fontName='DB', fontSize=10.5, leading=14, spaceBefore=9, spaceAfter=3),
 p=st('p', spaceAfter=6),
 q=st('q', fontName='DB', spaceAfter=2),
 qd=st('qd', spaceAfter=3),
 qa=st('qa', textColor=MUTED, fontSize=8.5, spaceAfter=9),
 cell=st('c', fontSize=8.3, leading=11),
 cellb=st('cb', fontSize=8.3, leading=11, fontName='DB'),
 note=st('n', fontSize=7.8, leading=10.3, textColor=colors.HexColor('#6b4e00')),
 th=st('th', fontSize=8.3, leading=11, fontName='DB'),
)
P=lambda t,s='p': Paragraph(t, S[s])

rows=list(csv.DictReader(open(src, encoding='utf-8-sig'), delimiter=';'))
SECTIONS=['Mesures portant sur les données','Mesures générales de sécurité','Mesures organisationnelles']
# ordre des catégories PIA = ordre de la base de connaissances (fichier YAML)
import re
order=[]; 
for line in open(sys.argv[3], encoding='utf-8'):
    m=re.match(r'  (PIA_\w+): \{ label: "(.*?)", section: "(.*?)" \}', line)
    if m: order.append(m.groups())
bycat=collections.defaultdict(list)
for r in rows: bycat[r['code_pia']].append(r)
n_conf=sum(1 for r in rows if r['a_confirmer'])
empty=[lab for code,lab,sec in order if not bycat[code]]

def footer(c, d):
    c.saveState(); c.setFont('D', 7.5); c.setFillColor(MUTED)
    c.drawString(18*mm, 10*mm, "Correspondance des mesures MonServiceSécurisé et PIA — premier jet du 26 novembre 2026, à valider")
    c.drawRightString(A4[0]-18*mm, 10*mm, f"{d.page}")
    c.restoreState()

doc=SimpleDocTemplate(out, pagesize=A4, leftMargin=18*mm, rightMargin=18*mm, topMargin=16*mm, bottomMargin=18*mm,
    title="Correspondance des mesures MonServiceSécurisé et PIA", author="Incubateur IA, DRASI, rectorat de Paris", lang='fr-FR')
W=A4[0]-36*mm
story=[]
story.append(P("Correspondance entre les mesures de MonServiceSécurisé et les mesures du PIA", 'title'))
story.append(P("Premier jet du 26 novembre 2026, à valider par le DPD et le RSSI · Incubateur IA, DRASI, rectorat de Paris", 'sub'))

story.append(P("Contexte", 'h1'))
story.append(P("À l'étape « Sécurité » du parcours guidé, MonServiceSécurisé (ANSSI) propose des mesures de sécurité adaptées au service décrit. "
 "Lors de la séance du 26 novembre, il a été décidé que ces mesures seraient reportées dans la section 3.1 du PIA, "
 "« Mesures existantes ou prévues », en respectant les catégories de mesures du PIA, et que le porteur de projet indiquerait pour chacune si elle est mise en œuvre."))
story.append(P(f"Le référentiel de MonServiceSécurisé compte {len(rows)} mesures. Le PIA propose {len(order)} catégories de mesures, réparties en trois familles. "
 f"Le tableau ci-après range chaque mesure de MonServiceSécurisé dans une seule catégorie du PIA. Ce rangement a été fait à partir des intitulés ; "
 f"{n_conf} rattachements sont signalés « à confirmer », avec la raison du doute."))

story.append(P("Questions au DPD", 'h1'))
Q=[
 ("Mesures qui relèvent du RGPD plutôt que de la sécurité",
  "MonServiceSécurisé contient des mesures sur l'information des personnes (RGPD.4), l'exercice des droits (RGPD.5) et les durées de conservation (RGPD.3). "
  "Ces sujets sont déjà traités dans la section 2 du PIA. Faut-il les reporter aussi en 3.1, ou les écarter ?"),
 ("Catégories très chargées",
  f"« Contrôle des accès logiques » reçoit {len(bycat['PIA_TEC_CTLA'])} mesures et « Sécurisation de l'exploitation » {len(bycat['PIA_SEC_EXP'])}. "
  "Une fiche de mesure aussi longue reste-t-elle lisible dans le PIA, ou faut-il la découper en sous-ensembles (authentification, droits, comptes d'administration) ?"),
 ("Continuité d'activité",
  "Le PIA n'a pas de catégorie pour le plan de reprise, la durée d'interruption admissible ou la haute disponibilité (CONTINU.3, 5 et 6). "
  "Elles sont rattachées à « Sauvegarde des données » ou à « Sécurisation de l'exploitation ». Ce choix convient-il ?"),
 ("Journalisation ou traçabilité",
  "Le PIA distingue « Journalisation » (mesure portant sur les données) et « Traçabilité » (mesure générale de sécurité). "
  "Les quatre mesures de MonServiceSécurisé sur les journaux sont rangées dans « Traçabilité ». Laquelle des deux catégories faut-il retenir ?"),
 ("Catégories du PIA sans mesure correspondante",
  f"{len(empty)} catégories ne reçoivent aucune mesure de MonServiceSécurisé : " + ", ".join(empty) + ". "
  "Le porteur de projet doit-il les renseigner lui-même, et faut-il le lui rappeler dans le parcours ?"),
 ("États possibles d'une mesure",
  "La section 3.1 s'intitule « Mesures existantes ou prévues ». Deux états suffisent-ils (mise en œuvre, non mise en œuvre), "
  "ou faut-il aussi « prévue » et « sans objet » ? Une mesure non mise en œuvre doit-elle être accompagnée d'une justification ?"),
 ("Validation de la table",
  "Les rattachements signalés « à confirmer » portent surtout sur des choix techniques (administration, messagerie, interconnexions). "
  "Le RSSI doit-il les valider avec vous, ou votre visa suffit-il pour cette première version ?"),
]
for i,(t,d) in enumerate(Q,1):
    story.append(KeepTogether([P(f"{i}. {E(t)}", 'q'), P(E(d), 'qd'), P("Réponse : " + "." * 150, 'qa')]))

story.append(P("Vue d'ensemble", 'h1'))
data=[[P("Famille du PIA",'th'), P("Catégorie de mesures du PIA",'th'), P("Mesures MSS",'th'), P("À confirmer",'th')]]
styl=[('BACKGROUND',(0,0),(-1,0),HEAD),('GRID',(0,0),(-1,-1),0.4,LINE),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
      ('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),('ALIGN',(2,0),(3,-1),'CENTER')]
i=1
for sec in SECTIONS:
    cats=[(c,l) for c,l,s in order if s==sec]
    start=i
    for c,l in cats:
        n=len(bycat[c]); k=sum(1 for r in bycat[c] if r['a_confirmer'])
        data.append([P(E(sec),'cellb') if i==start else '', P(E(l),'cell'), P(str(n) if n else "aucune",'cell'), P(str(k) if k else "",'cell')])
        i+=1
    styl.append(('SPAN',(0,start),(0,i-1))); styl.append(('VALIGN',(0,start),(0,i-1),'TOP'))
data.append([P("Total",'cellb'),'',P(str(len(rows)),'cellb'),P(str(n_conf),'cellb')])
t=Table(data, colWidths=[W*0.25,W*0.47,W*0.14,W*0.14], repeatRows=1); t.setStyle(TableStyle(styl)); story.append(t)
story.append(Spacer(1,6))
story.append(P("MSS : MonServiceSécurisé. Les lignes sur fond jaune du tableau détaillé sont les rattachements à confirmer.", 'qa'))

story.append(PageBreak())
story.append(P("Tableau détaillé", 'h1'))
story.append(P("Les références (par exemple AUTH.7) sont celles du référentiel de MonServiceSécurisé."))
for sec in SECTIONS:
    story.append(P(E(sec), 'h1'))
    for c,l in [(c,l) for c,l,s in order if s==sec]:
        rs=bycat[c]
        head=P(f"{E(l)} <font name='D' color='#5b6770'>— {len(rs)} mesure{'s' if len(rs)>1 else ''}</font>" if rs else f"{E(l)} <font name='D' color='#5b6770'>— aucune mesure de MonServiceSécurisé</font>", 'h2')
        if not rs: story.append(head); continue
        data=[[P("Réf.",'th'), P("Mesure de MonServiceSécurisé",'th'), P("Remarque",'th')]]
        styl=[('BACKGROUND',(0,0),(-1,0),HEAD),('GRID',(0,0),(-1,-1),0.4,LINE),('VALIGN',(0,0),(-1,-1),'TOP'),
              ('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3)]
        for j,r in enumerate(rs,1):
            data.append([P(E(r['id_mss']).replace('_','_<wbr/>'),'cell'), P(E(r['mesure_mss']),'cell'), P(E(r['remarque']),'note') if r['remarque'] else ''])
            if r['a_confirmer']: styl.append(('BACKGROUND',(0,j),(-1,j),WARN))
        t=Table(data, colWidths=[W*0.16,W*0.46,W*0.38], repeatRows=1); t.setStyle(TableStyle(styl))
        story.append(KeepTogether([head, t]) if len(rs)<=8 else head)
        if len(rs)>8: story.append(t)
doc.build(story, onFirstPage=footer, onLaterPages=footer)
