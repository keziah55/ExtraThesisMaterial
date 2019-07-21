#ifndef PLOTDATA_H
#define PLOTDATA_H

#include <QWidget>
#include <QXYSeries>
#include <QTimer>

#include "detectorbank.h"

class PlotData : public QWidget
{
    Q_OBJECT
    
public:
    /*! Make a PlotData window 
     *  \param db DetectorBank that will provide the data 
     */
    PlotData(DetectorBank& db);
    
public slots:
    void update(); // should take input buffer as arg
    
protected:
     /*! The DetectorBank which produces the results */
    DetectorBank& db;
//     QXYSeries *series = nullptr;
    QTimer timer;
};

#endif
