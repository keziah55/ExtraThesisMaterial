TEMPLATE = app
TARGET = audioinput

QT += multimedia widgets

HEADERS       = audioinput.h 

SOURCES       = audioinput.cpp \
                main.cpp 

target.path = .
INSTALLS += target

#INCLUDEPATH += /usr/local/include/detectorbank
#DEPENDPATH += ./usr/local/include/detectorbank

unix:!macx: PRE_TARGETDEPS += /usr/local/lib/libdetectorbank.so

unix:!macx: LIBS += -L/usr/local/lib/ -ldetectorbank

INCLUDEPATH += /usr/local/include
DEPENDPATH += /usr/local/include

unix:!macx: LIBS += -lfftw3f
