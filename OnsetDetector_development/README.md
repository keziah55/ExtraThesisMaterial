# OnsetDetector development

These files were used in the initial development and testing of the OnsetDetector
and generated the figures found in Chapter 3 of the thesis.

- **threshold.py** generates Figures 3.2 and 3.3, which show detectors 
with different damping factors, responding to a piano melody.

- **plot_before_voice_midi.py** generates the plots in Figure 3.4, comparing a
singing voice to a MIDI rendering.

- **SumGradient/sumgradient_test.py** generates Figures 3.5 and 3.6, which test the OnsetDetector
prototype which uses the sum gradient method. This is implemented in **SumGradient/preprocessor.py**
and **SumGradient/onsetdetector.py**.

- **HoughTransform/fit_lines.py** makes Figure 3.7, whih shows the response to a single sung note and
fits two lines to the shape, using functions from **HoughTransform/ht_funcs.py**.

- **HoughTransform/polar_line.py** demonstrates the polar form of a straight line, as seen in Figure 3.8.

- **HoughTransform/ht_single_note.py** takes the Hough transform of the single sung note, using 
[this Hough transformer](https://github.com/keziah55/HoughTransformer). It also uses 
**HoughTransform/plot_acc_surface.py** to plot this (Figure 3.10); however, [Plotly](https://plot.ly/) have
changed their interface, so this currently doesn't work. 

- **HoughTransform/plot_before_band.py** generates Figure 3.11 - a critical band of responses to a sung melody.

