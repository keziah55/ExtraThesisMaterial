#include "plotdata.h"
#include "visualizer.h"

#include <complex>

#include <QWidget>
#include <QChartView>
#include <QTimer>
#include <QXYSeries>

PlotData::PlotData()
{
      setWindowTitle("Live Vizualizer");
//       showFullScreen();
      showMaximized();
      
      connect(&timer, &QTimer::timeout, this, &PlotData::update);
      timer.setInterval(30);
      
//       series = new QXYSeries();
      
      
      timer.start();
}

void PlotData::update()
{
    
}
