#define AppVersion "1.10"

[Setup]
AppId={{41B77C55-166D-46E1-B933-E208EC834421}
AppName=Engineering Document Translator
AppVersion={#AppVersion}
AppPublisher=Engineering Document Translator contributors
AppPublisherURL=https://github.com/eizatabdullah12-stack/eizat96
DefaultDirName={localappdata}\Programs\EngineeringDocumentTranslator
DefaultGroupName=Engineering Document Translator
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
OutputDir=installer_output
OutputBaseFilename=EngineeringTranslator-{#AppVersion}-Setup
Compression=lzma2/ultra64
SolidCompression=yes
LZMANumBlockThreads=2
WizardStyle=modern
LicenseFile=LICENSE
UninstallDisplayIcon={app}\EngineeringPDFTranslator.exe
SetupLogging=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "dutch"; MessagesFile: "compiler:Languages\Dutch.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\EngineeringPDFTranslator\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Engineering Document Translator"; Filename: "{app}\EngineeringPDFTranslator.exe"
Name: "{autodesktop}\Engineering Document Translator"; Filename: "{app}\EngineeringPDFTranslator.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\EngineeringPDFTranslator.exe"; Description: "{cm:LaunchProgram,Engineering Document Translator}"; Flags: nowait postinstall skipifsilent
