#ifndef PLOTDATA_H
#define PLOTDATA_H

#include <complex>

#include <qwt_plot_canvas.h>
#include <qwt_plot.h>
#include <qwt_legend.h>
#include <qwt_plot_grid.h>
#include <qwt_plot_curve.h>
#include <qwt_symbol.h>

#include <QWidget>
#include <QVector>

typedef std::complex<double> discriminator_t;

class PlotData : public QWidget
{
    Q_OBJECT
    
public:
    /*! Make a PlotData window 
     *  \param numChans Number of channels in the DetectorBank
     *  \param offset Offset between A and the lowest note in the DetectorBank.
     *  Defaults to zero.
     */
    PlotData(const std::size_t numChans, 
             const int offset=0,
             QWidget *parent=nullptr);
    
public slots:
    // TODO figure out how data is passed from Visualizer to PlotData
    // if update() is a slot, it will be called by the QTimer in PlotData, so
    // can't take getZ data as args
    
    // If update takes new input samples (and the DetectorBank), we have
    // the same problem: the data needs to be sent from the Visualizer
    
    // If PlotData is given a reference to the DetectorBank, can Visualizer
    // call setInputBuffer() and PlotData knows about it?
    
    /*! Update chart from getZ data
     * \param frames Input array
     * \param numChans Height of input array
     * \param numFrames Length of input array
     */
    void update(const discriminator_t* frames,
                const std::size_t numChans,
                const std::size_t numFrames); 
    
protected:
    QwtPlot *plot;
    QVector<QwtPlotCurve*> curves;
    
};

#endif
