<#
.SYNOPSIS
    Downloads and extracts a portable Tesseract OCR bundle for the project.

.DESCRIPTION
    Fetches the Tesseract OCR engine Windows build from UB-Mannheim and
    extracts it into ``BACKEND/bin/tesseract/`` so the PdfToDocxOcrAdapter
    can find it without requiring a system-wide installation.

    Extraction uses 7-Zip if available; otherwise runs the installer
    silently to the target directory.

.PARAMETER Version
    Tesseract version to download (default: 5.3.3.20231005).

.PARAMETER TargetDir
    Output directory (default: ``<script-dir>/tesseract``).

.EXAMPLE
    .\download_tesseract.ps1
    .\download_tesseract.ps1 -Version 5.4.0 -TargetDir C:\tesseract
#>

param(
    [string]$Version    = "5.3.3.20231005",
    [string]$TargetDir  = (Join-Path $PSScriptRoot "tesseract")
)

$ErrorActionPreference = "Stop"
$Url = "https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-$Version.exe"
$Installer = Join-Path $env:TEMP "tesseract_setup_$Version.exe"

# ── Download ──────────────────────────────────────────────────────────
if (-not (Test-Path $Installer)) {
    Write-Host "⬇ Downloading Tesseract $Version ..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri $Url -OutFile $Installer -UseBasicParsing
} else {
    Write-Host "✔ Installer already cached at $Installer" -ForegroundColor Green
}

# ── Ensure target directory ──────────────────────────────────────────
New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null

# ── Extract ──────────────────────────────────────────────────────────
# Try 7-Zip first (handles NSIS installers natively)
$7z = Get-Command "7z" -ErrorAction SilentlyContinue
if (-not $7z) {
    $7z = Get-Command "C:\Program Files\7-Zip\7z.exe" -ErrorAction SilentlyContinue
}

if ($7z) {
    Write-Host "📦 Extracting with 7-Zip ..." -ForegroundColor Cyan
    & $7z.Source x $Installer -o"$TargetDir" -y *> $null
    if ($LASTEXITCODE -ne 0) {
        throw "7-Zip extraction failed (exit code $LASTEXITCODE)"
    }
} else {
    Write-Host "📦 7-Zip not found. Running installer silently ..." -ForegroundColor Yellow
    Write-Host "   The installer will show a progress window. This is expected." -ForegroundColor Yellow
    $proc = Start-Process -Wait -PassThru -FilePath $Installer -ArgumentList "/S /D=$TargetDir"
    if ($proc.ExitCode -ne 0) {
        throw "Installer exited with code $($proc.ExitCode)"
    }
}

# ── Verify ───────────────────────────────────────────────────────────
$tesseractExe = Join-Path $TargetDir "tesseract.exe"
if (-not (Test-Path $tesseractExe)) {
    throw "tesseract.exe not found after extraction at: $TargetDir"
}

Write-Host "✅ Tesseract $Version bundled at: $TargetDir" -ForegroundColor Green
Write-Host "   Try it: `"$tesseractExe`" --version" -ForegroundColor Gray
