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
#include <QLineEdit>
#include <QSlider>
#include <QWidget>
#include <QScopedPointer>

#include "detectorbank.h"

class AudioDevice : public QIODevice
{
    Q_OBJECT

public:
    AudioDevice(const QAudioFormat &format);

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


class Visualizer : public QMainWindow
{
    Q_OBJECT

public:
    /*! Make object to process input */
    Visualizer();
    
protected:
    /*! Find number of semitones between note 'name' and A4 
     *  \param name Note name, as pitch class, sharp or flat ('#' or 'b') and octave number
     *  \param EDO Number of division per octave. Defaults to 12.
     * Note: currently only implemented for EDO=12.
     */
    int getNoteNum(QString name, const double EDO);
    /*! Convert a bandwidth given in cents to Hertz 
     *  \param f0 Centre frequency, around which the bandwidth will be calculated
     *  \param cents Bandwidth in cents
     *  \param EDO Number of division per octave. Defaults to 12.
     */
    double centsToHz(const double f0, const double cents,
                     const double EDO);
    /*! Return the sample rate as a integer */
    int getSampleRateInt();
    /*! Return the sample rate as a double */
    double getSampleRateDbl();
    
       
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
    void makeDetectorBank();

private:
    
    // Owned by layout
    RenderArea *canvas = nullptr;
//     QPushButton *modeButton = nullptr;
//     QPushButton *suspendResumeButton = nullptr;
    QComboBox *deviceBox = nullptr;
    QComboBox *sRateBox = nullptr;
    
    QLineEdit *bandwidthEdit = nullptr;
    QLineEdit *dampingEdit = nullptr;
    QLineEdit *gainEdit = nullptr;
    QLineEdit *edoEdit = nullptr;
    QLineEdit *lwrEdit = nullptr;
    QLineEdit *uprEdit = nullptr;
    
    QPushButton *startButton = nullptr;
    
//     QSlider *volumeSlider = nullptr;

    QScopedPointer<AudioDevice> audioDevice;
    QScopedPointer<QAudioInput> audioInput;
    bool pullMode = true;
};

#endif // AUDIOINPUT_H
