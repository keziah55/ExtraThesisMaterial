#include "plotdata.h"
#include "visualizer.h"

#include <complex>
#include <iostream>

#include <QWidget>
#include <QVBoxLayout>
#include <QColor>
#include <QVector>

PlotData::PlotData(const std::size_t numChans, const int offset, 
                   QWidget *parent)
  : QWidget(parent)
{
    QWidget *window = new QWidget;
    setWindowTitle("Live Visualizer");
    
    QwtPlot *plot = new QwtPlot(parent);
      
    QVBoxLayout *layout = new QVBoxLayout;
    
    // colours for an octave
    QVector<QColor> colours = {QColor(255,0,0),
                               QColor(255,0,255),
                               QColor(255,136,0),
                               QColor(255,255,0),
                               QColor(85,255,0),
                               QColor(128,0,255),
                               QColor(0,153,0),
                               QColor(255,255,255),
                               QColor(0,178,178),
                               QColor(178,178,36),
                               QColor(0,170,255),
                               QColor(0,43,255)};
      
    // instead of seriesVector, store a vector of QVector<QPointF>
      
                                    
    // make all the required series and set their colours
    std::size_t c_idx; // colour index
    for (std::size_t i{0}; i<numChans; i++) {
        QwtPlotCurve *curve = new QwtPlotCurve();
        c_idx = (static_cast<int>(i)+offset) % 12;
        curve->setPen(colours[c_idx], 1.0);
        curves.append(curve);
        curve->attach(plot);
    }

    plot->setAxisScale(0, -50, 50);
    plot->setAxisScale(2, -50, 50);
    plot->updateAxes();
    
    showMaximized();
    layout->addWidget(plot);
    setLayout(layout);
    window->setLayout(layout);
    window->show();
}

void PlotData::update(const discriminator_t* frames,
                      const std::size_t numChans, 
                      const std::size_t numFrames)
{
    double x[numFrames];
    double y[numFrames];
    
    for (std::size_t i{0}; i<numChans; i++) {
        for (std::size_t n{0}; n<numFrames; n++){
            discriminator_t z {frames[(i*numFrames)+n]};
            x[n] = z.real();
            y[n] = z.imag();
        }
        curves[i]->setSamples(x, y, numFrames);
    }
//     plot->replot();
}
