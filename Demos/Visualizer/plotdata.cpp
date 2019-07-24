#include "plotdata.h"
#include "visualizer.h"

#include <complex>

#include <QWidget>
#include <QChartView>
#include <QXYSeries>

PlotData::PlotData()
{
      setWindowTitle("Live Vizualizer");
//       showFullScreen();
      showMaximized();
      
      
      
//       series = new QXYSeries();
      
      
      
}

void PlotData::update(discriminator_t* frames,
                std::size_t chans, std::size_t numFrame)
{
    
}
