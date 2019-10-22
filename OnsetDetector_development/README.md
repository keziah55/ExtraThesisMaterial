# OnsetDetector development

These files were used in the initial development and testing of the OnsetDetector
and generated the figures found in Chapter 3 of the thesis.

- **threshold.py** generates Figures 3.2 and 3.3, which show detectors 
with different damping factors, responding to a piano melody.

- **plot_before_voice_midi.py** generates the plots in Figure 3.4, comparing a
singing voice to a MIDI rendering.

- **SumGradient/gradient_test_dream.py** generates Figures 3.5 and 3.6, which test the OnsetDetector
prototype which uses the sum gradient method. This is implemented in **SumGradient/preprocessor.py**
and **SumGradient/onsetdetector.py**.

