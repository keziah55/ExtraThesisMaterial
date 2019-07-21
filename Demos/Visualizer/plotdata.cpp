#include "plotdata.h"
#include "visualizer.h"

#include <QWidget>
#include <QChartView>
#include <QTimer>
#include <QXYSeries>

PlotData::PlotData(DetectorBank& db)
  : db(db)
{
      setWindowTitle("Live Vizualizer");
//       showFullScreen();
      showMaximized();
      
      // look at dynamicspline to figure this out
      connect(&timer, &QTimer::timeout, this, &PlotData::update);
      timer.setInterval(30);
      
//       series = new QXYSeries();
      
      
      timer.start();
}

void PlotData::update()
{
    
}
