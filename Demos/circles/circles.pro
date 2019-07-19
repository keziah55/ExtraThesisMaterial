TEMPLATE = app
TARGET = audioinput

QT += multimedia widgets

HEADERS       = audioinput.h 

SOURCES       = audioinput.cpp \
                main.cpp 

target.path = .
INSTALLS += target

INCLUDEPATH += /usr/local/include/detectorbank
DEPENDPATH += ./usr/local/include/detectorbank

unix:!macx: PRE_TARGETDEPS += /usr/local/lib/libdetectorbank.so
