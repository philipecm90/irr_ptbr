# -*- coding: utf-8 -*-
NOUN = {
    'Riflescope': 'Luneta de rifle',
    'Thermal Scope': 'Luneta térmica',
    'Hybrid Scope': 'Luneta híbrida',
    'Scope': 'Luneta',
    'Collapsible Stock': 'Coronha retrátil',
    'Vertical Foregrip': 'Empunhadura frontal vertical',
    'Thread Protector': 'Protetor de rosca',
    'Angled Foregrip': 'Empunhadura frontal angulada',
    'Folding Stock': 'Coronha dobrável',
    'Muzzle Device': 'Dispositivo de bocal',
    'Plate Carrier': 'Colete balístico',
    'Vertical Grip': 'Empunhadura vertical',
    'Sling Adapter': 'Adaptador de alça',
    'Stock Adapter': 'Adaptador de coronha',
    'Muzzle Brake': 'Freio de boca',
    'Buffer Mount': 'Suporte de recuo',
    'Carry Handle': 'Alça de transporte',
    'Pistol Grip': 'Empunhadura da pistola',
    'Front Sight': 'Mira frontal',
    'Armored Rig': 'Colete tático blindado',
    'Flash Hider': 'Apagador de chamas',
    'Buffer Tube': 'Tubo de recuo',
    'Rear Sight': 'Mira traseira',
    'Iron Sight': 'Mira de ferro',
    'Barrel Nut': 'Porca do cano',
    'Cheek Rest': 'Apoio de bochecha',
    'Handguard': 'Guarda-mão', 'Hanguard': 'Guarda-mão',
    'Buttstock': 'Soleira', 'Gas Block': 'Bloco de gás',
    'Key Chain': 'Chaveiro', 'Key Card': 'Cartão-chave',
    'Suppressor': 'Supressor', 'Silencer': 'Silenciador', 'Gas Tube': 'Tubo de gás',
    'Backpack': 'Mochila', 'Safe Key': 'Chave do cofre', 'Foregrip': 'Empunhadura frontal',
    'Document': 'Documento', 'Cabinet': 'Armário', 'Voucher': 'Voucher', 'Chassis': 'Chassi',
    'Battery': 'Bateria', 'Grenade': 'Granada', 'Barrel': 'Cano', 'Muzzle': 'Bocal',
    'Helmet': 'Capacete', 'Camera': 'Câmera', 'Laptop': 'Notebook', 'Stock': 'Coronha',
    'Sight': 'Mira', 'Crate': 'Caixote', 'Mount': 'Suporte', 'Slide': 'Corrediça',
    'Radio': 'Rádio', 'Cigar': 'Charuto', 'Plate': 'Prato', 'Rail': 'Trilho',
    'Grip': 'Empunhadura', 'Case': 'Estojo', 'Belt': 'Cinto', 'Coin': 'Moeda',
    'Ammo': 'Munição', 'Rig': 'Colete tático', 'Box': 'Caixa', 'Key': 'Chave',
    'Bag': 'Bolsa', 'Mag': 'Carregador', 'Cigarettes': 'Cigarros', 'Magazine': 'Carregador',
}
KEEP = {'Dust Cover'}
# modificadores que exigem "de"
DE = {
    'Attachments': 'de acessórios', 'Weapons': 'de armas', 'Weapon': 'de arma',
    'Ammunition': 'de munição', 'Battery': 'de bateria', 'Supply': 'de suprimento',
    'Mining': 'de mineração', 'Food': 'de comida', 'Metal': 'de metal', 'Oil': 'de óleo',
    'Concrete': 'de concreto', 'Hand': 'de mão', 'Favor': 'de favor', 'Gear': 'de equipamento',
    'Med': 'médica', 'Medic': 'médica',
}
# adjetivos simples
ADJ = {
    'Large': 'grande', 'Small': 'pequeno', 'Compact': 'compacto', 'Standard': 'padrão',
    'Threaded': 'com rosca', 'Medical': 'médica', 'Tactical': 'tático', 'Vertical': 'vertical',
    'Angled': 'angulada', 'Folding': 'dobrável', 'Collapsible': 'retrátil', 'Advanced': 'avançado',
    'Polymer': 'polímero', 'Wooden': 'madeira', 'Steel': 'aço', 'Skeleton': 'esqueleto',
    'Enhanced': 'aprimorado', 'Front': 'frontal', 'Rear': 'traseiro', 'Extended': 'estendido',
    'Field': 'de campo', 'Basic': 'básico', 'Machine': 'de máquina', 'Bandolier': 'bandoleira',
    'Antique': 'antigo', 'Golden': 'dourado', 'Old': 'velho', 'Military': 'militar',
    'Thermal': 'térmica', 'Holographic': 'holográfica', 'Hybrid': 'híbrida', 'Short': 'curto',
    'Long': 'longo', 'Slim': 'fino', 'Low': 'baixo', 'High': 'alto', 'Profile': 'perfil',
    'Combat': 'combate', 'Modular': 'modular', 'Adjustable': 'ajustável', 'Classified': 'classificado',
}
SPECIAL = {
    'Chest Rig': 'Colete peitoral',
    'Armor Plate': 'Placa de armadura',
    'Hand Grenade': 'Granada de mão',
}
ORDER = sorted(NOUN.keys(), key=len, reverse=True)

def translate_name(name):
    s = name.strip()
    if s in SPECIAL:
        return SPECIAL[s]
    if s.endswith('.') and ' for the ' in s:
        return s[:-1].replace(' for the ', ' para a ') + '.'
    for t in ORDER:
        if s == t or s.endswith(' ' + t):
            noun = NOUN[t]
            base = s[:-(len(t) + 1)] if len(s) > len(t) else ''
            if not base:
                return noun
            out = []
            for w in base.split():
                if w in DE:
                    out.append(DE[w])
                elif w in ADJ:
                    out.append(ADJ[w])
                else:
                    out.append(w)
            return noun + ' ' + ' '.join(out)
    return None

if __name__ == '__main__':
    for x in ['Battery Case', 'Large Medical Bag', 'Attachments Box', 'Large Weapons Crate',
              'AK Zenitco B-13 Rail', 'AR-15 Magpul CTR Buttstock', 'AK Izhmash Polymer Stock',
              'AAC 762-SDN-6 Suppressor', 'AK-74 Steel PATRIOT Silencer', 'M9A3 Thread Protector',
              'AVS PL SGT Armored Rig', 'Chest Rig', 'Bunker Compact Safe Key', 'Classified Document',
              'Concrete Supply Voucher', 'Mining Battery', 'F-1 Hand Grenade', 'Antique Plate',
              'Armor Plate', 'AK Izhmash Dust Cover', 'EOTECH CNVDT 1x Thermal Scope',
              '10.4 Inch barrel for the P90.', 'EOTECH Vudu 1-6x Scope', 'Small Medic Bag',
              'M700 MDT ESS Stock', 'MP5 Polymer Handguard', 'AR-10 Low Profile Gas Block',
              'Attachments Cabinet', 'Large Medical Bag', 'Food Supply Voucher']:
        print('%-38s -> %s' % (x, translate_name(x)))
