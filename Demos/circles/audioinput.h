#ifndef AUDIOINPUT_H
#define AUDIOINPUT_H

#include <memory>

#include <QAudioInput>
#include <QByteArray>
// #include <QChart>
#include <QComboBox>
#include <QMainWindow>
#include <QObject>
#include <QPixmap>
#include <QPushButton>
#include <QTextEdit>
#include <QSlider>
#include <QWidget>
#include <QScopedPointer>

#include "detectorbank.h"

class AudioInfo : public QIODevice
{
    Q_OBJECT

public:
    AudioInfo(const QAudioFormat &format);

    void start();
    void stop();

    qreal getLevel() const { return level; }

    qint64 readData(char *data, qint64 maxlen) override;
    qint64 writeData(const char *data, qint64 len) override;

private:
    const QAudioFormat format;
    quint32 maxAmplitude = 0;
    qreal level = 0.0; // 0.0 <= level <= 1.0

signals:
    void update();
};


class RenderArea : public QWidget
{
    Q_OBJECT

public:
    explicit RenderArea(QWidget *parent = nullptr);

    void setLevel(qreal value);

protected:
    void paintEvent(QPaintEvent *event) override;

private:
    qreal level = 0;
    QPixmap pixmap;
};


class InputTest : public QMainWindow
{
    Q_OBJECT

public:
    /*! Make object to process input */
    InputTest();
    
protected:
    void makeDetectorBank();
    int getSampleRateInt();
    double getSampleRateDbl();
    
    /*! Sample rate */
//     const int sr;      
    /*! DetectorBank that produces values */
    std::unique_ptr<DetectorBank> db; 

private:
    void initializeWindow();
    void initializeAudio(const QAudioDeviceInfo &deviceInfo);

private slots:
    void toggleMode();
//     void toggleSuspend();
    void deviceChanged(int index);
    void sliderChanged(int value);

private:
    
    // Owned by layout
    RenderArea *canvas = nullptr;
//     QPushButton *modeButton = nullptr;
//     QPushButton *suspendResumeButton = nullptr;
    QComboBox *deviceBox = nullptr;
    QComboBox *sRateBox = nullptr;
    
    QTextEdit *bandwidthEdit = nullptr;
    QTextEdit *dampingEdit = nullptr;
    QTextEdit *gainEdit = nullptr;
    QTextEdit *edoEdit = nullptr;
    QTextEdit *lwrEdit = nullptr;
    QTextEdit *uprEdit = nullptr;
    
    QPushButton *startButton = nullptr;
    
//     QSlider *volumeSlider = nullptr;

    QScopedPointer<AudioInfo> audioInfo;
    QScopedPointer<QAudioInput> audioInput;
    bool pullMode = true;
};

#endif // AUDIOINPUT_H
