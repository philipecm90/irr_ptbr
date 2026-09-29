# -*- coding: utf-8 -*-
import re

# regras aplicadas a chaves de descricao/nome (permitem espaco inicial)
RULES = [
    # --- carregadores por codigo: "AK 5.45x39 30rnd" -> "AK 5.45x39 30 tiros" ---
    (r'^(\s*)(.+?) (\d+)\s*[Rr]nd$', r'\1\2 \3 tiros'),
    (r'^(\s*)(.+?) (\d+)\s*[Rr]ound$', r'\1\2 \3 tiros'),
    # --- descricoes de carregador ---
    (r'^(\s*)(\d+) round (.+) mag, for (.+) ammunition\.$', r'\1Carregador \3 de \2 tiros, para munição \4.'),
    (r'^(\s*)A (\d+)-round mag by (.+), for (.+) ammunition\.$', r'\1Carregador de \2 tiros da \3, para munição \4.'),
    (r'^(\s*)(\d+) round (.+) mag, for (.+) shells\.$', r'\1Carregador \3 de \2 tiros, para cartuchos \4.'),
    (r'^(\s*)(\d+) round (.+) magazine for the (.+)\.$', r'\1Carregador de \2 tiros para a \3.'),
    (r'^(\s*)(\d+) round (.+) magazine for (.+)\.$', r'\1Carregador de \2 tiros para \3.'),
    (r'^(\s*)(\d+)-round (.+) magazine for (.+)\.$', r'\1Carregador \3 de \2 tiros para \4.'),
    (r'^(\s*)(\d+) round capacity (.+)\.$', r'\1Capacidade de \2 tiros \3.'),
    (r'^(\s*)(\d+) round (.+)\.$', r'\1\3 de \2 tiros.'),
    (r'^(\s*)(.+) (\d+) round magazine\.$', r'\1Carregador \2 de \3 tiros.'),
    (r'^(\s*)(.+) magazine\.$', r'\1Carregador \2.'),
    # --- projeteis ---
    (r'^(\s*)(.+) bullet\.\s*Armor piercing\.$', r'\1Projétil \2. Perfurante.'),
    (r'^(\s*)(.+) bullet\.\s+Standard issue\.$', r'\1Projétil \2. Padrão.'),
    (r'^(\s*)(.+) bullet\.$', r'\1Projétil \2.'),
    (r'^(\s*)(.+) bullet$', r'\1Projétil \2.'),
    (r'^(\s*)(.+) buckshot\.$', r'\1Cartucho de balins \2.'),
    (r'^(\s*)(.+) slug\.$', r'\1Slug \2.'),
    # --- supressores / bocais / canos ---
    (r'^(\s*)(.+) suppressor for (.+)\.$', r'\1Supressor \2 para \3.'),
    (r'^(\s*)(.+) suppressor\.$', r'\1Supressor \2.'),
    (r'^(\s*)(.+) suppressor$', r'\1Supressor \2.'),
    (r'^(\s*)(.+) muzzle for (.+)\.$', r'\1Bocal \2 para \3.'),
    (r'^(\s*)Muzzle brake for (.+) barrels\.$', r'\1Freio de boca para canos \2.'),
    (r'^(\s*)([\d.x]+) [Ii]nch [Bb]arrel for the (.+)\.$', r'\1Cano de \2 polegadas para a \3.'),
    (r'^(\s*)A ([\d.x]+) Inch Barrel for the (.+)\.$', r'\1Cano de \2 polegadas para a \3.'),
    (r'^(\s*)(.+) barrel\.$', r'\1Cano \2.'),
    (r'^(\s*)(.+) handguard\.$', r'\1Guarda-mão \2.'),
    (r'^(\s*)(.+) stock\.$', r'\1Coronha \2.'),
    (r'^(\s*)(.+) pistol grip\.$', r'\1Empunhadura de pistola \2.'),
    # --- descricoes de arma ---
    (r'^(\s*)(.+) assault rifle designed by (.+)\.$', r'\1Fuzil de assalto \2 projetado pela \3.'),
    (r'^(\s*)(.+) assault rifle chambered in (.+)\.$', r'\1Fuzil de assalto \2 no calibre \3.'),
    (r'^(\s*)(.+) rifle designed by (.+)\.$', r'\1Rifle \2 projetado pela \3.'),
    (r'^(\s*)(.+) rifle chambered in (.+)\.$', r'\1Rifle \2 no calibre \3.'),
    (r'^(\s*)(.+) marksman rifle\. (.+)$', r'\1Rifle de precisão \2. \3'),
    (r'^(\s*)(.+) designated marksman rifle\. Manufactured by (.+)\.$', r'\1Rifle de precisão designado \2. Fabricado pela \3.'),
    (r'^(\s*)(.+) designated marksman rifle\.$', r'\1Rifle de precisão designado \2.'),
    (r'^(\s*)(.+) pistol by (.+)\.$', r'\1Pistola \2 da \3.'),
    (r'^(\s*)(.+) pistol\.$', r'\1Pistola \2.'),
    (r'^(\s*)(.+) submachine gun designed by (.+)\.$', r'\1Submetralhadora \2 projetada pela \3.'),
    (r'^(\s*)(.+) submachine gun\.$', r'\1Submetralhadora \2.'),
    (r'^(\s*)(.+) shotgun\.$', r'\1Escopeta \2.'),
    (r'^(\s*)(.+) rifle\.$', r'\1Rifle \2.'),
    (r'^(\s*)(.+) variant of (.+)\.$', r'\1Variante \2 de \3.'),
    (r'^(\s*)(.+) scope for (.+)\.$', r'\1Mira \2 para \3.'),
    (r'^(\s*)(.+) scope\.$', r'\1Mira \2.'),
    (r'^(\s*)(.+) optic\.$', r'\1Óptica \2.'),
    (r'^(\s*)(.+) sight\.$', r'\1Mira \2.'),
    # --- finais ---
    (r'^(\s*)([\d.x]+) [Ii]nch$', r'\1\2 polegadas'),
    (r'^(\s*)(\d+) Inc$', r'\1\2 polegadas'),
    (r'^(\s*)(\d+)\s*[Rr]nd (.+)$', r'\1\3 \2 tiros'),
    (r'^(\s*)(.+) (\d+)-shell$', r'\1\2 \3 cartuchos'),
    # --- genericos ---
    (r'^(\s*)(.+) for the (.+)\.$', r'\1\2 para a \3.'),
]

COMPILED = [(re.compile(p), r) for p, r in RULES]

def rule_translate(key):
    for rx, rep in COMPILED:
        m = rx.match(key)
        if m:
            try:
                out = m.expand(rep)
                if out != key:
                    return out
            except Exception:
                return None
    return None
