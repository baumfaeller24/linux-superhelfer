# 🔍 Modell-Research Template

## Suchkriterien für GitHub/Ollama Library

### Standard-Modell (15GB VRAM-Bereich)
- **Größe**: 11B - 20B Parameter
- **Quantisierung**: Q4_K_M oder Q5_K_M
- **VRAM**: 12-15GB bei Quantisierung
- **Release**: 2024/2025
- **Ollama-Support**: Verfügbar

### Kandidaten zum Prüfen:
```bash
# Aktuelle Modelle checken:
ollama list
ollama search llama
ollama search qwen
ollama search mistral
```

### Bewertungskriterien:
1. **VRAM-Verbrauch** (exakte Angaben)
2. **Performance-Benchmarks** (MMLU, HumanEval)
3. **Code/Linux-Performance** 
4. **Deutsche Sprache** Support
5. **Community-Feedback**

### Template für Modell-Bewertung:
```
Modell: [Name]
Parameter: [Anzahl]B
Quantisierung: [Q4/Q5]
VRAM: [GB] 
Benchmarks: [Scores]
Ollama-Command: ollama pull [model]
```

## Backup-Plan falls nichts Passendes:
- Llama 3.2 11B als Basis
- Custom Quantisierung testen
- Mehrere kleinere Modelle parallel