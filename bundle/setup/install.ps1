# gekko-toolchain: sets DEVKITPRO and DEVKITPPC (for you, not the whole machine) to this folder,
# and points its MSYS2 at it. Run by Install.bat; -Uninstall (Uninstall.bat) undoes it.
param([switch]$Uninstall)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path.TrimEnd('\')

function MsysPath([string]$p) { '/' + $p.Substring(0, 1).ToLower() + ($p.Substring(2) -replace '\\', '/') }
function Get-UserVar([string]$n) { [Environment]::GetEnvironmentVariable($n, 'User') }
function Set-UserVar([string]$n, $v) { [Environment]::SetEnvironmentVariable($n, $v, 'User') }

if ($Uninstall) {
    $mine = MsysPath $root
    if ((Get-UserVar 'DEVKITPRO') -ne $mine) {
        Write-Host "DEVKITPRO isn't this folder ($mine): nothing to undo."
        exit 0
    }
    Set-UserVar 'DEVKITPRO' (Get-UserVar 'GEKKO_PREVIOUS_DEVKITPRO')
    Set-UserVar 'DEVKITPPC' (Get-UserVar 'GEKKO_PREVIOUS_DEVKITPPC')
    Set-UserVar 'GEKKO_PREVIOUS_DEVKITPRO' $null
    Set-UserVar 'GEKKO_PREVIOUS_DEVKITPPC' $null
    $back = Get-UserVar 'DEVKITPRO'
    if ($back) { Write-Host "DEVKITPRO is $back again." } else { Write-Host 'DEVKITPRO and DEVKITPPC removed.' }
    Write-Host 'Programs already open keep the old values until they are restarted.'
    exit 0
}

if ($root -match '\s') {
    Write-Host "This folder's path has a space in it: $root"
    Write-Host "devkitPro's makefiles don't work from such a path. Move the gekko-toolchain folder"
    Write-Host 'somewhere without spaces (C:\gekko-toolchain, say) and run Install.bat again.'
    exit 1
}
if (-not (Test-Path (Join-Path $root 'devkitPPC\bin\powerpc-eabi-gcc.exe'))) {
    Write-Host "No devkitPPC\bin\powerpc-eabi-gcc.exe in $root : unzip the whole bundle and run Install.bat from it."
    exit 1
}

$dkp = MsysPath $root
$current = Get-UserVar 'DEVKITPRO'
if (-not $current) { $current = [Environment]::GetEnvironmentVariable('DEVKITPRO', 'Machine') }
if ($current -and $current -ne $dkp) {
    Write-Host "DEVKITPRO is set already: $current (an official devkitPro, perhaps)."
    $answer = Read-Host 'Point it at gekko-toolchain instead? Uninstall.bat puts it back. [y/N]'
    if ($answer -notmatch '^[Yy]') { Write-Host 'Nothing changed.'; exit 0 }
    if (-not (Get-UserVar 'GEKKO_PREVIOUS_DEVKITPRO')) {
        Set-UserVar 'GEKKO_PREVIOUS_DEVKITPRO' (Get-UserVar 'DEVKITPRO')
        Set-UserVar 'GEKKO_PREVIOUS_DEVKITPPC' (Get-UserVar 'DEVKITPPC')
    }
}

# MSYS2's mount table: this folder as /opt/devkitpro, as devkitPro's own install has it
$fstab = "none / cygdrive binary,posix=0,noacl,user 0 0`n$root`t/opt/devkitpro`n"
[IO.File]::WriteAllText((Join-Path $root 'msys2\etc\fstab'), $fstab)
New-Item -ItemType Directory -Force -Path (Join-Path $root 'msys2\tmp') | Out-Null

Set-UserVar 'DEVKITPRO' $dkp
Set-UserVar 'DEVKITPPC' "$dkp/devkitPPC"
Write-Host "gekko-toolchain installed: DEVKITPRO=$dkp, DEVKITPPC=$dkp/devkitPPC"
Write-Host 'Programs already open (a terminal, Visual Studio, a builder) see it once restarted.'
