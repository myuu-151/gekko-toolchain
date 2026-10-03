"""Makes the gekko-toolchain bundle from an installed devkitPro (Windows): only what GameCube
development needs, by devkitPro's own package records (pacman's local database: the files each
package installed, and what each needs).

    python tools/make_bundle.py [devkitPro folder, default C:\\devkitPro] [--out folder]

The bundle is laid out as devkitPro is, so the same makefiles and tools work from it:

    gekko-toolchain/
      devkitPPC/   the compiler, linker, C library and gamecube_rules
      libogc/      libogc, asnd, bba ... and libfat
      tools/bin/   elf2dol, gxtexconv, gcdsptool, bin2s ...
      msys2/       make, the shell and the commands the makefiles use, and cygpath
      licenses/    the licences of what's in it
      Install.bat, Uninstall.bat, README.md, VERSIONS.txt

and zipped as gekko-toolchain-<devkitPPC version>-<revision>.zip.
"""
import os
import re
import shutil
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
# The bundle's own revision of a devkitPPC version: 2 added GDB. The zip is named
# gekko-toolchain-<devkitPPC version>-<revision>.zip from revision 2 on.
REVISION = 2

# devkitPro's packages for GameCube development ...
GAMECUBE = ['devkitPPC', 'devkitppc-binutils', 'devkitppc-gcc', 'devkitppc-newlib', 'devkitppc-rules',
            'devkitppc-crtls', 'libogc', 'libfat-ogc', 'gamecube-tools', 'general-tools',
            'devkitPPC-gdb']          # GDB, for debugging on a GameCube through a USB Gecko
# ... and MSYS2's the makefiles run with (what these need comes with them)
MSYS = ['msys2-runtime', 'make', 'bash', 'coreutils', 'sed', 'grep', 'gawk', 'findutils', 'which', 'diffutils']


def packages(db):
    """Every installed package: name -> (version, depends, files)."""
    out = {}
    for entry in db.iterdir():
        desc = entry / 'desc'
        if not desc.exists():
            continue
        fields, key = {}, None
        for line in desc.read_text(encoding='utf-8', errors='replace').splitlines():
            if line.startswith('%') and line.endswith('%'):
                key = line.strip('%')
                fields[key] = []
            elif line and key:
                fields[key].append(line)
        files = []
        if (entry / 'files').exists():
            in_files = False
            for line in (entry / 'files').read_text(encoding='utf-8', errors='replace').splitlines():
                if line == '%FILES%':
                    in_files = True
                elif line.startswith('%'):
                    in_files = False
                elif in_files and line and not line.endswith('/'):
                    files.append(line)
        name = fields['NAME'][0]
        out[name] = (fields['VERSION'][0], [re.split(r'[<>=]', d)[0] for d in fields.get('DEPENDS', [])], files)
    return out


def provides(db):
    """Virtual names (such as "sh") -> the package that provides them."""
    out = {}
    for entry in db.iterdir():
        desc = entry / 'desc'
        if not desc.exists():
            continue
        text = desc.read_text(encoding='utf-8', errors='replace')
        name = re.search(r'%NAME%\n(.+)', text).group(1)
        block = re.search(r'%PROVIDES%\n((?:.+\n)+)', text)
        if block:
            for p in block.group(1).split():
                out[re.split(r'[<>=]', p)[0]] = name
    return out


def with_dependencies(wanted, installed, virtual):
    seen, todo = [], list(wanted)
    while todo:
        name = todo.pop(0)
        name = name if name in installed else virtual.get(name, name)
        if name in seen or name not in installed:
            continue
        seen.append(name)
        todo.extend(installed[name][1])
    return seen


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    dkp = Path(args[0] if args else r'C:\devkitPro')
    out = Path(sys.argv[sys.argv.index('--out') + 1]) if '--out' in sys.argv else HERE / 'build'
    db = dkp / 'msys2' / 'var' / 'lib' / 'pacman' / 'local'
    installed, virtual = packages(db), provides(db)
    missing = [p for p in GAMECUBE + MSYS if p not in installed]
    if missing:
        sys.exit(f'not installed in {dkp}: {", ".join(missing)} (pacman -S gamecube-dev)')
    names = with_dependencies(GAMECUBE + MSYS, installed, virtual)

    root = out / 'gekko-toolchain'
    if root.exists():
        def writable(func, path, _):           # (some of MSYS2's files are read-only)
            os.chmod(path, 0o666)
            func(path)
        shutil.rmtree(root, onexc=writable)
    copied = 0
    for name in names:
        for f in installed[name][2]:
            # devkitPro's packages install under /opt/devkitpro (C:\devkitPro); MSYS2's under msys2/
            rel = f[len('opt/devkitpro/'):] if f.startswith('opt/devkitpro/') else 'msys2/' + f
            src, dst = dkp / rel, root / rel
            if src.is_file():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                copied += 1
    # what MSYS2 needs to start that no package lists: its folders, and the mount table the
    # installer points at this folder
    for folder in ('msys2/tmp', 'msys2/etc'):
        (root / folder).mkdir(parents=True, exist_ok=True)
    (root / 'msys2' / 'etc' / 'fstab').write_text(
        'none / cygdrive binary,posix=0,noacl,user 0 0\n'
        '# Install.bat writes this folder here, as /opt/devkitpro (devkitPro\'s makefiles may use it)\n', newline='\n')
    for f in ('passwd', 'group', 'nsswitch.conf'):
        if (dkp / 'msys2' / 'etc' / f).exists():
            shutil.copy2(dkp / 'msys2' / 'etc' / f, root / 'msys2' / 'etc' / f)
    if (dkp / 'licenses').is_dir():
        for d in (dkp / 'licenses').iterdir():
            if d.name in names or d.name.lower() in (n.lower() for n in names):
                shutil.copytree(d, root / 'licenses' / d.name, dirs_exist_ok=True)
    shutil.copytree(HERE / 'bundle', root, dirs_exist_ok=True)      # Install.bat, Uninstall.bat, setup/
    shutil.copy2(HERE / 'README.md', root / 'README.md')
    versions = '\n'.join(f'{n} {installed[n][0]}' for n in sorted(names, key=str.lower))
    (root / 'VERSIONS.txt').write_text(versions + '\n', newline='\n')

    ppc = installed['devkitPPC'][0].split('-')[0]
    archive = out / (f'gekko-toolchain-{ppc}.zip' if REVISION < 2 else f'gekko-toolchain-{ppc}-{REVISION}.zip')
    files = sorted(p for p in root.rglob('*') if p.is_file())
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in files:
            z.write(p, p.relative_to(out).as_posix())
        for d in ('gekko-toolchain/msys2/tmp/',):
            z.writestr(d, '')
    size = sum(p.stat().st_size for p in files)
    print(f'{len(names)} packages, {copied} files, {size / 1048576:.0f} MB -> {archive} '
          f'({archive.stat().st_size / 1048576:.0f} MB)')
    print(versions)


if __name__ == '__main__':
    main()
