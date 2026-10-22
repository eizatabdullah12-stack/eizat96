# Builder script, not the end-user launcher. Requires Windows x64 and Python 3.11.
$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
Set-Location $PSScriptRoot
py -3.11 -m venv .build-env
if ($LASTEXITCODE -ne 0) { throw 'Windows Python 3.11 is required on the build machine.' }
$buildPython = Join-Path $PSScriptRoot '.build-env\Scripts\python.exe'
& $buildPython -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency download failed.' }
& $buildPython fetch_models.py
if ($LASTEXITCODE -ne 0) { throw 'Language-model download failed.' }
& $buildPython -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { throw 'Document checks failed.' }
& $buildPython collect_notices.py
if ($LASTEXITCODE -ne 0) { throw 'Dependency notices could not be retained.' }
& $buildPython create_assets.py
if ($LASTEXITCODE -ne 0) { throw 'Logo generation failed.' }
& $buildPython -m PyInstaller --noconfirm --clean --onedir --windowed --name EngineeringPDFTranslator --icon 'assets/app.ico' --version-file 'assets/version_info.txt' --add-data 'src/models;models' --add-data 'src/engineering_terms.psv;.' --add-data 'src/conversation.psv;.' --add-data 'licenses;licenses' --collect-all ctranslate2 --collect-all sentencepiece src/app.py
if ($LASTEXITCODE -ne 0) { throw 'Windows executable build failed.' }
$bundlePath = Join-Path $PSScriptRoot 'dist\EngineeringPDFTranslator'
$resultPath = Join-Path $bundlePath 'windows-selftest.json'
$checkProcess = Start-Process -FilePath (Join-Path $bundlePath 'EngineeringPDFTranslator.exe') -ArgumentList @('--self-test', ('"' + $resultPath + '"')) -PassThru
if (-not $checkProcess.WaitForExit(300000)) { $checkProcess.Kill(); throw 'Compiled executable self-test timed out.' }
if ($checkProcess.ExitCode -ne 0 -or -not (Test-Path $resultPath)) { throw 'Compiled executable self-test failed.' }
$testResult = Get-Content -Raw $resultPath | ConvertFrom-Json
if (-not $testResult.passed) { throw 'Compiled executable checks did not pass.' }
Copy-Item PORTABLE_README.txt (Join-Path $bundlePath 'README.txt')
Copy-Item THIRD_PARTY.md (Join-Path $bundlePath 'THIRD_PARTY.txt')
Copy-Item LICENSE (Join-Path $bundlePath 'LICENSE.txt')
Copy-Item TERMINOLOGY.md (Join-Path $bundlePath 'TERMINOLOGY.txt')
& $buildPython export_glossary.py
if ($LASTEXITCODE -ne 0) { throw 'Engineering glossary export failed.' }
Copy-Item licenses (Join-Path $bundlePath 'licenses') -Recurse
Copy-Item dist\EngineeringGlossary.tsv $bundlePath
function Find-InstallerCompiler {
    $roots = @(${env:ProgramFiles(x86)}, $env:ProgramFiles)
    return Get-ChildItem -Path $roots -Directory -Filter 'Inno Setup*' -ErrorAction SilentlyContinue |
        Sort-Object FullName -Descending |
        ForEach-Object { Join-Path $_.FullName 'ISCC.exe' } |
        Where-Object { Test-Path $_ } | Select-Object -First 1
}
$compiler = Find-InstallerCompiler
if (-not $compiler) {
    choco install innosetup --yes --no-progress
    if ($LASTEXITCODE -ne 0) { throw 'Installer compiler download failed.' }
    $compiler = Find-InstallerCompiler
    if (-not $compiler) { throw 'Installer compiler not found.' }
}
& $compiler installer.iss
if ($LASTEXITCODE -ne 0) { throw 'Windows installer build failed.' }
$setup = Join-Path $PSScriptRoot 'installer_output\EngineeringTranslator-1.11-Setup.exe'
$installPath = Join-Path $env:TEMP 'Translator setup verification'
$installation = Start-Process -FilePath $setup -ArgumentList @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART','/SP-',('/DIR="' + $installPath + '"')) -Wait -PassThru
if ($installation.ExitCode -ne 0) { throw 'Windows installer smoke test failed.' }
$installedFiles = Get-ChildItem -Path $bundlePath -File -Recurse
foreach ($file in $installedFiles) {
    $relative = $file.FullName.Substring($bundlePath.Length + 1)
    $installed = Join-Path $installPath $relative
    if (-not (Test-Path $installed) -or (Get-FileHash $file.FullName).Hash -ne (Get-FileHash $installed).Hash) {
        throw ('Installer content verification failed: ' + $relative)
    }
}
Write-Host 'Windows installer installed successfully; every installed application file matches the verified bundle.'
Write-Host ('Installer bytes: ' + (Get-Item $setup).Length)
Get-FileHash $setup -Algorithm SHA256
Write-Host 'Executable built and compiled-app checks passed.'
