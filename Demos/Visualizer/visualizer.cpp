#include <stdlib.h>
#include <math.h>
#include <stdexcept>

#include <Qt>

#include <QDateTime>
#include <QDebug>

#include <QHBoxLayout>
#include <QVBoxLayout>
#include <QGridLayout>

#include <QPushButton>
#include <QLineEdit>
#include <QLabel>

#include <QAudioDeviceInfo>
#include <QAudioInput>

#include <qendian.h>

#include <QVector>
#include <QString>
#include <QList>

#include <QTimer>

#include "visualizer.h"
#include "audiodevice.h"
#include "detectorbank.h"
#include "plotdata.h"


Visualizer::Visualizer()
{
    initializeWindow();
}


void Visualizer::initializeWindow()
{
    QWidget *window = new QWidget;
    QVBoxLayout *layout = new QVBoxLayout;

    // layout for audio device and sample rate selection
    QHBoxLayout *deviceLayout = new QHBoxLayout;

    // make audio device selection box
    deviceBox = new QComboBox(this);
    const QAudioDeviceInfo &defaultDeviceInfo = QAudioDeviceInfo::defaultInputDevice();
    deviceBox->addItem(defaultDeviceInfo.deviceName(), 
                         qVariantFromValue(defaultDeviceInfo));
    for (auto &deviceInfo: QAudioDeviceInfo::availableDevices(QAudio::AudioInput)) {
        if (deviceInfo != defaultDeviceInfo) {
            deviceBox->addItem(deviceInfo.deviceName(), 
                                 qVariantFromValue(deviceInfo));
        }
    }

    connect(deviceBox, QOverload<int>::of(&QComboBox::activated), this, 
            &Visualizer::deviceChanged);
    
    // make sample rate label and textedit
    QLabel *sRateLabel = new QLabel("Sample rate:");
    sRateLabel->setAlignment(Qt::AlignRight);
    
    // user can choose between 44.1 and 48kHz
    sRateBox = new QComboBox();
    sRateBox->addItem("44100");
    sRateBox->addItem("48000");
    sRateBox->setCurrentIndex(1);
    
    // add device and sr widgets to local layout
    deviceLayout->addWidget(deviceBox);
    deviceLayout->addWidget(sRateLabel);
    deviceLayout->addWidget(sRateBox);
    
    // add device layout to main layout
    layout->addLayout(deviceLayout);
    
    // DetectorBank parameters layout 
    // two rows of three parameters
    // (including QLabels, the grid should tbe 2x6)
    QGridLayout *detBankParamLayout = new QGridLayout();
    
    // label and textedit for each
    
    QLabel *bandwidthLabel = new QLabel("Bandwidth (cents):");
    QLabel *dampingLabel = new QLabel("Damping:");
    QLabel *gainLabel = new QLabel("Gain:");
    QLabel *edoLabel = new QLabel("EDO:");
    QLabel *lwrLabel = new QLabel("Lower note:");
    QLabel *uprLabel = new QLabel("Upper note:");
    
    bandwidthEdit = new QLineEdit("0");
    dampingEdit = new QLineEdit("0.0001");
    gainEdit = new QLineEdit("25");
    edoEdit = new QLineEdit("12");
    lwrEdit = new QLineEdit("A3");
    uprEdit = new QLineEdit("A5");
    
    QVector<QLabel*> detBankParamLabels = {bandwidthLabel, dampingLabel, gainLabel, 
                                          edoLabel, lwrLabel, uprLabel} ;
    QVector<QLineEdit*> detBankParamEdits = {bandwidthEdit, dampingEdit, gainEdit, 
                                         edoEdit, lwrEdit, uprEdit} ;
    
    // fill first row of labels and edits                                      
    int row {0};
    int widgetNum {0};
    
    for (int i{0}; i<3; i++) {
        detBankParamLayout->addWidget(detBankParamLabels[i], row, widgetNum);
        widgetNum++;
        detBankParamLayout->addWidget(detBankParamEdits[i], row, widgetNum);
        widgetNum++;
    }
    
    // fill second row of labels and edits   
    row++;
    widgetNum = 0;
    for (int i{3}; i<detBankParamLabels.size(); i++) {
        detBankParamLayout->addWidget(detBankParamLabels[i], row, widgetNum);
        widgetNum++;
        detBankParamLayout->addWidget(detBankParamEdits[i], row, widgetNum);
        widgetNum++;
    }
    
    // align all labels to the right
    for (int i{0}; i<detBankParamLabels.size(); i++) {
        detBankParamLabels[i]->setAlignment(Qt::AlignRight);
    }
    
    // button to make DetectorBank and start visualisation
    row++;
    startButton = new QPushButton("Start!");
    connect(startButton, SIGNAL(clicked()), this, SLOT(start()));
    detBankParamLayout->addWidget(startButton, row, 5, Qt::AlignRight);
    
    // add grid of detbank params (and start button) to main layout
    layout->addLayout(detBankParamLayout);
    
    
    // volume slider
//     volumeSlider = new QSlider(Qt::Horizontal, this);
//     volumeSlider->setRange(0, 100);
//     volumeSlider->setValue(100);
//     connect(volumeSlider, &QSlider::valueChanged, this, &Visualizer::sliderChanged);
//     layout->addWidget(volumeSlider);
// 
//     modeButton = new QPushButton(this);
//     connect(modeButton, &QPushButton::clicked, this, &Visualizer::toggleMode);
//     layout->addWidget(modeButton);

    

    window->setLayout(layout);

    setCentralWidget(window);
    window->show();
}

void Visualizer::initializeAudio(const QAudioDeviceInfo &deviceInfo)
{
    const int sr_int = getSampleRateInt();
    setBufLen(static_cast<int>(getSampleRateDbl() * 0.04)); // 40ms buffer
    
    QAudioFormat format;
    format.setSampleRate(sr_int);
    format.setChannelCount(1);
    format.setSampleSize(32);
    format.setSampleType(QAudioFormat::Float);
    format.setByteOrder(QAudioFormat::LittleEndian); // is this right? and/or is it necessary?
    format.setCodec("audio/pcm");

    if (!deviceInfo.isFormatSupported(format)) {
        qWarning() << "Default format not supported - trying to use nearest";
        format = deviceInfo.nearestFormat(format);
    }

    audioDevice.reset(new AudioDevice(format));

    audioInput.reset(new QAudioInput(deviceInfo, format));
    qreal initialVolume = QAudio::convertVolume(audioInput->volume(),
                                                QAudio::LinearVolumeScale,
                                                QAudio::LogarithmicVolumeScale);

    audioBuffer.reset(new QAudioBuffer(getBufLen(), format));
    
    audioProbe.reset(new QAudioProbe(this));
    
    if (audioProbe->setSource(audioInput)) {
        connect(audioProbe, SIGNAL(audioBufferProbed(*audioBuffer)), this,
                SLOT(getDetBankData(audioBuffer)));
    }
    
    audioDevice->start();
}

void Visualizer::start()
{
    std::cout << "Initialsing audio..\n";
    initializeAudio(QAudioDeviceInfo::defaultInputDevice());
    std::cout << "Making DetectorBank\n";
    makeDetectorBank();
    std::cout << "Making PlotData object\n";
    plotData.reset(new PlotData());
    std::cout << "Opening PlotData window\n";
    plotData->show();
    
    std::cout << "Starting audio\n";
    startAudio();
//     connect(&timer, &QTimer::timeout, this, plotData->update());
//     timer.setInterval(30);
//     timer.start();
}

void Visualizer::startAudio()
{
//     audioInput->stop();
//     toggleSuspend();

    // Change bewteen pull and push modes
//     if (pullMode) {
//         modeButton->setText(tr("Enable push mode"));
//         audioInput->start(audioDevice.data());
//     } else {
//         modeButton->setText(tr("Enable pull mode"));
    
    // push mode
    auto io = audioInput->start();
    connect(io, &QIODevice::readyRead,
        [&, io]() {
            qint64 len = audioInput->bytesReady();
//             const int BufferSize = static_cast<int>(0.03 * getSampleRateDbl()); 
            if (len > buflen)
                len = buflen;

            QByteArray buffer(len, 0);
            qint64 l = io->read(buffer.data(), len);
            if (l > 0)
                audioDevice->write(buffer.constData(), l);
        });
//     }
//     pullMode = !pullMode;
}

void Visualizer::getDetBankData(QAudioBuffer buffer)
{
    QAudioBuffer::S32F *data = audioBuffer->constData<QAudioBuffer::S32F>();
    float monoData[buflen];
    if (buflen != audioBuffer.frameCount()) {
        std::cout << "buflen != audioBuffer.frameCount()\n";
        std::cout << "buflen = " << buflen << ", frameCount = " << audioBuffer.frameCount() << "\n";
    }
        
    // get left channel 
    for (int i{0}; i<buflen; i++) 
        monoData[i] = data[i].left;
}

void Visualizer::deviceChanged(int index)
{
    audioDevice->stop();
    audioInput->stop();
    audioInput->disconnect(this);

    initializeAudio(deviceBox->itemData(index).value<QAudioDeviceInfo>());
}

void Visualizer::sliderChanged(int value)
{
    qreal linearVolume = QAudio::convertVolume(value / qreal(100),
                                               QAudio::LogarithmicVolumeScale,
                                               QAudio::LinearVolumeScale);

    audioInput->setVolume(linearVolume);
}

int Visualizer::getNoteNum(QString name, const double EDO=12)
{
    // TODO update so that EDO values other than 12 work
//     std::cout << "getNoteNum('" << name.toStdString() << "') = "; 
    name = name.toLower();
    const QList<QString> pitches  = {"c", "c#","d", "d#", "e", "f", "f#", "g", "g#", 
                                     "a", "a#", "b"};
                               
    // get pitch class, octave number and alter (i.e. sharp or flat) from `name`
    const QString pitch_class {name.left(1)};
    const int octave {name.right(1).toInt()};
    
    QString alter;
    if (name.size() == 3)
        alter = name.mid(1, 1); // from index 1, get 1 character
    else
        alter = "";
    
    // find number of notes between A4 and given 
    
    // number of notes between given octave and fourth octave
    int octave_diff {4-octave};
    octave_diff *= EDO;
    
    // position of pitch in pitches list
    int pitch_idx = pitches.indexOf(pitch_class);
    // position of A in pitches list
    int a_idx = pitches.indexOf("a");
    // number of chromatic steps between given pitch class and A
    int pitch_diff = a_idx-pitch_idx;
    
    // find total chromatic steps between given and A4
//     int note_num {A4 - (octave_diff + pitch_diff)};
    int note_num {-(octave_diff + pitch_diff)};
    
    // adjust if given note was sharp or flat
    if (alter == "b")
        note_num--;
    else if (alter == "#")
        note_num++;
    
//     std::cout << note_num << "\n";
    
    return note_num;
}

double Visualizer::centsToHz(const double f0, const double cents, const double EDO=12)
{
    // Work out the difference in Hertz between f0 and f0+cents/2 (i.e. upper half)
    // and double it, as we want to be centred on f0 
    double h_cents {cents/200.};
    double semitone {std::pow(2, (1/EDO))};
    return 2*f0*h_cents*(semitone-1);    
}

void Visualizer::makeDetectorBank()
{    
    // get values from GUI
    const double sr_dbl = getSampleRateDbl();
    const double bandwidth_cents {bandwidthEdit->text().toDouble()};
    const double dmp {dampingEdit->text().toDouble()};
    const double gain {gainEdit->text().toDouble()};
    const double edo {edoEdit->text().toDouble()};
    const int lwr {getNoteNum(lwrEdit->text(), edo)};
    const int upr {getNoteNum(uprEdit->text(), edo) + 1}; // include upr 
    
    // calculate detector frequencies
    double freq[upr-lwr];
    for (int i {0}; i<upr-lwr; i++) {
        double k = static_cast<double>(lwr+i);
        freq[i] = 440. * std::pow(2, (k/edo));
    }
    
    // make empty array for bandwidths
    const std::size_t len = sizeof(freq)/sizeof(freq[0]);
    double bw[len];
    
    // if minimum bandwidth detectors have been requested, fill with zeros
    if (bandwidth_cents == 0.) {
        std::fill_n(bw, len, 0.);
    }
    // otherwise calculate B in Hz from the given value in cents
    else {
        for (std::size_t i{0}; i<len; i++) {
            bw[i]  = centsToHz(freq[i], bandwidth_cents, edo);
        }
    }
    
    // empty input buffer to initialise DetectorBank
    const float buffer[] = {0.};
    const std::size_t bufLen {1};
    
    db.reset(new DetectorBank(sr_dbl, buffer, bufLen, 0, freq, bw, len,
                              static_cast<DetectorBank::Features>(
                                DetectorBank::Features::runge_kutta|
                                DetectorBank::Features::freq_unnormalized|
                                DetectorBank::Features::amp_unnormalized), 
                              dmp, gain));  
    
    std::cout << "Made DetectorBank with " << db->getChans() << " channels ";
    std::cout << "and sample rate of " << db->getSR() << "Hz\n";
}

int Visualizer::getSampleRateInt()
{
    int sr; 
    int srIdx { sRateBox->currentIndex() };
    
    if (srIdx==0)
        sr = 44100;
    else if (srIdx==1)
        sr = 48000;
    else
        throw std::invalid_argument("Sample rate should be 44100 or 48000.");
    return sr;
}

double Visualizer::getSampleRateDbl()
{
    double sr;
    int srIdx { sRateBox->currentIndex() };
    
    if (srIdx==0)
        sr = 44100.;
    else if (srIdx==1)
        sr = 48000.;
    else
        throw std::invalid_argument("Sample rate should be 44100 or 48000.");
    return sr;
}

void Visualizer::getBufLen()
{
    return buflen;
}

int Visualizer::setBufLen(int newBuflen)
{
    buflen = newBuflen;
}
