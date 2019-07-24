TEMPLATE = app
TARGET = visualizer

QT += charts multimedia widgets

HEADERS += visualizer.h \
           audiodevice.h \
           plotdata.h

SOURCES += visualizer.cpp \
           audiodevice.cpp \
           plotdata.cpp \
           main.cpp 

target.path = .
INSTALLS += target

unix:!macx: PRE_TARGETDEPS += /usr/local/lib/libdetectorbank.so

unix:!macx: LIBS += -L/usr/local/lib/ -ldetectorbank -lfftw3f
unix:!macx: LIBS += -L/usr/lib/ -lqwt-qt5

INCLUDEPATH += /usr/local/include/detectorbank /usr/include/qwt/
DEPENDPATH += ./usr/local/include/detectorbank /usr/include/qwt
