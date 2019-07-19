TEMPLATE = app
TARGET = audioinput

QT += multimedia widgets

HEADERS       = audioinput.h 

SOURCES       = audioinput.cpp \
                main.cpp 

target.path = .
INSTALLS += target
#include(../../shared/shared.pri)
