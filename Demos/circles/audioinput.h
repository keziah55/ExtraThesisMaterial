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

    qreal level() const { return m_level; }

    qint64 readData(char *data, qint64 maxlen) override;
    qint64 writeData(const char *data, qint64 len) override;

private:
    const QAudioFormat m_format;
    quint32 m_maxAmplitude = 0;
    qreal m_level = 0.0; // 0.0 <= m_level <= 1.0

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
    qreal m_level = 0;
    QPixmap m_pixmap;
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
    RenderArea *m_canvas = nullptr;
    QPushButton *m_modeButton = nullptr;
//     QPushButton *m_suspendResumeButton = nullptr;
    QComboBox *m_deviceBox = nullptr;
    QComboBox *m_sRateBox = nullptr;
    QSlider *m_volumeSlider = nullptr;

    QScopedPointer<AudioInfo> m_audioInfo;
    QScopedPointer<QAudioInput> m_audioInput;
    bool m_pullMode = true;
};

#endif // AUDIOINPUT_H
