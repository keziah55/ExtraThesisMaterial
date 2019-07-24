#include "plotdata.h"
#include "visualizer.h"

#include <complex>

#include <QWidget>
#include <QVBoxLayout>
#include <QColor>
#include <QVector>
#include <QChart>
#include <QChartView>
#include <QScatterSeries>

PlotData::PlotData(const std::size_t chans, const int offset)
{
    setWindowTitle("Live Vizualizer");
      
    QVBoxLayout *layout = new QVBoxLayout;
      
    chart = new QChart();
    chart->setTheme(QChart::ChartThemeDark);
    chart->legend()->hide();
      
    std::size_t c_idx; // colour index
    // colours for an octave
    QVector<QColor> colourVector = {QColor(255,0,0),
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
      
      
    // make all the required series and set their colours
    for (std::size_t i{0}; i<chans; i++) {
        QScatterSeries *series = new QScatterSeries();
        c_idx = (static_cast<int>(i)+offset) % 12;
        series->setColor(colourVector[c_idx]);
        seriesVector.append(series);
        chart->addSeries(series);
    }
      
    QChartView *chartView = new QChartView(chart);
    layout->addWidget(chartView);
    showMaximized();
    setLayout(layout);
}

void PlotData::update(const discriminator_t* frames,
                      const std::size_t chans, 
                      const std::size_t numFrames)
{
    for (std::size_t i{0}; i<chans; i++) {
        seriesVector[i]->clear();
        
        for (std::size_t n{0}; n<numFrames; n++){
            // get current value
            discriminator_t z {frames[(i*chans)+n]};
            seriesVector[i]->append(z.real(), z.imag());
        }
    }
}
