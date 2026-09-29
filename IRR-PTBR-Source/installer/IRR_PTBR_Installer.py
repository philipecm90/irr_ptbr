#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instalador da Traducao PT-BR para Incursion Red River
- Detecta a pasta do jogo (Steam ou copia local)
- Faz backup do estado original antes de instalar
- Instala: patch pak de traducao + UE4SS + PTTranslator (traducao em runtime)
- Permite desinstalar / restaurar o idioma original
"""
import os
import sys
import shutil
import hashlib
import datetime
import argparse

MOD_PAK = "pakchunk999-IRRPTBR_P.pak"
BACKUP_DIR = "_IRRPTBR_backup"
PAKS_REL = os.path.join("Test_C", "Content", "Paks")
EXE_REL = os.path.join("Test_C", "Binaries", "Win64", "Test_C-Win64-Shipping.exe")
GAME_FOLDER_NAMES = [
    "PROJECT QUARANTINE",
    "Incursion Red River",
    "Incursion.Red.River",
    "IncursionRedRiver",
]


def resource_path(name):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)


def sha1_file(path, chunk=1 << 20):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def human(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return "%.1f %s" % (n, unit)
        n /= 1024.0


def safe_log(msg):
    try:
        if sys.stdout is not None:
            print(msg)
    except Exception:
        pass


def is_game_root(path):
    if not path:
        return False
    return os.path.isdir(os.path.join(path, PAKS_REL))


def is_game_running():
    try:
        out = os.popen('tasklist /FI "IMAGENAME eq Test_C-Win64-Shipping.exe"').read().lower()
        return "test_c-win64-shipping.exe" in out
    except Exception:
        return False


# ----------------------------------------------------------------------------
# Deteccao
# ----------------------------------------------------------------------------
def _steam_library_paths(steam_root):
    libs = []
    if not steam_root:
        return libs
    vdf = os.path.join(steam_root, "steamapps", "libraryfolders.vdf")
    if os.path.isfile(vdf):
        try:
            with open(vdf, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if '"path"' in line:
                        parts = line.split('"')
                        if len(parts) >= 4:
                            libs.append(parts[3].replace("\\\\", "\\"))
        except Exception:
            pass
    libs.append(steam_root)
    return libs


def _registry_steam():
    roots = []
    try:
        import winreg
        keys = [
            (winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam", "SteamPath"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam", "InstallPath"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam", "InstallPath"),
        ]
        for hive, key, val in keys:
            try:
                with winreg.OpenKey(hive, key) as k:
                    roots.append(winreg.QueryValueEx(k, val)[0])
            except OSError:
                pass
    except Exception:
        pass
    return roots


def find_game_roots():
    found = []

    def add(p):
        if p and is_game_root(p) and p not in found:
            found.append(p)

    for steam in _registry_steam():
        for lib in _steam_library_paths(steam):
            for name in GAME_FOLDER_NAMES:
                add(os.path.join(lib, "steamapps", "common", name))

    common_parents = [
        r"C:\Program Files (x86)\Steam\steamapps\common",
        r"C:\Program Files\Steam\steamapps\common",
        r"C:\Games",
        r"D:\Games",
        r"E:\Games",
        "C:\\",
        "D:\\",
        "E:\\",
        os.path.expanduser("~"),
        os.path.join(os.path.expanduser("~"), "Desktop"),
        os.path.join(os.path.expanduser("~"), "Downloads"),
    ]
    for parent in common_parents:
        if not os.path.isdir(parent):
            continue
        for name in GAME_FOLDER_NAMES:
            add(os.path.join(parent, name))
        try:
            for entry in os.listdir(parent):
                low = entry.lower()
                if "incursion" in low and "red" in low:
                    add(os.path.join(parent, entry))
        except Exception:
            pass

    here = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, "frozen", False) else __file__))
    add(here)
    add(os.path.dirname(here))
    return found


# ----------------------------------------------------------------------------
# Payload
# ----------------------------------------------------------------------------
def payload_root():
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    for cand in (os.path.join(base, "payload"), os.path.join(base, "..", "payload")):
        if os.path.isdir(cand):
            return os.path.abspath(cand)
    return os.path.join(base, "payload")


def payload_files():
    proot = payload_root()
    out = []
    for dp, dn, fn in os.walk(proot):
        for f in fn:
            full = os.path.join(dp, f)
            rel = os.path.relpath(full, proot)
            out.append((rel, full))
    return out


# ----------------------------------------------------------------------------
# Backup / instalacao
# ----------------------------------------------------------------------------
def install(root, log=safe_log):
    if not is_game_root(root):
        raise RuntimeError("Pasta do jogo invalida (nao encontrei %s)" % PAKS_REL)
    files = payload_files()
    if not files:
        raise RuntimeError("Payload nao encontrado (a pasta 'payload' deve estar junto do instalador).")
    if is_game_running():
        log("AVISO: o jogo parece estar aberto. Feche-o antes de continuar.")

    bdir = os.path.join(root, BACKUP_DIR)
    filesdir = os.path.join(bdir, "files")
    os.makedirs(filesdir, exist_ok=True)

    # manifest do estado original (todos os paks)
    paks = os.path.join(root, PAKS_REL)
    lines = ["# Estado original da pasta de paks (nome<TAB>tamanho<TAB>sha1)",
             "# Gerado em " + datetime.datetime.now().isoformat()]
    try:
        for f in sorted(os.listdir(paks)):
            fp = os.path.join(paks, f)
            if os.path.isfile(fp):
                lines.append("%s\t%d\t%s" % (f, os.path.getsize(fp), sha1_file(fp)))
    except Exception as e:
        lines.append("# erro: %r" % (e,))
    with open(os.path.join(bdir, "manifest_original.txt"), "w", encoding="utf-8") as w:
        w.write("\n".join(lines))

    log("Fazendo backup em: %s" % bdir)
    n = 0
    for rel, full in files:
        dst = os.path.join(root, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.exists(dst):
            bak = os.path.join(filesdir, rel)
            os.makedirs(os.path.dirname(bak), exist_ok=True)
            shutil.copy2(dst, bak)
        shutil.copy2(full, dst)
        n += 1

    with open(os.path.join(bdir, "backup_info.txt"), "w", encoding="utf-8") as w:
        w.write("Backup criado em: %s\n" % datetime.datetime.now().isoformat())
        w.write("Pasta do jogo: %s\n" % root)
        w.write("Arquivos instalados: %d\n" % n)
        w.write("\nO mod NAO altera os arquivos originais do jogo: ele adiciona\n")
        w.write("um patch pak (_P.pak) e a pasta UE4SS/PTTranslator.\n")
        w.write("Para voltar ao ingles, use o Desinstalar.\n")

    write_restore_script(root, bdir)
    log("Instalados %d arquivos (traducao + UE4SS)." % n)
    log("Backup/restauracao em: %s" % bdir)
    return bdir


def uninstall(root, log=safe_log):
    if not is_game_root(root):
        raise RuntimeError("Pasta do jogo invalida")
    bdir = os.path.join(root, BACKUP_DIR)
    filesdir = os.path.join(bdir, "files")

    removed = 0
    for rel, full in payload_files():
        dst = os.path.join(root, rel)
        if os.path.exists(dst):
            try:
                os.remove(dst); removed += 1
            except Exception:
                pass
    # limpar pasta ue4ss vazia
    ue4ss = os.path.join(root, "Test_C", "Binaries", "Win64", "ue4ss")
    if os.path.isdir(ue4ss):
        try:
            shutil.rmtree(ue4ss)
        except Exception:
            pass

    restored = 0
    if os.path.isdir(filesdir):
        for dp, dn, fn in os.walk(filesdir):
            for f in fn:
                src = os.path.join(dp, f)
                rel = os.path.relpath(src, filesdir)
                dst = os.path.join(root, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                restored += 1

    log("Removidos %d arquivos." % removed)
    if restored:
        log("Restaurados %d arquivos originais." % restored)
    log("Idioma original restaurado.")


def write_restore_script(root, bdir):
    bat = os.path.join(bdir, "Desinstalar_PTBR.bat")
    lines = [
        "@echo off",
        "chcp 65001 >nul",
        "echo Removendo traducao PT-BR...",
        'del /f /q "%~dp0..\\Test_C\\Content\\Paks\\' + MOD_PAK + '"',
        'rmdir /s /q "%~dp0..\\Test_C\\Binaries\\Win64\\ue4ss" 2>nul',
        'del /f /q "%~dp0..\\Test_C\\Binaries\\Win64\\dwmapi.dll" 2>nul',
        "echo Pronto. Idioma original restaurado.",
        "pause",
    ]
    with open(bat, "w", encoding="cp850", errors="ignore") as w:
        w.write("\r\n".join(lines) + "\r\n")


# ----------------------------------------------------------------------------
# GUI
# ----------------------------------------------------------------------------
def run_gui():
    import tkinter as tk
    from tkinter import filedialog, messagebox

    BG = "#1b1f24"; FG = "#e6e6e6"; ACC = "#c0392b"
    root = tk.Tk()
    root.title("Incursion Red River - Traducao PT-BR")
    root.configure(bg=BG)
    root.geometry("640x360")
    root.resizable(False, False)

    tk.Label(root, text="INCURSION RED RIVER", bg=BG, fg=ACC, font=("Segoe UI", 18, "bold")).pack(pady=(16, 0))
    tk.Label(root, text="Traducao PT-BR (mantendo termos militares)", bg=BG, fg=FG, font=("Segoe UI", 10)).pack(pady=(0, 12))

    frm = tk.Frame(root, bg=BG); frm.pack(fill="x", padx=20)
    tk.Label(frm, text="Pasta do jogo:", bg=BG, fg=FG, font=("Segoe UI", 10)).pack(anchor="w")
    path_var = tk.StringVar()
    tk.Entry(frm, textvariable=path_var, font=("Segoe UI", 9)).pack(fill="x", pady=4)
    btns = tk.Frame(frm, bg=BG); btns.pack(fill="x")
    status = tk.Label(root, text="", bg=BG, fg="#9ad", font=("Segoe UI", 9), wraplength=600, justify="left")
    status.pack(fill="x", padx=20, pady=(10, 0))

    def set_status(msg):
        status.config(text=msg); root.update_idletasks()

    def detect():
        found = find_game_roots()
        if found:
            path_var.set(found[0])
            set_status("Jogo encontrado em:\n" + "\n".join(found[:5]))
        else:
            set_status("Nao encontrei automaticamente. Clique em Procurar e selecione a pasta que contem 'Test_C'.")

    def browse():
        p = filedialog.askdirectory(title="Selecione a pasta do jogo (a que contem Test_C)")
        if p:
            path_var.set(os.path.normpath(p))
            set_status("Pasta valida." if is_game_root(p) else "ATENCAO: essa pasta nao contem Test_C\\Content\\Paks.")

    def do_install():
        p = path_var.get().strip().strip('"')
        if not is_game_root(p):
            messagebox.showerror("Erro", "Pasta invalida. Selecione a pasta do jogo (que contem Test_C).")
            return
        try:
            install(p, log=set_status)
            messagebox.showinfo("Sucesso", "Traducao instalada!\n\nBackup em:\n" + os.path.join(p, BACKUP_DIR))
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def do_uninstall():
        p = path_var.get().strip().strip('"')
        if not is_game_root(p):
            messagebox.showerror("Erro", "Pasta invalida.")
            return
        try:
            uninstall(p, log=set_status)
            messagebox.showinfo("Pronto", "Idioma original restaurado.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    tk.Button(btns, text="Detectar", command=detect, width=14).pack(side="left", padx=(0, 6))
    tk.Button(btns, text="Procurar...", command=browse, width=14).pack(side="left")

    actions = tk.Frame(root, bg=BG); actions.pack(pady=16)
    tk.Button(actions, text="INSTALAR TRADUCAO", command=do_install, bg=ACC, fg="white",
              font=("Segoe UI", 11, "bold"), width=22, height=2).pack(side="left", padx=8)
    tk.Button(actions, text="DESINSTALAR / RESTAURAR", command=do_uninstall,
              font=("Segoe UI", 10), width=24, height=2).pack(side="left", padx=8)
    tk.Label(root, text="Feche o jogo antes de instalar. O mod nao altera os arquivos originais.",
             bg=BG, fg="#888", font=("Segoe UI", 8)).pack(side="bottom", pady=8)

    detect()
    root.mainloop()


def main():
    ap = argparse.ArgumentParser(description="Instalador PT-BR Incursion Red River")
    ap.add_argument("--install", metavar="PASTA", nargs="?", const="__AUTO__")
    ap.add_argument("--uninstall", metavar="PASTA", nargs="?", const="__AUTO__")
    ap.add_argument("--detect", action="store_true")
    args = ap.parse_args()

    def resolve(p):
        if p and p != "__AUTO__":
            return os.path.normpath(p.strip('"'))
        found = find_game_roots()
        return found[0] if found else None

    if args.detect:
        for f in find_game_roots():
            print("  " + f)
        return 0
    if args.install is not None:
        p = resolve(args.install)
        if not p:
            print("Nao encontrei a pasta do jogo. Use --install \"CAMINHO\".")
            return 1
        install(p); return 0
    if args.uninstall is not None:
        p = resolve(args.uninstall)
        if not p:
            print("Nao encontrei a pasta do jogo.")
            return 1
        uninstall(p); return 0
    run_gui(); return 0


if __name__ == "__main__":
    sys.exit(main())
