# DetectorBank development

These files were used in the initial development and testing of the DetectorBank
and generated the figures found in Section 2.2 of the thesis.

- **frequency_response.py** generates many of the figures in Section 2.2.1 
Frequency Response. In order to reproduce these results, several features in the 
DetectorBank source must be disabled: amplitude scaling, frequency shifting and 
sample rate limitation.

- **oscillations.py** shows the small oscillations in a repsonse, and generates 
Figures 2.4 and 2.7. Requires `peakdetect.py`, originally found 
[here](https://gist.github.com/endolith/250860#file-peakdetect-py).

- **eccentricity.py** plots the complex response at 5Hz and 400Hz, to illustrate
orbital eccentricity. Figures 2.5 and 2.6.

- **amp_scaling.py** generates Figure 2.12, which shows the decay in response amplitude
 as frequency increases. This script calculates this at two sample rates, for both
 numerical methods and both with and without frequency normalisation, and was originally
 used to generate the `scale_values.inc` file found in the DetectorBank repo.
 
 
