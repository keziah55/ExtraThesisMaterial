#ifndef PLOTDATA_H
#define PLOTDATA_H

#include <QWidget>

#include "detectorbank.h"

class PlotData : public QWidget
{
    Q_OBJECT
    
public:
    /*! Make a PlotData window 
     *  \param db DetectorBank that will provide the data 
     */
    PlotData(DetectorBank& db);
    
    void update(); // should take input buffer as arg
    
protected:
     /*! The DetectorBank which produces the results */
    DetectorBank& db;
};

#endif
