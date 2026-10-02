# gekko-toolchain

An unofficial, ready-to-use snapshot of the GameCube toolchain for Windows, in one zip: the
compiler, libogc, libfat, the GameCube tools, and the `make` and shell its makefiles run with.
Unzip it, run `Install.bat`, and GameCube projects build as they would with devkitPro's own
install.

> **Unofficial.** gekko-toolchain is not made or supported by devkitPro. It's their toolchain,
> as their installer puts it on a PC, taken unchanged and packed into one zip. For the official
> one, go to [devkitpro.org](https://devkitpro.org/wiki/Getting_Started). Please don't ask
> devkitPro for help with this bundle. Report problems with it on this repo's
> [Issues page](https://github.com/myuu-151/gekko-toolchain/issues).

## Installing

1. Download `gekko-toolchain-r49.2.zip` from [Releases](https://github.com/myuu-151/gekko-toolchain/releases).
2. Unzip it to a folder **without spaces** in its path, such as `C:\gekko-toolchain`.
3. Run **`Install.bat`** in it. It sets `DEVKITPRO` and `DEVKITPPC` (for your account, not the
   whole machine) to that folder. If devkitPro's own install is there already, it asks first.
4. Restart anything already open (a terminal, Visual Studio, a builder window).

**`Uninstall.bat`** puts `DEVKITPRO` and `DEVKITPPC` back to what they were (or removes them);
then delete the folder.

The builders (`Build Octave.bat`, `Build CCGC.bat`, `Build Sonic Pipe Dream.bat`) find it through
`DEVKITPRO`. From a terminal, put its `devkitPPC\bin`, `tools\bin` and `msys2\usr\bin` on `PATH`
and run `make` as usual.

## What's in it

About 430 MB unzipped, laid out as devkitPro's install is (`devkitPPC/`, `libogc/`, `tools/`,
`msys2/`), so makefiles and tools find everything where they expect it. Every package and version
is in `VERSIONS.txt`.

| Part | Version | Source |
|---|---|---|
| devkitPPC: GCC, binutils, newlib | r49.2: GCC 15.2.0, binutils 2.45.1, newlib 4.6.0.20260123 | Built by [buildscripts `devkitPPC_r49.2`](https://github.com/myuu-151/buildscripts/tree/devkitPPC_r49.2) from the GNU and Sourceware release archives it names, with its patches. devkitPro's branches: [gcc](https://github.com/myuu-151/gcc), [newlib](https://github.com/myuu-151/newlib) |
| devkitPPC's rules (`gamecube_rules`) | 1.2.1 | [devkitppc-rules `v1.2.1`](https://github.com/myuu-151/devkitppc-rules/tree/v1.2.1) |
| devkitPPC's startup files | 2.0.0 | [devkitPro/devkitppc-crtls](https://github.com/devkitPro/devkitppc-crtls) |
| libogc (with asnd, bba, ...) | 3.0.4 | [libogc](https://github.com/myuu-151/libogc) ([upstream `v3.0.4`](https://github.com/devkitPro/libogc/tree/v3.0.4)) |
| libfat | 2.1.0 | [libfat](https://github.com/myuu-151/libfat) |
| gamecube-tools (`elf2dol`, `gxtexconv`, `gcdsptool`) | 1.0.7 | [gamecube-tools](https://github.com/myuu-151/gamecube-tools) ([upstream `v1.0.7`](https://github.com/devkitPro/gamecube-tools/tree/v1.0.7)) |
| general-tools (`bin2s`, `raw2c`, ...) | 1.4.4 | [devkitPro/general-tools `v1.4.4`](https://github.com/devkitPro/general-tools/tree/v1.4.4) |
| MSYS2: `make`, `bash`, coreutils, `sed`, `grep`, `gawk`, `cygpath` ... | make 4.4.1, bash 5.3, runtime 3.6.6 | [msys2/MSYS2-packages](https://github.com/msys2/MSYS2-packages) |

The `myuu-151` links are forks, kept so the sources stay available. Each part keeps its own
licence, in `licenses/` (and `libogc/LICENSE`): GCC and binutils are GPL-3, with GCC's runtime
library exception for what's linked into a program; newlib, libogc and libfat have their own
permissive licences; MSYS2's packages are under theirs.

## Making the bundle

`tools/make_bundle.py` makes it from an installed devkitPro (with `gamecube-dev`): it reads
devkitPro's own package records for the files each GameCube package installed, takes those and
the MSYS2 packages the makefiles need (with what they need), and zips them with `Install.bat`,
`Uninstall.bat` and the licences.

    python tools/make_bundle.py [C:\devkitPro]

*devkitPro, devkitPPC and libogc are devkitPro's. GameCube is a trademark of Nintendo; this
project isn't affiliated with Nintendo.*
