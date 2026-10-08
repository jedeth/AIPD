#!/usr/bin/env python3
"""Génère la version vulgarisée des questions standard du questionnaire PIA (CNIL).

Seuls des textes publics sont envoyés au LLM (questions, aides et fiches de la base
de connaissances CNIL) : aucune donnée utilisateur.

Usage : generate_simplified_questions.py [--only 111,112] [--model gpt-oss-120b]
Sortie : pia/src/assets/files/pia_assistant_fr.json (statut "brouillon" à faire valider).
Les entrées déjà validées (validated: true) ne sont jamais régénérées.
"""
import argparse
import datetime
import html
import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
PIA = ROOT / 'pia'
ENV_FILE = ROOT / 'env' / 'server' / '.env'
OUTPUT = PIA / 'src' / 'assets' / 'files' / 'pia_assistant_fr.json'
# Albert limite gpt-oss-120b à 10 requêtes/minute : on espace les appels
PAUSE_SECONDS = 7
RATE_LIMIT_WAIT = 30

SYSTEM = """Tu aides des agents de l'Éducation nationale (chefs d'établissement, gestionnaires,
enseignants, agents administratifs) qui ne sont ni juristes ni informaticiens à remplir une
analyse d'impact relative à la protection des données (AIPD / PIA, article 35 du RGPD) avec
l'outil PIA de la CNIL.

Pour la question fournie, produis une aide en français clair : phrases courtes, vocabulaire
courant, pas de jargon (si un terme juridique est indispensable, explique-le entre parenthèses).
Reste fidèle au sens de la question et aux fiches CNIL fournies : n'ajoute aucune obligation
juridique qui n'y figure pas.
Ne cite JAMAIS de durée légale, d'article de loi, de code ou de texte réglementaire précis qui
ne figure pas dans les fiches CNIL fournies. Dans les exemples, n'écris pas « conformément à
la loi » ou « 5 ans » comme s'il s'agissait d'une règle : écris plutôt « durée fixée par le
référentiel applicable (à vérifier avec le DPO ou les archives) ».
N'écris AUCUN chiffre de durée de conservation, même dans les exemples.
N'invente aucun nom de code de conduite, de label, de certification ou de référentiel : reste
générique (« le référentiel de sécurité de votre ministère, s'il existe », « une certification
de sécurité de l'hébergeur ») sauf s'il est cité dans les fiches CNIL fournies.

Réponds UNIQUEMENT avec un objet JSON de la forme :
{
  "en_clair": "la question reformulée simplement, 1 ou 2 phrases, à la 2e personne (vous)",
  "pourquoi": "pourquoi on pose cette question, 1 ou 2 phrases",
  "a_inclure": ["3 à 5 éléments concrets à mettre dans la réponse"],
  "exemples": ["2 ou 3 exemples courts tirés d'un établissement scolaire ou d'un service académique"],
  "piege": "une erreur fréquente à éviter, 1 phrase"
}"""

GAUGE_HINT = """Cette question se répond avec une jauge à 4 niveaux (négligeable, limitée, importante,
maximale) puis une justification écrite. Dans "a_inclure", explique concrètement à quoi
correspond chaque niveau pour ce critère."""

LIST_HINT = """Cette question se répond par une liste de mots-clés (étiquettes). Les exemples doivent
être des étiquettes courtes (quelques mots), pas des phrases."""


def load_env():
    env = {}
    for line in ENV_FILE.read_text(encoding='utf-8').splitlines():
        if '=' in line and not line.lstrip().startswith('#'):
            key, value = line.split('=', 1)
            env[key.strip()] = value.strip()
    return env


def translator():
    fr = json.loads((PIA / 'src/assets/i18n/fr.json').read_text(encoding='utf-8'))

    def t(key):
        node = fr
        for part in (key or '').split('.'):
            if isinstance(node, dict) and part in node:
                node = node[part]
            else:
                return key or ''
        return node if isinstance(node, str) else key

    return t


def strip_html(text):
    text = re.sub(r'<[^>]+>', ' ', text or '')
    return re.sub(r'\s+', ' ', html.unescape(text)).strip()


def standard_questions():
    t = translator()
    arch = json.loads((PIA / 'src/assets/files/pia_architecture.json').read_text(encoding='utf-8'))
    kb = {k['slug']: k for k in json.loads((PIA / 'src/assets/files/pia_knowledge-base.json').read_text(encoding='utf-8'))}
    for section in arch['sections']:
        for item in section['items']:
            for q in item.get('questions', []):
                knowledge = [
                    {'name': strip_html(t(kb[s]['name'])), 'description': strip_html(t(kb[s]['description']))[:1200]}
                    for s in q.get('link_knowledge_base', []) if s in kb
                ]
                yield {
                    'id': str(q['id']),
                    'title_key': q['title'],
                    'answer_type': q['answer_type'],
                    'section': strip_html(t(section['title'])),
                    'item': strip_html(t(item['title'])),
                    'item_help': strip_html(t(item.get('short_help', ''))),
                    'title': strip_html(t(q['title'])),
                    'placeholder': strip_html(t(q.get('placeholder', ''))),
                    'knowledge': knowledge,
                }


def prompt_for(q):
    parts = [
        f"Partie du questionnaire : {q['section']} > {q['item']}",
        f"Présentation de cette partie : {q['item_help']}",
        f"Question : {q['title']}",
        f"Aide de la CNIL : {q['placeholder']}",
    ]
    if q['answer_type'] == 'gauge':
        parts.append(GAUGE_HINT)
    elif q['answer_type'] == 'list':
        parts.append(LIST_HINT)
    if q['knowledge']:
        parts.append('Fiches de la base de connaissances CNIL liées à la question :')
        parts += [f"- {k['name']} : {k['description']}" for k in q['knowledge']]
    return '\n'.join(parts)


def call_llm(env, model, prompt):
    body = json.dumps({
        'model': model,
        'temperature': 0.2,
        'response_format': {'type': 'json_object'},
        'messages': [{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': prompt}],
    }).encode()
    request = urllib.request.Request(
        env['LLM_BASE_URL'].rstrip('/') + '/chat/completions', data=body,
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {env['LLM_API_KEY']}"})
    with urllib.request.urlopen(request, timeout=180) as response:
        content = json.loads(response.read())['choices'][0]['message']['content']
    content = re.sub(r'^```(?:json)?|```$', '', content.strip()).strip()
    data = json.loads(content)
    expected = {'en_clair': str, 'pourquoi': str, 'a_inclure': list, 'exemples': list, 'piege': str}
    for key, kind in expected.items():
        if not isinstance(data.get(key), kind):
            raise ValueError(f'champ {key} manquant ou invalide')
    return {key: data[key] for key in expected}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--only', help='ids séparés par des virgules')
    parser.add_argument('--model')
    args = parser.parse_args()

    env = load_env()
    model = args.model or env.get('LLM_MODEL') or 'gpt-oss-120b'
    only = set(args.only.split(',')) if args.only else None

    existing = json.loads(OUTPUT.read_text(encoding='utf-8')) if OUTPUT.exists() else {'questions': {}}
    questions = existing.get('questions', {})

    for q in standard_questions():
        if only and q['id'] not in only:
            continue
        if questions.get(q['id'], {}).get('validated'):
            print(f"{q['id']} : déjà validée, ignorée")
            continue
        content = None
        for attempt in range(5):
            try:
                started = time.time()
                content = call_llm(env, model, prompt_for(q))
                break
            except urllib.error.HTTPError as error:
                if error.code != 429:
                    print(f"{q['id']} : tentative {attempt + 1} échouée ({error})", file=sys.stderr)
                time.sleep(RATE_LIMIT_WAIT if error.code == 429 else PAUSE_SECONDS)
            except Exception as error:  # noqa: BLE001 - réponse invalide : on réessaie
                print(f"{q['id']} : tentative {attempt + 1} échouée ({error})", file=sys.stderr)
        time.sleep(PAUSE_SECONDS)
        if content is None:
            print(f"{q['id']} : abandonnée", file=sys.stderr)
            continue
        questions[q['id']] = {
            'title_key': q['title_key'],
            'original': q['title'],
            **content,
            'validated': False,
            'model': model,
        }
        print(f"{q['id']} : ok ({time.time() - started:.1f} s) - {content['en_clair'][:80]}")

    output = {
        'meta': {
            'description': 'Version vulgarisée des questions standard du PIA (CNIL). '
                           "Générée par IA à partir des textes publics du questionnaire ; "
                           "à faire valider question par question par le DPO.",
            'generated_at': datetime.date.today().isoformat(),
        },
        'questions': dict(sorted(questions.items())),
    }
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'\n{len(questions)} questions dans {OUTPUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
