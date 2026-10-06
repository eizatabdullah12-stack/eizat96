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
if ($LASTEXITCODE -ne 0) { throw 'PDF checks failed.' }
& $buildPython collect_notices.py
if ($LASTEXITCODE -ne 0) { throw 'Dependency notices could not be retained.' }
& $buildPython -m PyInstaller --noconfirm --clean --onefile --windowed --name EngineeringPDFTranslator --add-data 'src/models;models' --add-data 'licenses;licenses' --collect-all ctranslate2 --collect-all sentencepiece src/app.py
if ($LASTEXITCODE -ne 0) { throw 'Windows executable build failed.' }
$resultPath = Join-Path $PSScriptRoot 'dist\windows-selftest.json'
$checkProcess = Start-Process -FilePath (Join-Path $PSScriptRoot 'dist\EngineeringPDFTranslator.exe') -ArgumentList @('--self-test', ('"' + $resultPath + '"')) -PassThru
if (-not $checkProcess.WaitForExit(180000)) { $checkProcess.Kill(); throw 'Compiled executable self-test timed out.' }
if ($checkProcess.ExitCode -ne 0 -or -not (Test-Path $resultPath)) { throw 'Compiled executable self-test failed.' }
$testResult = Get-Content -Raw $resultPath | ConvertFrom-Json
if (-not $testResult.passed) { throw 'Compiled executable checks did not pass.' }
Copy-Item PORTABLE_README.txt dist\README.txt
Copy-Item THIRD_PARTY.md dist\THIRD_PARTY.txt
Copy-Item LICENSE dist\LICENSE.txt
Copy-Item TERMINOLOGY.md dist\TERMINOLOGY.txt
& $buildPython export_glossary.py
if ($LASTEXITCODE -ne 0) { throw 'Engineering glossary export failed.' }
Copy-Item licenses dist\licenses -Recurse
Compress-Archive -Path dist\* -DestinationPath EngineeringPDFTranslator_Portable_Windows.zip -Force
Write-Host 'Executable built and compiled-app checks passed.'
