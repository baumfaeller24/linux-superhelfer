# Anforderungsdokument

## Einführung

Das Linux Superhelfer System hat derzeit keine Kontextwahrnehmung zwischen aufeinanderfolgenden Benutzeranfragen, was zu einer schlechten Benutzererfahrung führt, wenn Benutzer Folgefragen stellen. Zum Beispiel, wenn ein Benutzer "was ist linux?" fragt, gefolgt von "wer hat es erfunden?", behandelt das System die zweite Frage als isoliert, anstatt zu verstehen, dass sie sich auf Linux bezieht. Diese Funktion wird sitzungsbasierte Kontextverfolgung implementieren, um einen natürlichen Gesprächsfluss zu ermöglichen.

## Anforderungen

### Anforderung 1

**User Story:** Als Benutzer möchte ich, dass das System sich an vorherige Fragen in unserem Gespräch erinnert, damit ich Folgefragen stellen kann, ohne den Kontext zu wiederholen.

#### Akzeptanzkriterien

1. WENN ein Benutzer eine Folgefrage stellt DANN SOLL das System Kontext aus vorherigen Fragen in derselben Sitzung verwenden
2. WENN ein Benutzer "wer hat es erfunden?" nach einer Frage über Linux fragt DANN SOLL das System verstehen, dass sich die Frage auf Linux bezieht
3. WENN das System eine Anfrage mit verfügbarem Kontext verarbeitet DANN SOLL es "Context Used: True" protokollieren
4. WENN eine Sitzung keinen vorherigen Kontext hat DANN SOLL das System Anfragen normal ohne Kontext verarbeiten

### Anforderung 2

**User Story:** Als Benutzer möchte ich, dass meine Gesprächssitzungen automatisch verwaltet werden, damit ich die Sitzungserstellung oder -bereinigung nicht manuell handhaben muss.

#### Akzeptanzkriterien

1. WENN ein Benutzer die UI zu verwenden beginnt DANN SOLL das System automatisch eine eindeutige Sitzungs-ID erstellen
2. WENN ein Benutzer seine erste Anfrage sendet DANN SOLL das System eine neue Gesprächssitzung erstellen
3. WENN eine Sitzung länger als 1 Stunde inaktiv ist DANN SOLL das System automatisch abgelaufene Sitzungen bereinigen
4. WENN die UI aktualisiert wird DANN SOLL das System dieselbe Sitzung bis zum Timeout beibehalten

### Anforderung 3

**User Story:** Als Benutzer möchte ich, dass das System relevanten Kontext bereitstellt, ohne das AI-Modell zu überlasten, damit Antworten schnell und genau bleiben.

#### Akzeptanzkriterien

1. WENN Kontext für eine Anfrage erstellt wird DANN SOLL das System nur die letzten 5 Gesprächsrunden einbeziehen
2. WENN der Kontext 2000 Token überschreitet DANN SOLL das System älteren Kontext kürzen, um innerhalb der Grenzen zu bleiben
3. WENN Kontext zu einer Anfrage hinzugefügt wird DANN SOLL das System ihn klar für das AI-Modell formatieren
4. WENN kein relevanter Kontext existiert DANN SOLL das System die Anfrage ohne Kontext-Overhead verarbeiten

### Anforderung 4

**User Story:** Als Entwickler möchte ich die Kontextnutzung und Sitzungsstatistiken überwachen, damit ich die Gesprächserfahrung optimieren kann.

#### Akzeptanzkriterien

1. WENN eine Anfrage Kontext verwendet DANN SOLL das System die Anzahl der einbezogenen vorherigen Runden protokollieren
2. WENN Anfragen verarbeitet werden DANN SOLL das System Kontextnutzungsstatistiken pro Sitzung verfolgen
3. WENN Sitzungen erstellt oder ablaufen DANN SOLL das System Sitzungslebenszyklus-Ereignisse protokollieren
4. WENN Kontext gekürzt wird DANN SOLL das System die Kürzung zur Überwachung protokollieren

### Anforderung 5

**User Story:** Als Benutzer möchte ich, dass kontextbewusstes Routing mit dem bestehenden intelligenten Modell-Routing funktioniert, damit Folgefragen an geeignete Modelle weitergeleitet werden.

#### Akzeptanzkriterien

1. WENN eine Anfrage Kontext hat DANN SOLL das Routing-System sowohl die aktuelle Anfrage als auch den Kontext für die Modellauswahl berücksichtigen
2. WENN der Kontext ein mathematisches Gespräch anzeigt DANN SOLLEN Folgefragen angemessen an schwere Modelle weitergeleitet werden
3. WENN der Kontext eine Programmierdiskussion anzeigt DANN SOLLEN Folgefragen angemessen an Code-Modelle weitergeleitet werden
4. WENN mit Kontext geroutet wird DANN SOLL das System die Routing-Entscheidung und den Kontexteinfluss protokollieren