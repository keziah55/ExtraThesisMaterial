#ifndef PLOTDATA_H
#define PLOTDATA_H

#include <complex>

#include <QWidget>
#include <QVector>
#include <QScatterSeries>
#include <QChart>
#include <QChartView>

QT_CHARTS_BEGIN_NAMESPACE
class QChartView;
class QChart;
QT_CHARTS_END_NAMESPACE

typedef std::complex<double> discriminator_t;

QT_CHARTS_USE_NAMESPACE

class PlotData : public QWidget
{
    Q_OBJECT
    
public:
    /*! Make a PlotData window 
     *  \param chans Number of channels in the DetectorBank
     *  \param offset Offset between A and the lowest note in the DetectorBank.
     *  Defaults to zero.
     */
    PlotData(const std::size_t chans, 
             const int offset=0);
    
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
    void update(const discriminator_t* frames,
                const std::size_t chans, const std::size_t numFrames); 
    
protected:
    QChart *chart;
    QVector<QScatterSeries*> seriesVector;
    
};

#endif
