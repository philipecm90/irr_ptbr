-- PTTranslator: runtime English -> Portuguese (exact + pattern + tooltip)
-- Incursion Red River  PT-BR patch  (baseado no mecanismo do patch coreano de s10th24b)
local PT_VERSION = "0.1.0"
local SCRIPT_DIR = (debug.getinfo(1, "S").source:gsub("^@", ""):gsub("[^/\\]+$", ""))
local TR_PATH = SCRIPT_DIR .. "translations.lua"

translations = {}
tnorm = {}
unames = {}

function norm(s)
    return (s:gsub("%s+", " "):gsub("^ ", ""):gsub(" $", ""))
end

plainmap = {}
function plainnorm(s)
    return (s:gsub("<[^>]*>", ""):gsub("%s+", " "):gsub("^ ", ""):gsub(" $", ""))
end

local function loadExternal()
    local ok_tr, ext = pcall(dofile, TR_PATH)
    if ok_tr and type(ext) == "table" then
        local n = 0
        tnorm = {}
        plainmap = {}
        unames = {}
        for k, v in pairs(ext) do
            translations[k] = v
            tnorm[norm(k)] = v
            if #k > 40 then plainmap[plainnorm(k)] = v end
            if k:find(" ", 1, true) then unames[string.upper(k)] = v end
            n = n + 1
        end
        print(string.format("[PTTranslator] loaded %d translations\n", n))
    else
        print("[PTTranslator] translations.lua not loaded\n")
    end
end
loadExternal()

FAC = { None = "Nenhuma" }
function fac(f) return FAC[f] or f end

function transList(x)
    local parts = {}
    for p in string.gmatch(x, "[^,]+") do
        p = p:gsub("^%s+", ""):gsub("%s+$", "")
        parts[#parts+1] = translations[p] or p
    end
    return table.concat(parts, ", ")
end

function transItemName(x)
    if not x then return x end
    local whole = translations[x] or unames[string.upper(x)]
    if whole then return whole end
    if x:find(",", 1, true) then
        local parts = {}
        for p in string.gmatch(x, "[^,]+") do
            local q = p:gsub("^%s+", ""):gsub("%s+$", "")
            parts[#parts+1] = translations[q] or unames[string.upper(q)] or q
        end
        return table.concat(parts, ", ")
    end
    return x
end

function transTail(y)
    if not y or y == "" then return y or "" end
    return (y:gsub("[^\n]+", function(line) return transItemName(line) end))
end

MONTHS = {Jan="1",Feb="2",Mar="3",Apr="4",May="5",Jun="6",Jul="7",Aug="8",Sep="9",Oct="10",Nov="11",Dec="12",
          January="1",February="2",March="3",April="4",June="6",July="7",August="8",September="9",October="10",November="11",December="12"}

-- mapas internos (POI) traduzidos; nomes de mapa (QUARRY/BUNKER/DELTA) mantidos
locations = {
    ["factory"]="fábrica", ["military base"]="base militar", ["fishing village"]="vila de pescadores",
    ["cave"]="caverna", ["school"]="escola", ["warehouse"]="armazém", ["quarry"]="pedreira",
    ["train depot"]="depósito de trens", ["docks"]="docas", ["rice fields"]="arrozais",
    ["industrial zone"]="zona industrial", ["command room"]="sala de comando", ["med bay"]="posto médico",
    ["eastern village"]="vila oriental", ["western village"]="vila ocidental",
    ["market"]="mercado", ["bunker"]="bunker", ["delta"]="delta",
}
function transLoc(s)
    if not s then return s end
    return locations[s] or locations[string.lower(s)] or s
end

patterns = {
    {"^(%a+) (%d+), (%d%d%d%d)$",
     function(mon, day, year) local m = MONTHS[mon]; if not m then return nil end
       return tonumber(day).."/"..m.."/"..year end},
    {"^Arrival Time: (.+)$", function(x) return "Horário de chegada: "..x end},
    {"^Filter: (.+)$", function(x) return "Filtro: "..(translateString(x) or x) end},
    {"^Resources %- (.+)$", function(x) return "Recursos - "..(translateString(x) or x) end},
    {"^Item needed for: (.+)$", function(x) return "Item necessário para: "..transList(x) end},
    {"^<Red>Item needed for: (.-)</>(.*)$",
     function(list, rest) local pre, item = rest:match("^(%s*)(.*)$")
       return "<Red>Item necessário para: "..transList(list).."</>"..pre..(translateString(item) or item) end},
    {"^<Red>You haven't unlocked Rarity Tier (%d+) of (.-)%.</>$",
     function(n, f) return "<Red>Você não desbloqueou o Nível de Raridade "..n.." de "..fac(f)..".</>" end},
    {"^You haven't unlocked Rarity Tier (%d+) of (.-)%.$",
     function(n, f) return "Você não desbloqueou o Nível de Raridade "..n.." de "..fac(f).."." end},
    {"^Requires (.-) Level (%d+) ?%.$",
     function(u, n) local t = translations[u]; return "Requer "..(t or u).." Nível "..n.."." end},
    {"^Upgrading this container requires: ([%d,]+) Cash%.$",
     function(c) return "Melhorar este contêiner requer: $ "..c.." em dinheiro." end},
    {"^Upgrading this container requires (.-) Level (%d+)%.$",
     function(x, n) local t = translations[x]; return "Melhorar este contêiner requer "..(t or x).." Nível "..n.."." end},
    {"^(.-) %- Level (%d+)$",
     function(u, n) local t = translations[u]; if t then return t.." - Nível "..n end return nil end},
    {"^Refresh Missions%. Costs %$ ([%d,]+)%.$",
     function(c) return "Atualizar missões. Custa $ "..c.."." end},
    {"^(.-) is ([%d,]+)/([%d,]+)%.$",
     function(x, a, b) local t = translateString(x); return (t or x).." em estoque "..a.."/"..b.."." end},
    {"^<Red>Cannot Equip the Weapon%. Some of the Vital parts are missing : (.-)%.</>$",
     function(x) return "<Red>Não é possível equipar a arma. Faltam algumas peças vitais: "..(translateString(x) or x)..".</>" end},
    {"^Starting in (%d+)s$", function(n) return "Começando em "..n.."s" end},
    {"^Required (.-):%s*$", function(x) return transItemName(x).." necessário: " end},
    {"^Linked Search: (.+)$", function(x) return "Busca vinculada: "..(translateString(x) or x) end},
    {"^Repair for %$([%d,]+)$", function(c) return "Consertar por $"..c end},
    {"^(.+) Joined The Party$", function(x) return x.." entrou no grupo" end},
    {"^(.+) Left The Party$", function(x) return x.." saiu do grupo" end},
    {"^(.+) HAS JOINED THE LOBBY$", function(x) return x.." ENTROU NO LOBBY" end},
    {"^(.+) HAS LEFT THE LOBBY$", function(x) return x.." SAIU DO LOBBY" end},
    {"^(.+) is dead%.$", function(x) return x.." morreu." end},
    {"^(.+) has been revived%.$", function(x) return x.." foi reanimado." end},
    {"^(%u+) Mercenary$", function(f) return f.." Mercenário" end},
    {"^([%d,]+) (.-) gathered%.$",
     function(n, r) return (translateString(r) or r)..": "..n.." coletado(s)." end},
    {"^Press <Red>F</> to <Red>Pickup</> (.+)$",
     function(x) return "Pressione <Red>F</> para <Red>Pegar</>: "..(translateString(x) or x) end},
    {"^Press <Red>F</> to <Red>upgrade</> the (.+)%.$",
     function(x) local t = translateString(x); if not t then return nil end
       return "Pressione <Red>F</> para <Red>melhorar</> "..t.."." end},
    {"^Hold <Red>F</> to loot (.+)$",
     function(x) return "Segure <Red>F</> para saquear: "..(translateString(x) or x) end},
    {"^Hold <Red>F</> to place the (%w+) here%.?$",
     function(x) local o={bomb="bomba",bug="escuta",jammer="bloqueador"}
       return "Segure <Red>F</> para colocar "..(o[x] or x).." aqui" end},
    {"^Sell %[%$ ([%d,]+)%]$", function(c) return "Vender [$ "..c.."]" end},
    {"^Buy %[%$ ([%d,]+)%]$", function(c) return "Comprar [$ "..c.."]" end},
    {"^Cannot purchase: (.+)$", function(x) return "Não é possível comprar: "..(translateString(x) or x) end},
    {"^You need to upgrade intel center to level (%d+) to view these overlays%.$",
     function(n) return "Você precisa melhorar o Centro de Inteligência para o nível "..n.." para ver estas sobreposições." end},
    {"^Deliver ([%d,]+) (.+)%.$", function(n, x) return "Entregue "..n.." "..(translateString(x) or x).."." end},
    {"^Eliminate (%d+) with an? (.+)%.$",
     function(n, x) return "Elimine "..n.." com "..(translateString(x) or x).."." end},
    {"^Eliminate (%d+) with the weapon from (.+)%.$",
     function(n, x) return "Elimine "..n.." com a arma de "..(translateString(x) or x).."." end},
    {"^Hint: (.+)$", function(x) return "Dica: "..(translateString(x) or x) end},
    {"^Eliminate (%d+) (.+)%.$", function(n, x) return "Elimine "..n.." "..(translateString(x) or x).."." end},
    {"^Eliminate (%d+)%.$", function(n) return "Elimine "..n.."." end},
    {"^Find & Retrieve the (.+)%.$", function(x) return "Encontre e recupere "..(translateString(x) or x).."." end},
    {"^Find & Retrieve (.+)%.$", function(x) return "Encontre e recupere "..(translateString(x) or x).."." end},
    {"^Use (.+) to upgrade (.+)%.$",
     function(x, y) return "Use "..(translateString(x) or x).." para melhorar "..(translateString(y) or y).."." end},
    {"^Complete (%d+) operations? of type (.+)%.$",
     function(n, x) return "Conclua "..n.." operação(ões) do tipo "..(translateString(x) or x).."." end},
    {"^Deliver the (.+)%.$", function(x) return "Entregue "..(translateString(x) or x).."." end},
    {"^Kill (%d+) (%u+) soldiers at any location%.$", function(n, f) return "Mate "..n.." soldados "..f.." em qualquer local." end},
    {"^Kill (%d+) (%u+) soldiers at (.+)%.$", function(n, f, loc) return "Mate "..n.." soldados "..f.." em "..transLoc(loc).."." end},
    {"^Kill (%d+) (%u+) soldiers on (.+)%.$", function(n, f, loc) return "Mate "..n.." soldados "..f.." em "..transLoc(loc).."." end},
    {"^Sell to the vendor a (.+) (%d+) times%.$",
     function(x, n) return "Venda "..(translateString(x) or x).." ao vendedor "..n.." vezes." end},
    {"^Cannot download (.+)%.$", function(x) return "Não é possível baixar "..x.."." end},
    {"^Cannot read (.+)%.$", function(x) return "Não é possível ler "..x.."." end},
    {"^Cannot run (.+)%.$", function(x) return "Não é possível executar "..x.."." end},
    {"^Cannot scan (.+)%.$", function(x) return "Não é possível escanear "..x.."." end},
    {"^Initiating download of (.+)%.%.%.$", function(x) return "Iniciando download de "..x.."..." end},
    {"^(.-) downloaded file successfully%. ?$", function(x) return x.." baixado com sucesso. " end},
    {'^Error: Command "(.-)" not recognized%. Please enter a valid command%. Or type "help" for a list of available commands%.$',
     function(x) return 'Erro: Comando "'..x..'" não reconhecido. Insira um comando válido. Ou digite "help" para ver a lista de comandos disponíveis.' end},
    {"^<Red>Can.t remove parts from reward items%.</>(.*)$",
     function(rest) return "<Red>Não é possível remover peças de itens de recompensa.</>"..(translateString(rest) or rest) end},
    {"^Cannot add (.-) to (.-)%. The modified item will take more space than is available%. Try repositioning the item to another part of your inventory%.$",
     function(a,b) return "Não é possível adicionar "..(translateString(a) or a).." a "..(translateString(b) or b)..". O item modificado ocupará mais espaço do que o disponível. Tente reposicionar o item em outra parte do inventário." end},
    {"^This attachment cannot be removed since it is required by the following Attachment%(s%) : (.+)%.$",
     function(x) return "Este acessório não pode ser removido, pois é necessário para o(s) seguinte(s) acessório(s): "..(translateString(x) or x).."." end},
    {"^<Red>This item is conflicting with the following equipped Item%(s%) : (.-)%.?</>(.*)$",
     function(x, y) return "<Red>Este item está em conflito com o(s) seguinte(s) item(ns) equipado(s): "..transItemName(x)..".</>"..transTail(y) end},
    {"^<Red>This item is conflicting with the following Item%(s%) : (.-)%.?</>(.*)$",
     function(x, y) return "<Red>Este item está em conflito com o(s) seguinte(s) item(ns): "..transItemName(x)..".</>"..transTail(y) end},
    {"^This item is conflicting with the following equipped Item%(s%) : (.-)%.?$",
     function(x) return "Este item está em conflito com o(s) seguinte(s) item(ns) equipado(s): "..transItemName(x).."." end},
    {"^This item is conflicting with the following Item%(s%) : (.-)%.?$",
     function(x) return "Este item está em conflito com o(s) seguinte(s) item(ns): "..transItemName(x).."." end},
    {"^<Red>You need to install the following Item%(s%) first: (.-)%.?</>(.*)$",
     function(x, y) return "<Red>Você precisa instalar o(s) seguinte(s) item(ns) primeiro: "..transItemName(x)..".</>"..transTail(y) end},
    {"^You need to install the following Item%(s%) first: (.+)%.$",
     function(x) return "Você precisa instalar o(s) seguinte(s) item(ns) primeiro: "..transItemName(x).."." end},
    {"^Deliver ([%d,]+) (.+) to the vendor%.$", function(n,x) return "Entregue "..n.." "..(translateString(x) or x).." ao vendedor." end},
    {"^Sell ([%d,]+) (.+) to the vendor$", function(n,x) return "Venda "..n.." "..(translateString(x) or x).." ao vendedor" end},
    {"^Extract (%d+) times successfully from a raid%.$", function(n) return "Extraia com sucesso de uma raid "..n.." vezes." end},
    {"^Retrieve evidence from (.+)%.$", function(x) return "Recupere evidências em "..transLoc(x).."." end},
    {"^Find (.+) location%.$", function(x) return "Encontre o local: "..transLoc(x).."." end},
    {"^Investigate (.+) location%.$", function(x) return "Investigue o local: "..transLoc(x).."." end},
    {"^Successfully logged in as %[(.+)%]%.$", function(x) return "Login bem-sucedido como ["..x.."]." end},
    {"^(.-) has not access to this directory%.$", function(x) return x.." não tem acesso a este diretório." end},
    {"^(Alpha[ #v]+%d[%w%.%- ]*)$", function(x) return x.."    ~ PT-BR" end},
    {"^(ALPHA[ #v]+%d[%w%.%- ]*)$", function(x) return x.."    ~ PT-BR" end},
    {"^Press <Red>F</> to <Red>add</> ?(.-) to inventory%.$", function(x) return "Pressione <Red>F</> para <Red>adicionar</> "..(translateString(x) or x).." ao inventário." end},
    {"^\"(.+)\"$", function(x) local t = translateString(x); if t then return '"'..t..'"' end return nil end},
    {"^<Red>(.-)</>(.*)$",
     function(x, y) local t = translateString(x); if t then return "<Red>"..t.."</>"..(y or "") end return nil end},
}

translateString = function(s)
    local tr = translations[s]
    if tr then return tr end
    if string.find(s, " > ", 1, true) then
        local out, changed = {}, false
        for part in string.gmatch(s, "[^>]+") do
            part = part:gsub("^%s+", ""):gsub("%s+$", "")
            local t = translations[part]
            if t then changed = true; out[#out+1] = t else out[#out+1] = part end
        end
        if changed then return table.concat(out, " > ") end
    end
    for _, p in ipairs(patterns) do
        local caps = { string.match(s, p[1]) }
        if caps[1] ~= nil then
            local ok, res = pcall(function() return p[2](table.unpack(caps)) end)
            if ok and res then return res end
        end
    end
    local nm = tnorm[norm(s)]
    if nm then return nm end
    if #s > 40 then
        local pm = plainmap[plainnorm(s)]
        if pm and pm ~= s then return pm end
    end
    return nil
end

function toText(s)
    local KTL = StaticFindObject("/Script/Engine.Default__KismetTextLibrary")
    if KTL and KTL:IsValid() then return KTL:Conv_StringToText(s) end
    return nil
end

inHook = false
local DBG = SCRIPT_DIR .. "pt_dump.txt"
local dbgseen = {}
local function dbglog(s, tr)
    if dbgseen[s] then return end
    dbgseen[s] = true
    local f = io.open(DBG, "a")
    if f then f:write(s, "\t=>\t", tr, "\n"); f:close() end
end
function onSetText(self)
    if inHook then return end
    pcall(function()
        local w = self:get()
        if not (w and w:IsValid()) then return end
        local s = w:GetText():ToString()
        if not (s and #s > 0) then return end
        local tr = translateString(s)
        if tr and tr ~= s then
            dbglog(s, tr)
            local ft = toText(tr)
            if ft and w:IsValid() then inHook = true; w:SetText(ft) end
        end
    end)
    inHook = false
end
RegisterHook("/Script/UMG.TextBlock:SetText", function() end, function(self) onSetText(self) end)
RegisterHook("/Script/UMG.RichTextBlock:SetText", function() end, function(self) onSetText(self) end)
pcall(function() RegisterHook("/Script/IRRCoreUI.IRRTextBlock:SetText", function() end, function(self) onSetText(self) end) end)

function onSetToolTip(self)
    if inHook then return end
    pcall(function()
        local w = self:get()
        if not (w and w:IsValid()) then return end
        local tt = w.ToolTipText
        if not tt then return end
        local s = tt:ToString()
        if not (s and #s > 0) then return end
        local tr = translateString(s)
        if tr and tr ~= s then
            local ft = toText(tr)
            if ft and w:IsValid() then inHook = true; w:SetToolTipText(ft) end
        end
    end)
    inHook = false
end
RegisterHook("/Script/UMG.Widget:SetToolTipText", function() end, function(self) onSetToolTip(self) end)

print("[PTTranslator] Incursion Red River PT-BR v" .. PT_VERSION .. " loaded.\n")
