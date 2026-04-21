Diese interaktive Demo ist im **ScaDS.AI Living Lab** in Leipzig entstanden.
Sie zeigt, wie der Computer **Texte und Bilder** in eine **gemeinsame numerische Darstellung** übersetzt. Diese Darstellung heißt **Embedding**. Dadurch kann man Inhalte vergleichen, auch wenn sie aus unterschiedlichen Datentypen kommen.

---

## Embeddings - Wie aus Daten Seerosen werden

**Stell dir eine Stadt vor, in der Informationen leben:** Jede Information — ein Wort, ein Satz oder ein Bild — wohnt an einem Ort mit einer Adresse. Diese Adresse besteht aus vielen Zahlen und heißt **Embedding**.

Das Besondere ist: In dieser Stadt wohnen ähnliche Informationen in derselben Nachbarschaft. "Apfel" liegt also eher bei "Banane" als bei "Haus". Die Adresse, also das Embedding, enthält damit die Bedeutung der Information.

Genau das macht Embeddings in der Praxis so nützlich: Sie helfen bei **semantischer Suche** ("Finde Ähnliches"), **Clustering** (ähnliche Dinge automatisch gruppieren) und **Empfehlungen**.

> ### Embeddings in KI-Chatbots
> Embeddings spielen eine **zentrale Rolle** in **Large Language Models (LLMs)**, also in den Modellen hinter KI-Chatbots. Vereinfacht läuft es so: Eingaben werden tokenisiert, in Embeddings umgewandelt und durch die **Transformer-Schichten** geschickt. Kurz: Embeddings sind die numerische Sprache, in der das Modell Bedeutung verarbeitet.

### Multimodale Embeddings - CLIP

Das **CLIP**-Modell von OpenAI wurde dafür trainiert, **Bilder und Texte** in denselben Raum zu bringen. Es lernt einen **gemeinsamen Vektorraum**, indem passende Bild-Text-Paare näher zusammenrücken und unpassende Paare auseinandergehen. Ergebnis: Ein Satz und ein Bild, die dasselbe meinen, liegen oft **nah beieinander**.

![CLIP-Kodierung von Text und Bildern in gemeinsame Embeddings](/blogpost/clip_embeddings.gif)

Wenn du tiefer einsteigen willst: Hier ist die OpenAI-Veröffentlichung zu CLIP: [openai.com/research/clip](https://openai.com/research/clip)

### Wie die Seerosen dargestellt werden

In unserer Visualisierung sind Embeddings **Seerosen auf einem Teich**. Jede Seerose steht für eine Eingabe — Text oder Bild — und ihre Position entspricht der Lage ihres Embeddings. Ähnliche Eingaben landen also auch als Seerosen nah beieinander.

Auch die **Form der Seerose** wird aus den **Embedding-Werten** erzeugt. In der Animation siehst du, wie aus den Zahlen Schritt für Schritt die Kontur entsteht.

Die **Farbe** wird ebenfalls aus dem Embedding abgeleitet. In dieser Demo ist sie auf einen **Rosa-bis-Weiß**-Bereich begrenzt.

![Embedding-Werte formen Seerosenkontur und Farbe](/blogpost/waterlily_render.gif)

---

## Seerosen pflanzen - Von hunderten Dimensionen zu 2D

Embeddings leben in einem Raum mit **hunderten Dimensionen** — weit mehr, als wir uns in 2D oder 3D vorstellen können. Damit wir sie auf einem flachen Teich zeigen können, müssen wir diesen Raum auf **zwei Koordinaten** reduzieren, ohne die Beziehungen zwischen den Embeddings zu verlieren.

Eine gängige Methode dafür ist **PCA** (Principal Component Analysis). PCA findet die Richtungen mit der größten Streuung in den Daten und projiziert die Embeddings auf diese Achsen. Das Ergebnis ist eine **2D-Skizze** des ursprünglichen Raums. Sie ist nicht perfekt, zeigt aber oft gut, welche Embeddings nahe beieinander liegen.

### Die Modality Gap

Das Bild unten zeigt so eine **2D-Projektion**. Dabei taucht oft ein typisches Muster auf: **Textpunkte** und **Bildpunkte** landen in **verschiedenen Regionen**. Diese räumliche Trennung nennt man **Modality Gap**. Das heißt: Selbst wenn ein Satz und ein Bild dasselbe ausdrücken, liegen ihre Vektoren nicht immer so nah, wie man erwarten würde.

Sinnvolle Ähnlichkeiten kann man trotzdem berechnen. Visuell entsteht aber oft ein schiefes Bild, das du auch in unserem Seerosenteich siehst. Wir haben ein paar Ansätze eingebaut, um diesen Effekt abzuschwächen. Du findest sie im Bereich **Wissenschaft** unten rechts. Probier die Regler aus und schau, wie sich das Layout verändert.

![Visualisierung der Modality Gap](/blogpost/modality_gap.jpeg)

In dieser Grafik wurde statt PCA **UMAP** verwendet. Die Idee ist ähnlich, aber UMAP macht die Modality Gap häufig noch sichtbarer. Mehr dazu [hier](https://biostatsquid.com/pca-umap-tsne-comparison/).

---

## Technik

Alles läuft direkt in deinem **Browser**. Es gibt keine **serverseitige Berechnung** und deine Eingaben werden von dieser App nicht an externe Server geschickt.

Die Embeddings werden mit [Transformers.js](https://github.com/huggingface/transformers.js) berechnet. Dafür wird ein [CLIP](https://openai.com/index/clip/)-Modell lokal ausgeführt.

Transformers.js nutzt dafür Browser-Technologien wie **WebAssembly (WASM)** und je nach Gerät **WebGPU/WebGL**. Wie schnell das läuft, hängt von Browser und Hardware ab.

### Was passiert beim Klick auf "Wachsen lassen"

**Text** wird in Token-IDs zerlegt, **Bilder** werden skaliert und normalisiert. Beides geht durch **CLIP**, das daraus einen **Embedding-Vektor** berechnet. Danach leitet die App daraus **Form** und **Farbe** der Seerose ab und rendert sie als SVG.

Wenn du danach auf **"Einpflanzen"** klickst, berechnet die App das **PCA-Layout** neu und setzt die Positionen aller Seerosen im Teich.

### Modelldownload und Caching

Beim ersten Start der Demo werden die **Modelldateien** in deinen Browser geladen. Danach kann der Browser sie **cachen**, sodass spätere Durchläufe schneller sind.

### Datenverarbeitung

Die App **lädt** deine Texte oder Bilder **nicht hoch**. Wenn du eine Bilddatei auswählst, erzeugt der Browser eine **lokale Object URL**, damit das Bild auf deinem Gerät angezeigt und verarbeitet werden kann.

Die erzeugten Embeddings werden nur **im Arbeitsspeicher** während der Laufzeit gehalten und weder dauerhaft gespeichert noch an einen Server gesendet.
