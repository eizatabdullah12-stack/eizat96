"""Human-authored interface strings. English remains the startup default."""
from string import Formatter

LANGUAGE_NAMES = {'en':'English', 'fr':'Français', 'nl':'Nederlands', 'de':'Deutsch'}

_ROWS = r'''title|Engineering Document Translator|Traducteur de documents techniques|Vertaler voor technische documenten|Übersetzer für technische Dokumente
creator|Created by Eizat|Créé par Eizat|Gemaakt door Eizat|Erstellt von Eizat
text_style|Text style|Style du texte|Tekststijl|Textstil
conversation_mode|Conversation / natural sentences|Conversation / phrases naturelles|Gesprek / natuurlijke zinnen|Gespräch / natürliche Sätze
engineering_mode|Engineering terminology|Terminologie technique|Technische terminologie|Technische Fachbegriffe
conversation_hint|Conversation keeps sentence context and includes slang and swear words. Engineering prioritizes drawing terms. Grammar suggestions are limited.|Le mode conversation conserve le contexte et inclut l'argot et les gros mots. Le mode technique privilégie les termes des plans. Corrections grammaticales limitées.|Gespreksmodus behoudt zinscontext en bevat straattaal en scheldwoorden. Technische modus geeft voorrang aan tekentermen. Beperkte grammaticacorrectie.|Der Gesprächsmodus erhält den Satzkontext und enthält Umgangssprache und Schimpfwörter. Der Technikmodus bevorzugt Zeichnungsbegriffe. Begrenzte Grammatikkorrektur.
subtitle|English / French / Dutch / German · Offline|Anglais / Français / Néerlandais / Allemand · Hors ligne|Engels / Frans / Nederlands / Duits · Offline|Englisch / Französisch / Niederländisch / Deutsch · Offline
display_language|App language|Langue de l’application|Taal van de app|Sprache der Anwendung
source_language|Source language|Langue du document source|Brontaal|Ausgangssprache
output_language|Output language|Langue de traduction|Doeltaal|Zielsprache
auto|Auto / mixed languages|Auto / plusieurs langues|Automatisch / meerdere talen|Automatisch / mehrere Sprachen
document|PDF, Word or PowerPoint document|Document PDF, Word ou PowerPoint|PDF-, Word- of PowerPoint-document|PDF-, Word- oder PowerPoint-Dokument
choose_file|Choose file…|Choisir un fichier…|Bestand kiezen…|Datei auswählen…
replace_mode|PDF: replace text where it fits; add notes for other labels|PDF : remplacer le texte si possible ; ajouter des notes pour les autres libellés|PDF: tekst vervangen waar die past; anders vertaalnotities toevoegen|PDF: Text ersetzen, wenn er passt; sonst Übersetzungsnotizen hinzufügen
notes_mode|PDF: keep the original drawing and add translation notes|PDF : conserver le dessin original et ajouter des notes de traduction|PDF: originele tekening behouden en vertaalnotities toevoegen|PDF: Originalzeichnung beibehalten und Übersetzungsnotizen hinzufügen
help|Word/PowerPoint: save an editable translated copy. Originals are retained.\nEngineering glossary enabled. Text in pictures needs OCR.|Word/PowerPoint : enregistrer une copie traduite modifiable. Les originaux sont conservés.\nGlossaire technique activé. Le texte dans les images nécessite une reconnaissance OCR.|Word/PowerPoint: een bewerkbare vertaalde kopie opslaan. Originelen blijven behouden.\nTechnische woordenlijst actief. Tekst in afbeeldingen vereist OCR.|Word/PowerPoint: bearbeitbare übersetzte Kopie speichern. Originale bleiben erhalten.\nTechnisches Glossar aktiv. Text in Bildern erfordert OCR.
begin|Choose a PDF, .docx or .pptx file to begin.|Choisissez un fichier PDF, .docx ou .pptx pour commencer.|Kies een PDF-, .docx- of .pptx-bestand om te beginnen.|Wählen Sie eine PDF-, .docx- oder .pptx-Datei aus.
office_status|Office file: save an editable copy in the selected output language.|Fichier Office : enregistrer une copie modifiable dans la langue choisie.|Office-bestand: een bewerkbare kopie in de gekozen doeltaal opslaan.|Office-Datei: bearbeitbare Kopie in der gewählten Zielsprache speichern.
translate_save|Translate and save…|Traduire et enregistrer…|Vertalen en opslaan…|Übersetzen und speichern…
cancel|Cancel|Annuler|Annuleren|Abbrechen
glossary|Browse terminology…|Consulter le glossaire…|Woordenlijst bekijken…|Glossar anzeigen…
open_verified|Open verified file|Ouvrir le fichier vérifié|Gecontroleerd bestand openen|Geprüfte Datei öffnen
glossary_title|Engineering and architectural terminology|Terminologie technique et architecturale|Bouwkundige en technische terminologie|Technische und architektonische Begriffe
search|Search term or category:|Rechercher un terme ou une catégorie :|Zoek term of categorie:|Begriff oder Kategorie suchen:
source_term|Source term|Terme source|Bronterm|Ausgangsbegriff
english_meaning|English reference term|Terme de référence anglais|Engelse referentieterm|Englischer Referenzbegriff
category|Category|Catégorie|Categorie|Kategorie
select_term|Select a term to view its context note.|Sélectionnez un terme pour voir sa note de contexte.|Selecteer een term om de contextnotitie te bekijken.|Wählen Sie einen Begriff aus, um den Kontexthinweis anzuzeigen.
term_default|Check project-specific usage against the drawing legend.|Vérifiez l’usage propre au projet dans la légende du plan.|Controleer het projectspecifieke gebruik aan de hand van de tekenlegenda.|Prüfen Sie die projektspezifische Verwendung anhand der Zeichnungslegende.
term_count|{shown} shown / {total} entries. Reference glossary: source → English.|{shown} affichés / {total} entrées. Glossaire de référence : source → anglais.|{shown} getoond / {total} termen. Referentiewoordenlijst: bron → Engels.|{shown} angezeigt / {total} Einträge. Referenzglossar: Ausgangssprache → Englisch.
supported_documents|Supported documents|Documents pris en charge|Ondersteunde documenten|Unterstützte Dokumente
save_copy|Save translated copy|Enregistrer la copie traduite|Vertaalde kopie opslaan|Übersetzte Kopie speichern
choose_document|Choose a document|Choisir un document|Document kiezen|Dokument auswählen
invalid_document|Select an existing PDF, Word (.docx) or PowerPoint (.pptx) file. Save older .doc/.ppt files in the newer format first.|Sélectionnez un fichier PDF, Word (.docx) ou PowerPoint (.pptx) existant. Enregistrez d’abord les anciens fichiers .doc/.ppt au nouveau format.|Selecteer een bestaand PDF-, Word- (.docx) of PowerPoint-bestand (.pptx). Sla oudere .doc/.ppt-bestanden eerst op in het nieuwe formaat.|Wählen Sie eine vorhandene PDF-, Word- (.docx) oder PowerPoint-Datei (.pptx). Speichern Sie ältere .doc/.ppt-Dateien zuerst im neuen Format.
keep_original|Keep the original|Conserver l’original|Origineel behouden|Original beibehalten
different_name|Choose a different filename for the translated copy.|Choisissez un autre nom pour la copie traduite.|Kies een andere bestandsnaam voor de vertaalde kopie.|Wählen Sie einen anderen Dateinamen für die übersetzte Kopie.
keep_format|Keep the file format|Conserver le format|Bestandsformaat behouden|Dateiformat beibehalten
same_extension|Save the translated copy with the {extension} file extension.|Enregistrez la copie traduite avec l’extension {extension}.|Sla de vertaalde kopie op met de extensie {extension}.|Speichern Sie die übersetzte Kopie mit der Dateiendung {extension}.
loading|Loading offline translation models…|Chargement des modèles de traduction hors ligne…|Offline vertaalmodellen laden…|Offline-Übersetzungsmodelle werden geladen…
page_progress|Translated page {current} of {total}…|Page {current} sur {total} traduite…|Pagina {current} van {total} vertaald…|Seite {current} von {total} übersetzt…
part_progress|Translated document part {current} of {total}…|Partie {current} sur {total} traduite…|Documentonderdeel {current} van {total} vertaald…|Dokumentteil {current} von {total} übersetzt…
stopped|Translation stopped.|Traduction arrêtée.|Vertaling gestopt.|Übersetzung angehalten.
stopped_title|Translation stopped|Traduction arrêtée|Vertaling gestopt|Übersetzung angehalten
verified|Verified saved file: {name}|Fichier enregistré vérifié : {name}|Gecontroleerd opgeslagen bestand: {name}|Geprüfte gespeicherte Datei: {name}
saved_title|Translated copy saved|Copie traduite enregistrée|Vertaalde kopie opgeslagen|Übersetzte Kopie gespeichert
pdf_result|Saved PDF reopened and checked.\nReplacements: {replaced}; translation notes: {notes}.|PDF enregistré, rouvert et vérifié.\nRemplacements : {replaced} ; notes de traduction : {notes}.|Opgeslagen PDF opnieuw geopend en gecontroleerd.\nVervangingen: {replaced}; vertaalnotities: {notes}.|Gespeicherte PDF erneut geöffnet und geprüft.\nErsetzungen: {replaced}; Übersetzungsnotizen: {notes}.
office_result|Saved Office file reopened and checked.\nTranslated text groups: {groups}; updated parts: {parts}.|Fichier Office enregistré, rouvert et vérifié.\nGroupes de texte traduits : {groups} ; parties modifiées : {parts}.|Opgeslagen Office-bestand opnieuw geopend en gecontroleerd.\nVertaalde tekstgroepen: {groups}; gewijzigde onderdelen: {parts}.|Gespeicherte Office-Datei erneut geöffnet und geprüft.\nÜbersetzte Textgruppen: {groups}; geänderte Teile: {parts}.
office_warning|Review text fit and mixed formatting in Office. Text in pictures, fields, equations and embedded objects is retained.|Vérifiez la mise en page et la mise en forme dans Office. Le texte des images, champs, équations et objets incorporés est conservé.|Controleer tekstpassing en gemengde opmaak in Office. Tekst in afbeeldingen, velden, formules en ingesloten objecten blijft behouden.|Prüfen Sie Textpassung und gemischte Formatierung in Office. Text in Bildern, Feldern, Formeln und eingebetteten Objekten bleibt erhalten.
result_details|Output language: {language}.\nUnchanged groups: {unchanged}.\nGlossary matches: {glossary}. Context reviews: {reviews}.\n\n{path}\n\nA .translations.txt file records the results.|Langue de traduction : {language}.\nGroupes inchangés : {unchanged}.\nCorrespondances du glossaire : {glossary}. Contextes à vérifier : {reviews}.\n\n{path}\n\nUn fichier .translations.txt contient les résultats.|Doeltaal: {language}.\nOngewijzigde groepen: {unchanged}.\nWoordenlijsttreffers: {glossary}. Contextcontroles: {reviews}.\n\n{path}\n\nDe resultaten staan in een .translations.txt-bestand.|Zielsprache: {language}.\nUnveränderte Gruppen: {unchanged}.\nGlossartreffer: {glossary}. Kontextprüfungen: {reviews}.\n\n{path}\n\nEine .translations.txt-Datei enthält die Ergebnisse.
language_reviews|Segments requiring language review: {count}.|Segments nécessitant une vérification de langue : {count}.|Tekstsegmenten waarvoor taalcontrole nodig is: {count}.|Textabschnitte mit erforderlicher Sprachprüfung: {count}.
no_changes_title|No text changed|Aucun texte modifié|Geen tekst gewijzigd|Kein Text geändert
no_changes|No text changed. Check the language settings and translation report.|Aucun texte modifié. Vérifiez les langues choisies et le rapport de traduction.|Geen tekst gewijzigd. Controleer de taalinstellingen en het vertaalrapport.|Kein Text geändert. Prüfen Sie die Spracheinstellungen und den Übersetzungsbericht.
file_changed_title|File changed|Fichier modifié|Bestand gewijzigd|Datei geändert
file_changed|This file changed after verification. Translate again to verify a new copy.|Ce fichier a changé après vérification. Relancez la traduction pour vérifier une nouvelle copie.|Dit bestand is na de controle gewijzigd. Vertaal opnieuw om een nieuwe kopie te controleren.|Diese Datei wurde nach der Prüfung geändert. Übersetzen Sie erneut, um eine neue Kopie zu prüfen.
open_failed|Cannot open file|Impossible d’ouvrir le fichier|Bestand kan niet worden geopend|Datei kann nicht geöffnet werden
close_title|Translation in progress|Traduction en cours|Vertaling bezig|Übersetzung läuft
close_question|Cancel translation and close?|Annuler la traduction et fermer ?|Vertaling annuleren en sluiten?|Übersetzung abbrechen und schließen?
error_cancelled|Translation cancelled; no new output was saved.|Traduction annulée ; aucune nouvelle sortie n’a été enregistrée.|Vertaling geannuleerd; er is geen nieuwe uitvoer opgeslagen.|Übersetzung abgebrochen; keine neue Ausgabe gespeichert.
error_password|Save an unlocked copy of this document first.|Enregistrez d’abord une copie non protégée du document.|Sla eerst een onbeveiligde kopie van dit document op.|Speichern Sie zuerst eine ungeschützte Kopie dieses Dokuments.
error_no_text|No translatable editable text was found. Text in pictures or scanned pages needs OCR.|Aucun texte modifiable à traduire trouvé. Les images et pages numérisées nécessitent une reconnaissance OCR.|Geen vertaalbare bewerkbare tekst gevonden. Afbeeldingen en gescande pagina’s vereisen OCR.|Kein übersetzbarer bearbeitbarer Text gefunden. Bilder und gescannte Seiten erfordern OCR.
error_model|The bundled translation models are incomplete. Download a fresh copy of the app.|Les modèles intégrés sont incomplets. Téléchargez une nouvelle copie de l’application.|De meegeleverde vertaalmodellen zijn onvolledig. Download een nieuwe kopie van de app.|Die mitgelieferten Übersetzungsmodelle sind unvollständig. Laden Sie die Anwendung erneut herunter.
error_verification|The saved file did not pass verification. The previous output was retained.|Le fichier enregistré n’a pas passé la vérification. La sortie précédente a été conservée.|Het opgeslagen bestand doorstond de controle niet. De vorige uitvoer is behouden.|Die gespeicherte Datei hat die Prüfung nicht bestanden. Die vorherige Ausgabe wurde beibehalten.
error_generic|Translation could not be completed. Details: {details}|La traduction n’a pas pu être terminée. Détails : {details}|De vertaling kon niet worden voltooid. Details: {details}|Die Übersetzung konnte nicht abgeschlossen werden. Details: {details}
scanned_warning|Pages without selectable text: {pages}. These pages were not translated.|Pages sans texte sélectionnable : {pages}. Ces pages n’ont pas été traduites.|Pagina’s zonder selecteerbare tekst: {pages}. Deze pagina’s zijn niet vertaald.|Seiten ohne auswählbaren Text: {pages}. Diese Seiten wurden nicht übersetzt.
context_english|Context note in the reference glossary: {note}|Note de contexte du glossaire de référence : {note}|Contextnotitie uit de referentiewoordenlijst: {note}|Kontexthinweis aus dem Referenzglossar: {note}'''

_ROWS += r'''
text_tab|Text translator|Traduction de texte|Tekstvertaler|Textübersetzer
documents_tab|Documents|Documents|Documenten|Dokumente
text_hint|Type or paste text. Translation starts when you pause. Choose an output language above. Everything stays offline.|Saisissez ou collez du texte. La traduction démarre après une pause. Choisissez la langue de traduction ci-dessus. Tout reste hors ligne.|Typ of plak tekst. Het vertalen begint zodra u even stopt. Kies hierboven de doeltaal. Alles werkt offline.|Text eingeben oder einfügen. Die Übersetzung beginnt nach einer kurzen Pause. Wählen Sie oben die Zielsprache. Alles funktioniert offline.
text_input|Type or paste here|Saisissez ou collez ici|Typ of plak hier|Hier eingeben oder einfügen
text_output|Translation|Traduction|Vertaling|Übersetzung
text_auto|Translate automatically|Traduire automatiquement|Automatisch vertalen|Automatisch übersetzen
text_translate|Translate · Ctrl+Enter|Traduire · Ctrl+Entrée|Vertalen · Ctrl+Enter|Übersetzen · Strg+Eingabe
text_paste|Paste|Coller|Plakken|Einfügen
text_clear|Clear|Effacer|Wissen|Leeren
text_copy|Copy translation|Copier la traduction|Vertaling kopiëren|Übersetzung kopieren
text_ready|Ready. Enter text to translate.|Prêt. Saisissez le texte à traduire.|Gereed. Voer tekst in om te vertalen.|Bereit. Geben Sie den zu übersetzenden Text ein.
text_waiting|Waiting for you to finish typing…|En attente de la fin de la saisie…|Wachten tot u klaar bent met typen…|Warten auf das Ende der Eingabe…
text_working|Translating offline… First use may take a moment.|Traduction hors ligne… La première utilisation peut prendre un instant.|Offline vertalen… De eerste keer kan even duren.|Offline-Übersetzung… Die erste Verwendung kann einen Moment dauern.
text_complete|Source: {languages}. Context notes: {count}.|Source : {languages}. Notes de contexte : {count}.|Bron: {languages}. Contextnotities: {count}.|Ausgangssprache: {languages}. Kontexthinweise: {count}.
text_review|Review context. Reference notes below are in English:|Vérifiez le contexte. Les notes de référence ci-dessous sont en anglais :|Controleer de context. De onderstaande referentienotities zijn in het Engels:|Kontext prüfen. Die folgenden Referenzhinweise sind auf Englisch:
text_uncertain|Uncertain / unsupported|Incertaine / non prise en charge|Onzeker / niet ondersteund|Unklar / nicht unterstützt
text_long|Long text: click Translate or press Ctrl+Enter (up to 50,000 characters).|Texte long : cliquez sur Traduire ou sur Ctrl+Entrée (50 000 caractères maximum).|Lange tekst: klik op Vertalen of druk op Ctrl+Enter (maximaal 50.000 tekens).|Langer Text: Übersetzen anklicken oder Strg+Eingabe drücken (bis zu 50.000 Zeichen).
text_limit|Please shorten the text to 50,000 characters or fewer.|Veuillez limiter le texte à 50 000 caractères.|Beperk de tekst tot maximaal 50.000 tekens.|Bitte kürzen Sie den Text auf höchstens 50.000 Zeichen.
text_paused|Text translation is paused while a document is being translated.|La traduction de texte est en pause pendant la traduction d’un document.|Tekstvertaling is gepauzeerd terwijl een document wordt vertaald.|Die Textübersetzung pausiert während der Dokumentübersetzung.
text_clipboard|The clipboard contains no text.|Le presse-papiers ne contient pas de texte.|Het klembord bevat geen tekst.|Die Zwischenablage enthält keinen Text.
text_copied|Translation copied.|Traduction copiée.|Vertaling gekopieerd.|Übersetzung kopiert.'''

MESSAGES = {}
for row in _ROWS.splitlines():
    key,*values = row.split('|')
    if len(values) != 4:
        raise ValueError('Invalid interface translation: '+key)
    MESSAGES[key] = dict(zip(LANGUAGE_NAMES, (v.replace(r'\n','\n') for v in values)))


def text(locale, key, **values):
    return MESSAGES[key][locale].format(**values)


def error_text(language, message):
    lower = message.lower()
    for fragment,key in [('cancelled','error_cancelled'),('password','error_password'),
                         ('no translatable','error_no_text'),('model is incomplete','error_model'),
                         ('verification failed','error_verification')]:
        if fragment in lower:
            return text(language,key)
    return text(language,'error_generic',details=message)
