#!/usr/bin/env python3
"""Aller-retour de relecture DPO pour la version vulgarisée des questions PIA.

  export : pia_assistant_fr.json -> env/review/questions_vulgarisees_relecture.csv
           (Excel : séparateur « ; », UTF-8 avec BOM, une puce par ligne dans les cellules)
  import : CSV relu -> pia_assistant_fr.json (textes corrigés + colonne « valide » = oui)
"""
import csv
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
JSON_FILE = ROOT / 'pia' / 'src' / 'assets' / 'files' / 'pia_assistant_fr.json'
CSV_FILE = ROOT / 'env' / 'review' / 'questions_vulgarisees_relecture.csv'

COLUMNS = ['id', 'question_originale', 'en_clair', 'pourquoi', 'a_inclure', 'exemples', 'piege',
           'valide', 'commentaire_dpo', 'points_a_verifier']
LISTS = ('a_inclure', 'exemples')

# Points repérés lors de la relecture automatique, signalés au DPO
NOTES = {
    '113': "Vérifier qu'un code de conduite ministériel existe réellement ; sinon reformuler les exemples.",
    '226': "Vérifier la liste des mentions obligatoires du contrat de sous-traitance (art. 28 RGPD).",
}


def export():
    data = json.loads(JSON_FILE.read_text(encoding='utf-8'))
    CSV_FILE.parent.mkdir(parents=True, exist_ok=True)
    with CSV_FILE.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, delimiter=';')
        writer.writeheader()
        for qid, q in data['questions'].items():
            writer.writerow({
                'id': qid,
                'question_originale': q['original'],
                'en_clair': q['en_clair'],
                'pourquoi': q['pourquoi'],
                'a_inclure': '\n'.join(q['a_inclure']),
                'exemples': '\n'.join(q['exemples']),
                'piege': q['piege'],
                'valide': 'oui' if q.get('validated') else 'non',
                'commentaire_dpo': q.get('dpo_comment', ''),
                'points_a_verifier': NOTES.get(qid, ''),
            })
    print(f"{len(data['questions'])} questions exportées dans {CSV_FILE.relative_to(ROOT)}")


def import_():
    data = json.loads(JSON_FILE.read_text(encoding='utf-8'))
    validated = 0
    with CSV_FILE.open(encoding='utf-8-sig', newline='') as f:
        for row in csv.DictReader(f, delimiter=';'):
            q = data['questions'].get(row['id'].strip())
            if not q:
                print(f"id inconnu ignoré : {row['id']}", file=sys.stderr)
                continue
            for key in ('en_clair', 'pourquoi', 'piege'):
                q[key] = row[key].strip()
            for key in LISTS:
                q[key] = [line.strip(' -•\t') for line in row[key].splitlines() if line.strip()]
            q['validated'] = row['valide'].strip().lower() in ('oui', 'o', 'x', '1', 'yes')
            q['dpo_comment'] = row['commentaire_dpo'].strip()
            validated += q['validated']
    JSON_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f"{validated}/{len(data['questions'])} questions validées -> {JSON_FILE.relative_to(ROOT)}")


if __name__ == '__main__':
    {'export': export, 'import': import_}.get(sys.argv[1] if len(sys.argv) > 1 else '', lambda: sys.exit(__doc__))()
