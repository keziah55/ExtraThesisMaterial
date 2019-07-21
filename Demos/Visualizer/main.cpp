#include <QtWidgets>

#include "visualizer.h"

int main(int argv, char **args)
{
    QApplication app(argv, args);
    app.setApplicationName("Visualizer");

    Visualizer viz;
    viz.show();

    return app.exec();
}
