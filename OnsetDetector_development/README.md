# OnsetDetector development

These files were used in the initial development and testing of the OnsetDetector
and generated the figures found in Chapter 3 of the thesis. The directories here correspond
to the three onset detection methods prototyped, and the data directory contains some audio files
used to generate these graphs.

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
**HoughTransform/plot_acc_surface.py** to plot this (Figure 3.10); [Plotly](https://plot.ly/) have
changed their interface, so the function using thi library currently doesn't work, but the 
[Matplotlib](https://matplotlib.org/) function does work (and can plot in either 2D or 3D).

- **MeanLog/plot_before_band.py** generates Figures 3.11 and 3.13b - a critical band of responses to a sung melody.

- **MeanLog/plot_seg_mean.py** makes Figures 3.12, 3.13a and 3.14, which show the segment means of a band of reponses,
using **MeanLog/onsetdetector_temp.py** to generate the segment averages.

- **MeanLog/plot_mean_log1.py** makes Figures 3.15, 3.16 and 3.17, which show the mean log and highlight
key areas when detecting onsets. This implements the mean log algorithm directly in Python.

- **MeanLog/plot_mean_log2.py** generates Figure 3.18, which again shows the mean log and onsets for a given sample,
using the C++ `OnsetDetector`. To run this, first download the Trumpet files from the 
[University of Iowa musical instrument sample respository](http://theremin.music.uiowa.edu/MIS-Pitches-2012/MISBbTrumpet2012.html) 
and set the appropriate path to the `Trumpet.vib.ff.C4.stereo.wav` file.
