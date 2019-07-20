#include <stdlib.h>
#include <math.h>
#include <stdexcept>

#include <Qt>

#include <QDateTime>
#include <QDebug>
#include <QPainter>
#include <QHBoxLayout>
#include <QVBoxLayout>
#include <QGridLayout>
#include <QPushButton>
#include <QLineEdit>
#include <QAudioDeviceInfo>
#include <QAudioInput>
#include <QLabel>
#include <qendian.h>
#include <QVector>
#include <QString>

#include "audioinput.h"
#include "detectorbank.h"

// TODO: fill short buffer with audio data, send to DetectorBank, call getZ
// plot DetectorBank complex responses

AudioInfo::AudioInfo(const QAudioFormat &format)
    : format(format)
{
    switch (format.sampleSize()) {
    case 8:
        switch (format.sampleType()) {
        case QAudioFormat::UnSignedInt:
            maxAmplitude = 255;
            break;
        case QAudioFormat::SignedInt:
            maxAmplitude = 127;
            break;
        default:
            break;
        }
        break;
    case 16:
        switch (format.sampleType()) {
        case QAudioFormat::UnSignedInt:
            maxAmplitude = 65535;
            break;
        case QAudioFormat::SignedInt:
            maxAmplitude = 32767;
            break;
        default:
            break;
        }
        break;

    case 32:
        switch (format.sampleType()) {
        case QAudioFormat::UnSignedInt:
            maxAmplitude = 0xffffffff;
            break;
        case QAudioFormat::SignedInt:
            maxAmplitude = 0x7fffffff;
            break;
        case QAudioFormat::Float:
            maxAmplitude = 0x7fffffff; // Kind of
        default:
            break;
        }
        break;

    default:
        break;
    }
}

void AudioInfo::start()
{
    open(QIODevice::WriteOnly);
}

void AudioInfo::stop()
{
    close();
}

qint64 AudioInfo::readData(char *data, qint64 maxlen)
{
    Q_UNUSED(data)
    Q_UNUSED(maxlen)

    return 0;
}

qint64 AudioInfo::writeData(const char *data, qint64 len)
{
    if (maxAmplitude) {
        Q_ASSERT(format.sampleSize() % 8 == 0);
        const int channelBytes = format.sampleSize() / 8;
        const int sampleBytes = format.channelCount() * channelBytes;
        Q_ASSERT(len % sampleBytes == 0);
        const int numSamples = len / sampleBytes;

        quint32 maxValue = 0;
        const unsigned char *ptr = reinterpret_cast<const unsigned char *>(data);

        for (int i = 0; i < numSamples; ++i) {
            for (int j = 0; j < format.channelCount(); ++j) {
                quint32 value = 0;

                if (format.sampleSize() == 8 && format.sampleType() == QAudioFormat::UnSignedInt) {
                    value = *reinterpret_cast<const quint8*>(ptr);
                } else if (format.sampleSize() == 8 && format.sampleType() == QAudioFormat::SignedInt) {
                    value = qAbs(*reinterpret_cast<const qint8*>(ptr));
                } else if (format.sampleSize() == 16 && format.sampleType() == QAudioFormat::UnSignedInt) {
                    if (format.byteOrder() == QAudioFormat::LittleEndian)
                        value = qFromLittleEndian<quint16>(ptr);
                    else
                        value = qFromBigEndian<quint16>(ptr);
                } else if (format.sampleSize() == 16 && format.sampleType() == QAudioFormat::SignedInt) {
                    if (format.byteOrder() == QAudioFormat::LittleEndian)
                        value = qAbs(qFromLittleEndian<qint16>(ptr));
                    else
                        value = qAbs(qFromBigEndian<qint16>(ptr));
                } else if (format.sampleSize() == 32 && format.sampleType() == QAudioFormat::UnSignedInt) {
                    if (format.byteOrder() == QAudioFormat::LittleEndian)
                        value = qFromLittleEndian<quint32>(ptr);
                    else
                        value = qFromBigEndian<quint32>(ptr);
                } else if (format.sampleSize() == 32 && format.sampleType() == QAudioFormat::SignedInt) {
                    if (format.byteOrder() == QAudioFormat::LittleEndian)
                        value = qAbs(qFromLittleEndian<qint32>(ptr));
                    else
                        value = qAbs(qFromBigEndian<qint32>(ptr));
                } else if (format.sampleSize() == 32 && format.sampleType() == QAudioFormat::Float) {
                    value = qAbs(*reinterpret_cast<const float*>(ptr) * 0x7fffffff); // assumes 0-1.0
                }

                maxValue = qMax(value, maxValue);
                ptr += channelBytes;
            }
        }

        maxValue = qMin(maxValue, maxAmplitude);
        level = qreal(maxValue) / maxAmplitude;
    }

    emit update();
    return len;
}

RenderArea::RenderArea(QWidget *parent)
    : QWidget(parent)
{
    setBackgroundRole(QPalette::Base);
    setAutoFillBackground(true);

    setMinimumHeight(30);
    setMinimumWidth(200);
}

void RenderArea::paintEvent(QPaintEvent * /* event */)
{
    QPainter painter(this);

    painter.setPen(Qt::black);
    painter.drawRect(QRect(painter.viewport().left()+10,
                           painter.viewport().top()+10,
                           painter.viewport().right()-20,
                           painter.viewport().bottom()-20));
    if (level == 0.0)
        return;

    int pos = ((painter.viewport().right()-20)-(painter.viewport().left()+11))*level;
    painter.fillRect(painter.viewport().left()+11,
                     painter.viewport().top()+10,
                     pos,
                     painter.viewport().height()-21,
                     Qt::red);
}

void RenderArea::setLevel(qreal value)
{
    level = value;
    update();
}


InputTest::InputTest()
{
    initializeWindow();
    initializeAudio(QAudioDeviceInfo::defaultInputDevice());
//     makeDetectorBank();
}


void InputTest::initializeWindow()
{
    QWidget *window = new QWidget;
    QVBoxLayout *layout = new QVBoxLayout;

    canvas = new RenderArea(this);
    layout->addWidget(canvas);
    
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
            &InputTest::deviceChanged);
    
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
    connect(startButton, SIGNAL(clicked()), this, SLOT(makeDetectorBank()));
    detBankParamLayout->addWidget(startButton, row, 5, Qt::AlignRight);
    
    // add grid of detbank params (and start button) to main layout
    layout->addLayout(detBankParamLayout);
    
    
    // volume slider
//     volumeSlider = new QSlider(Qt::Horizontal, this);
//     volumeSlider->setRange(0, 100);
//     volumeSlider->setValue(100);
//     connect(volumeSlider, &QSlider::valueChanged, this, &InputTest::sliderChanged);
//     layout->addWidget(volumeSlider);
// 
//     modeButton = new QPushButton(this);
//     connect(modeButton, &QPushButton::clicked, this, &InputTest::toggleMode);
//     layout->addWidget(modeButton);

    

    window->setLayout(layout);

    setCentralWidget(window);
    window->show();
}

void InputTest::initializeAudio(const QAudioDeviceInfo &deviceInfo)
{
    const int sr_int = getSampleRateInt();
    QAudioFormat format;
    format.setSampleRate(sr_int);
    format.setChannelCount(1);
    format.setSampleSize(16);
    format.setSampleType(QAudioFormat::SignedInt);
    format.setByteOrder(QAudioFormat::LittleEndian);
    format.setCodec("audio/pcm");

    if (!deviceInfo.isFormatSupported(format)) {
        qWarning() << "Default format not supported - trying to use nearest";
        format = deviceInfo.nearestFormat(format);
    }

    audioInfo.reset(new AudioInfo(format));
    connect(audioInfo.data(), &AudioInfo::update, [this]() {
        canvas->setLevel(audioInfo->getLevel());
    });

    audioInput.reset(new QAudioInput(deviceInfo, format));
    qreal initialVolume = QAudio::convertVolume(audioInput->volume(),
                                                QAudio::LinearVolumeScale,
                                                QAudio::LogarithmicVolumeScale);
//     volumeSlider->setValue(qRound(initialVolume * 100));
    audioInfo->start();
    toggleMode();
}

void InputTest::toggleMode()
{
    audioInput->stop();
//     toggleSuspend();

    // Change bewteen pull and push modes
    if (pullMode) {
//         modeButton->setText(tr("Enable push mode"));
        audioInput->start(audioInfo.data());
    } else {
//         modeButton->setText(tr("Enable pull mode"));
        auto io = audioInput->start();
        connect(io, &QIODevice::readyRead,
            [&, io]() {
                qint64 len = audioInput->bytesReady();
                const int BufferSize = 4096;
                if (len > BufferSize)
                    len = BufferSize;

                QByteArray buffer(len, 0);
                qint64 l = io->read(buffer.data(), len);
                if (l > 0)
                    audioInfo->write(buffer.constData(), l);
            });
    }

    pullMode = !pullMode;
}

// void InputTest::toggleSuspend()
// {
//     toggle suspend/resume
//     if (audioInput->state() == QAudio::SuspendedState || audioInput->state() == QAudio::StoppedState) {
//         audioInput->resume();
//         suspendResumeButton->setText(tr("Suspend recording"));
//     } else if (audioInput->state() == QAudio::ActiveState) {
//         audioInput->suspend();
//         suspendResumeButton->setText(tr("Resume recording"));
//     } else if (audioInput->state() == QAudio::IdleState) {
//         no-op
//     }
// }

void InputTest::deviceChanged(int index)
{
    audioInfo->stop();
    audioInput->stop();
    audioInput->disconnect(this);

    initializeAudio(deviceBox->itemData(index).value<QAudioDeviceInfo>());
}

void InputTest::sliderChanged(int value)
{
    qreal linearVolume = QAudio::convertVolume(value / qreal(100),
                                               QAudio::LogarithmicVolumeScale,
                                               QAudio::LinearVolumeScale);

    audioInput->setVolume(linearVolume);
}

void InputTest::makeDetectorBank()
{    
    const double sr_dbl = getSampleRateDbl();
    // TODO method to convert cents to Hz for bandwidth
    const double bandwidth {bandwidthEdit->text().toDouble()};
    const double dmp {dampingEdit->text().toDouble()};
    const double gain {gainEdit->text().toDouble()};
    const float buffer[] = {0.};
    const std::size_t bufLen {1};
    
    const double edo {edoEdit->text().toDouble()};
    // TODO method to take note name and convert to number relative to A4
    const int lwr {-12};
    const int upr {13};
    
    double freq[upr-lwr];
    for (int i {0}; i<upr-lwr; i++) {
        double k = static_cast<double>(lwr+i);
        freq[i] = 440. * std::pow(2, (k/edo));
    }
    
    const std::size_t len = sizeof(freq)/sizeof(freq[0]);
    double bw[len];
    std::fill_n(bw, len, bandwidth); 
    
    db.reset(new DetectorBank(sr_dbl, buffer, bufLen, 0, freq, bw, len,
                              static_cast<DetectorBank::Features>(
                                DetectorBank::Features::runge_kutta|
                                DetectorBank::Features::freq_unnormalized|
                                DetectorBank::Features::amp_unnormalized), 
                              dmp, gain));  
    
    std::cout << "Made DetectorBank with " << db->getChans() << " channels ";
    std::cout << "and sample rate of " << db->getSR() << "Hz\n";
}

int InputTest::getSampleRateInt()
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

double InputTest::getSampleRateDbl()
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
