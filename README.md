# Extra thesis material

A repository of Python scripts used in the development and 
testing of the software I created for my PhD thesis.

Documentation and installation instructions for the software – DetectorBank – 
is hosted [here](https://github.com/keziah55/DetectorBank).

Each directory contains it's own readme, describing the files.
The OnsetDetector development and testing directories also contain results
directories, from which tables in Chapters 3 and 4 of the thesis can be reconstructed.

I've tried to tidy up the files, but let me know if anything is unclear.
A number of the 
[OnsetDetector_testing](https://github.com/keziah55/ExtraThesisMaterial/tree/master/OnsetDetector_testing) 
files may use `SavePlot` or `SaveLegend` 
objects, which can be found [here](https://github.com/keziah55/save_plot).
Alternatively, SavePlot commands can be replaced with 
[`matplotlib.pyplot.savefig()`](https://matplotlib.org/3.1.0/api/_as_gen/matplotlib.pyplot.savefig.html)
or similar.
