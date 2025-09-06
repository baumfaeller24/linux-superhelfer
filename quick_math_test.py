import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules', 'module_a_core'))

from query_analyzer import QueryAnalyzer

def quick_test():
    analyzer = QueryAnalyzer()
    
    test_cases = [
        ("Löse das Gleichungssystem: x + y = 10, x - y = 2", "heavy"),
        ("Berechne Fibonacci-Zahlen bis 100", "heavy"),
        ("Implementiere eine Fibonacci-Funktion in Python", "code"),
        ("Welcher Befehl zeigt alle Prozesse?", "fast"),
        
        # Sehr schwierige Mathematikaufgaben
        ("Berechne das Integral von 0 bis unendlich: sin(x)/x dx", "heavy"),
        ("Finde die Eigenwerte der Matrix [[2,-1,0],[-1,2,-1],[0,-1,2]]", "heavy"),
        ("Bestimme die Anzahl der Derangements von {1,...,9}", "heavy"),
        ("Zeige, dass pi(n) ~ n / ln(n) für n gegen unendlich", "heavy"),
        ("Zeige, dass M_n = X_n^2 - n ein Martingal ist (symmetrischer Random Walk)", "heavy"),
        ("Finde die Fourierreihe von f(x)=x auf (-pi,pi)", "heavy"),
        ("Berechne die Fläche eines gleichseitigen Dreiecks im Einheitskreis", "heavy"),
        ("Faktorisiere das Polynom x^4 + 4 über den komplexen Zahlen", "heavy"),
        ("Zeige, dass Summe über k=0..n von binom(n,k)^2 gleich binom(2n,n) ist", "heavy"),
        ("Bestimme die Anzahl der Lösungen der Kongruenz x^2 ≡ 1 mod 105", "heavy"),

        # 10 anspruchsvolle Textaufgaben
        ("TSP-Minimum: Vier Städte A,B,C,D. Symmetrische Distanzen: AB=7, AC=9, AD=8, BC=6, BD=7, CD=5. Finde die minimale Rundreise A->...->A und ihre Länge.", "heavy"),
        ("Bayes-Update: Praevalenz 0.8%. Test: Sensitivität 99%, Spezifität 96%. Zwei unabhängige Tests positiv. Posterior P(krank|++)?", "heavy"),
        ("Portfolio-Minimumvarianz: Var1=0.04, Var2=0.09, Kor=0.3. Finde Gewichte und Varianz des MV-Portfolios ohne Nebenbedingungen.", "heavy"),
        ("Projektplanung CPM: Dauern A=4, B=6, C=3, D=5, E=2. Abh.: B nach A, C nach A, D nach B und C, E nach D. Projektdauer und kritischer Pfad?", "heavy"),
        ("Spieltheorie: Nullsummenspiel Auszahlung an A: [[2,-1],[0,1]]. Finde gemischtes Nash-GG und Spielwert.", "heavy"),
        ("Kryptarithmus: SEND + MORE = MONEY. Finde eine zulässige Ziffernzuordnung.", "heavy"),
        ("Kreisgeometrie: Kreis mit Durchmesser 10. Rechtwinkliges Dreieck ABC auf dem Kreis. AB=6. Bestimme BC und die Bogenlängen ueber den Seiten.", "heavy"),
        ("Zahlentheorie: Anzahl ganzzahliger Paare (a,b) mit a^2 + b^2 = 2025.", "heavy"),
        ("Kombinatorik: Wie viele 10-stellige Dezimalzahlen (erste Ziffer !=0) haben Quersumme 45?", "heavy"),
        ("W'keit: Urne 3 rot, 2 schwarz. Zwei Zuege ohne Zuruecklegen. Bedingung: mindestens eine rot. P(beide rot | mindestens eine rot)?", "heavy"),

        # Weitere sehr schwierige Probleme
        ("PDE: Loese die Waermeleitung u_t = u_xx fuer x in R, t>0, Anfangsdaten f(x)=exp(-x^2). Gib u(x,t) explizit an.", "heavy"),
        ("Spektralgraphen: Zeige, dass die Eigenwerte der Laplace-Matrix eines zusammenhaengenden Graphen 0 = lambda1 < lambda2 <= ... sind und interpretiere lambda2.", "heavy"),
        ("Konvexe Optimierung: Zeige starke Dualitaet fuer ein strikt konvexes quadratisches Programm mit linearen Nebenbedingungen und Slater-Bedingung; berechne das Dual eines konkreten QP.", "heavy"),
        ("Maßtheorie: Zeige, dass Lp([0,1]) fuer 1<=p<infty separabel ist, aber L_infty([0,1]) nicht.", "heavy"),
        ("Funktionalgleichung: Finde alle f:R->R mit f(x+y)+f(x-y)=2f(x)+2f(y) und f stetig.", "heavy"),
        ("Extremal-Kombinatorik: Beweise Satz von Erdős–Ko–Rado fuer n>=2k: maximale Groesse eines k-Teilsystems mit schnitt != leer.", "heavy"),
        ("Informationstheorie: Zeige Kraft-Ungleichung und leite die Quellencodierungsgrenze fuer praefixfreie Codes her.", "heavy"),
        ("Stochastische Analysis: Wende Ito-Lemma auf X_t = exp(B_t - t/2) an und zeige, dass (X_t) ein Martingal ist; berechne E[X_t].", "heavy"),
        ("Fourier-Analyse: Zeige die Poisson-Summationsformel fuer eine Schwartz-Funktion und wende sie auf die Theta-Reihe an.", "heavy"),
        ("Lineare Algebra: Charakterisiere normal diagonaliserbare Operatoren via Spektralsatz; gib ein Beispiel eines nichtnormalen, aber diagonalisierbaren Operators.", "heavy"),
        ("Zahlentheorie: Bestimme alle ganzzahligen Loesungen von x^4 + y^4 = z^2 (Fermat-Pythagoras-Variante).", "heavy"),
        ("Kombinatorik: Bestimme die Anzahl der Standard-Young-Tableaux einer Form 2 x n (zwei Zeilen, n Spalten).", "heavy"),
        ("Topologie: Zeige, dass jede stetige Bijektion von kompakt nach Hausdorff ein Homöomorphismus ist; gib ein Gegenbeispiel ohne Kompaktheit.", "heavy"),
        ("Optimierung: Loese ein Transportproblem mit Kostenmatrix C=[[2,3,1],[5,4,8]] und Angebots/Bedarfsvektoren a=[30,70], b=[20,50,30] via Nordwestecke und MODI.", "heavy"),
        ("Geometrie: Beweise isoperimetrische Ungleichung in der Ebene in der Form 4*pi*A <= L^2 und bestimme den Gleichheitsfall.", "heavy"),
        ("W-Theorie: Zeige SLLN fuer iid mit E|X1|<infty via Kolmogorov; wende auf Bernoulli(p) an.", "heavy"),
        ("Codierungstheorie: Konstruiere einen (7,4)-Hamming-Code, gib Generator- und Paritaetsmatrix an und zeige Korrektur eines Einzelfehlers.", "heavy"),
        ("Graphentheorie: Ramsey-Zahl R(3,3)=6. Beweise mittels Pigeonhole-Argument und Fallunterscheidung.", "heavy"),
        ("Variationsrechnung: Loese Brachistochrone zwischen zwei Punkten im Schwerefeld; leite die Zykloide her.", "heavy"),
        ("Konvexe Geometrie: Beweise Carathéodorys Satz in R^d und gib ein Beispiel fuer d=2.", "heavy"),
    ]
    
    print("🔍 QUICK MATH TEST")
    print("=" * 30)
    
    for query, expected in test_cases:
        result = analyzer.analyze_query(query)
        status = "✅" if result.route_model == expected else "❌"
        print(f"{status} {result.route_model.upper()} (expected: {expected.upper()})")
        print(f"    Query: {query}")
        if result.route_model != expected:
            print(f"    ⚠️ FAILED! Expected {expected}, got {result.route_model}")
        print()

if __name__ == "__main__":
    quick_test()
