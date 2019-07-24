#ifndef VISUALIZER_H
#define VISUALIZER_H

#include <memory>
#include <utility>

#include <QAudioInput>
#include <QByteArray>
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
#include "audiodevice.h"
#include "plotdata.h"

typedef std::complex<double> discriminator_t;

class Visualizer : public QMainWindow
{
    Q_OBJECT

public:
    /*! Make object to process input */
    Visualizer();
    
    ~Visualizer();
    
protected:
    /*! Find number of semitones between note 'name' and A4 
     *  and between the pitch class of the note and A
     *  \param name Note name, as pitch class, sharp or flat ('#' or 'b') and octave number
     *  \param EDO Number of division per octave. Defaults to 12.
     *  \returns Number of semitones between 'name' and A4, and between pitch class of 'name' and A
     * Note: currently only implemented for EDO=12.
     */
    std::pair<int, int> getNoteNum(QString name, const double EDO);
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
    /*! Make DetectorBank from current parameters */
    void makeDetectorBank();
    /*! Get number of samples in buffer */
    int getBufLen();
    /*! Set number of samples in buffer */
    void setBufLen(int newBuflen);
    /*! Picth class offset between the lowest note in the DetectorBank and A */ 
    std::size_t pitchOffset;
    /*! Number of samples in buffer (or frames for a stereo buffer) */
    int buflen = 4096;
    /*! DetectorBank that produces values */
    std::unique_ptr<DetectorBank> db;
    /*! Widget to plot DetectorBank data */
    std::unique_ptr<PlotData> plotData;

protected slots:
    void start();

private:
    void initializeWindow();
    void initializeAudio(const QAudioDeviceInfo &deviceInfo);
    void startAudio();

private slots:
//     void toggleSuspend();
    void deviceChanged(int index);
    void getDetBankData();
    

private:
    
    // Owned by layout
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

    std::unique_ptr<AudioDevice> audioDevice;
    std::unique_ptr<QAudioInput> audioInput;
};

#endif // VISUALIZER_H
