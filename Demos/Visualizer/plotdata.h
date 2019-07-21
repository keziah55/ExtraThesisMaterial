#ifndef PLOTDATA_H
#define PLOTDATA_H

#include <complex>

#include <QWidget>
#include <QXYSeries>
#include <QTimer>

#include "detectorbank.h"

typedef std::complex<double> discriminator_t;

class PlotData : public QWidget
{
    Q_OBJECT
    
public:
    /*! Make a PlotData window 
     */
    PlotData();
    
public slots:
    // TODO figure out how data is passed from Visualizer to PlotData
    // if update() is a slot, it will be called by the QTimer in PlotData, so
    // can't take getZ data as args
    
    // If update takes new input samples (and the DetectorBank), we have
    // the same problem: the data needs to be sent from the Visualizer
    
    // If PlotData is given a reference to the DetectorBank, can Visualizer
    // call setInputBuffer() and PlotData knows about it?
    
    /*! Update chart from getZ data
     * \param frames Output array
     * \param chans Height of output array
     * \param numFrames Length of output array
     */
    void update(discriminator_t* frames,
                std::size_t chans, std::size_t numFrame); 
    
protected:
     /*! The DetectorBank which produces the results */
    DetectorBank& db;
//     QXYSeries *series = nullptr;
    QTimer timer;
};

#endif
