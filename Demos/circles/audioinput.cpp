#include <stdlib.h>
#include <math.h>

#include <QDateTime>
#include <QDebug>
#include <QPainter>
#include <QHBoxLayout>
#include <QVBoxLayout>
#include <QPushButton>
#include <QAudioDeviceInfo>
#include <QAudioInput>
#include <QSize>
#include <QLabel>
#include <qendian.h>

#include "audioinput.h"
#include "detectorbank.h"

// TODO: fill short buffer with audio data, send to DetectorBank, call getZ
// plot DetectorBank complex responses

AudioInfo::AudioInfo(const QAudioFormat &format)
    : m_format(format)
{
    switch (m_format.sampleSize()) {
    case 8:
        switch (m_format.sampleType()) {
        case QAudioFormat::UnSignedInt:
            m_maxAmplitude = 255;
            break;
        case QAudioFormat::SignedInt:
            m_maxAmplitude = 127;
            break;
        default:
            break;
        }
        break;
    case 16:
        switch (m_format.sampleType()) {
        case QAudioFormat::UnSignedInt:
            m_maxAmplitude = 65535;
            break;
        case QAudioFormat::SignedInt:
            m_maxAmplitude = 32767;
            break;
        default:
            break;
        }
        break;

    case 32:
        switch (m_format.sampleType()) {
        case QAudioFormat::UnSignedInt:
            m_maxAmplitude = 0xffffffff;
            break;
        case QAudioFormat::SignedInt:
            m_maxAmplitude = 0x7fffffff;
            break;
        case QAudioFormat::Float:
            m_maxAmplitude = 0x7fffffff; // Kind of
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
    if (m_maxAmplitude) {
        Q_ASSERT(m_format.sampleSize() % 8 == 0);
        const int channelBytes = m_format.sampleSize() / 8;
        const int sampleBytes = m_format.channelCount() * channelBytes;
        Q_ASSERT(len % sampleBytes == 0);
        const int numSamples = len / sampleBytes;

        quint32 maxValue = 0;
        const unsigned char *ptr = reinterpret_cast<const unsigned char *>(data);

        for (int i = 0; i < numSamples; ++i) {
            for (int j = 0; j < m_format.channelCount(); ++j) {
                quint32 value = 0;

                if (m_format.sampleSize() == 8 && m_format.sampleType() == QAudioFormat::UnSignedInt) {
                    value = *reinterpret_cast<const quint8*>(ptr);
                } else if (m_format.sampleSize() == 8 && m_format.sampleType() == QAudioFormat::SignedInt) {
                    value = qAbs(*reinterpret_cast<const qint8*>(ptr));
                } else if (m_format.sampleSize() == 16 && m_format.sampleType() == QAudioFormat::UnSignedInt) {
                    if (m_format.byteOrder() == QAudioFormat::LittleEndian)
                        value = qFromLittleEndian<quint16>(ptr);
                    else
                        value = qFromBigEndian<quint16>(ptr);
                } else if (m_format.sampleSize() == 16 && m_format.sampleType() == QAudioFormat::SignedInt) {
                    if (m_format.byteOrder() == QAudioFormat::LittleEndian)
                        value = qAbs(qFromLittleEndian<qint16>(ptr));
                    else
                        value = qAbs(qFromBigEndian<qint16>(ptr));
                } else if (m_format.sampleSize() == 32 && m_format.sampleType() == QAudioFormat::UnSignedInt) {
                    if (m_format.byteOrder() == QAudioFormat::LittleEndian)
                        value = qFromLittleEndian<quint32>(ptr);
                    else
                        value = qFromBigEndian<quint32>(ptr);
                } else if (m_format.sampleSize() == 32 && m_format.sampleType() == QAudioFormat::SignedInt) {
                    if (m_format.byteOrder() == QAudioFormat::LittleEndian)
                        value = qAbs(qFromLittleEndian<qint32>(ptr));
                    else
                        value = qAbs(qFromBigEndian<qint32>(ptr));
                } else if (m_format.sampleSize() == 32 && m_format.sampleType() == QAudioFormat::Float) {
                    value = qAbs(*reinterpret_cast<const float*>(ptr) * 0x7fffffff); // assumes 0-1.0
                }

                maxValue = qMax(value, maxValue);
                ptr += channelBytes;
            }
        }

        maxValue = qMin(maxValue, m_maxAmplitude);
        m_level = qreal(maxValue) / m_maxAmplitude;
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
    if (m_level == 0.0)
        return;

    int pos = ((painter.viewport().right()-20)-(painter.viewport().left()+11))*m_level;
    painter.fillRect(painter.viewport().left()+11,
                     painter.viewport().top()+10,
                     pos,
                     painter.viewport().height()-21,
                     Qt::red);
}

void RenderArea::setLevel(qreal value)
{
    m_level = value;
    update();
}


InputTest::InputTest(const int sr)
  : sr(sr)
{
    initializeWindow();
    initializeAudio(QAudioDeviceInfo::defaultInputDevice());
    makeDetectorBank();
}


void InputTest::initializeWindow()
{
    QWidget *window = new QWidget;
    QVBoxLayout *layout = new QVBoxLayout;

    m_canvas = new RenderArea(this);
    layout->addWidget(m_canvas);
    
    // layout for audio device and sample rate selection
    QHBoxLayout *deviceLayout = new QHBoxLayout;

    // make audio device selection box
    m_deviceBox = new QComboBox(this);
    const QAudioDeviceInfo &defaultDeviceInfo = QAudioDeviceInfo::defaultInputDevice();
    m_deviceBox->addItem(defaultDeviceInfo.deviceName(), 
                         qVariantFromValue(defaultDeviceInfo));
    for (auto &deviceInfo: QAudioDeviceInfo::availableDevices(QAudio::AudioInput)) {
        if (deviceInfo != defaultDeviceInfo) {
            m_deviceBox->addItem(deviceInfo.deviceName(), 
                                 qVariantFromValue(deviceInfo));
        }
    }

    connect(m_deviceBox, QOverload<int>::of(&QComboBox::activated), this, 
            &InputTest::deviceChanged);
    
    // make sample rate label and textedit
    QLabel *m_sRateLabel = new QLabel("Sample rate:");
    
    // user can choose between 44.1 and 48kHz
    m_sRateBox = new QComboBox();
    m_sRateBox->addItem("44100");
    m_sRateBox->addItem("48000");
    m_sRateBox->setCurrentIndex(1);
    
    // add device and sr widgets to local layout
    deviceLayout->addWidget(m_deviceBox);
    deviceLayout->addWidget(m_sRateLabel);
    deviceLayout->addWidget(m_sRateBox);
    
    // add device layout to main layout
    layout->addLayout(deviceLayout);

    
    // volume slider
    m_volumeSlider = new QSlider(Qt::Horizontal, this);
    m_volumeSlider->setRange(0, 100);
    m_volumeSlider->setValue(100);
    connect(m_volumeSlider, &QSlider::valueChanged, this, &InputTest::sliderChanged);
    layout->addWidget(m_volumeSlider);

    m_modeButton = new QPushButton(this);
    connect(m_modeButton, &QPushButton::clicked, this, &InputTest::toggleMode);
    layout->addWidget(m_modeButton);

    

    window->setLayout(layout);

    setCentralWidget(window);
    window->show();
}

void InputTest::initializeAudio(const QAudioDeviceInfo &deviceInfo)
{
    QAudioFormat format;
    format.setSampleRate(sr);
    format.setChannelCount(1);
    format.setSampleSize(16);
    format.setSampleType(QAudioFormat::SignedInt);
    format.setByteOrder(QAudioFormat::LittleEndian);
    format.setCodec("audio/pcm");

    if (!deviceInfo.isFormatSupported(format)) {
        qWarning() << "Default format not supported - trying to use nearest";
        format = deviceInfo.nearestFormat(format);
    }

    m_audioInfo.reset(new AudioInfo(format));
    connect(m_audioInfo.data(), &AudioInfo::update, [this]() {
        m_canvas->setLevel(m_audioInfo->level());
    });

    m_audioInput.reset(new QAudioInput(deviceInfo, format));
    qreal initialVolume = QAudio::convertVolume(m_audioInput->volume(),
                                                QAudio::LinearVolumeScale,
                                                QAudio::LogarithmicVolumeScale);
    m_volumeSlider->setValue(qRound(initialVolume * 100));
    m_audioInfo->start();
    toggleMode();
}

void InputTest::toggleMode()
{
    m_audioInput->stop();
//     toggleSuspend();

    // Change bewteen pull and push modes
    if (m_pullMode) {
        m_modeButton->setText(tr("Enable push mode"));
        m_audioInput->start(m_audioInfo.data());
    } else {
        m_modeButton->setText(tr("Enable pull mode"));
        auto io = m_audioInput->start();
        connect(io, &QIODevice::readyRead,
            [&, io]() {
                qint64 len = m_audioInput->bytesReady();
                const int BufferSize = 4096;
                if (len > BufferSize)
                    len = BufferSize;

                QByteArray buffer(len, 0);
                qint64 l = io->read(buffer.data(), len);
                if (l > 0)
                    m_audioInfo->write(buffer.constData(), l);
            });
    }

    m_pullMode = !m_pullMode;
}

// void InputTest::toggleSuspend()
// {
//     toggle suspend/resume
//     if (m_audioInput->state() == QAudio::SuspendedState || m_audioInput->state() == QAudio::StoppedState) {
//         m_audioInput->resume();
//         m_suspendResumeButton->setText(tr("Suspend recording"));
//     } else if (m_audioInput->state() == QAudio::ActiveState) {
//         m_audioInput->suspend();
//         m_suspendResumeButton->setText(tr("Resume recording"));
//     } else if (m_audioInput->state() == QAudio::IdleState) {
//         no-op
//     }
// }

void InputTest::deviceChanged(int index)
{
    m_audioInfo->stop();
    m_audioInput->stop();
    m_audioInput->disconnect(this);

    initializeAudio(m_deviceBox->itemData(index).value<QAudioDeviceInfo>());
}

void InputTest::sliderChanged(int value)
{
    qreal linearVolume = QAudio::convertVolume(value / qreal(100),
                                               QAudio::LogarithmicVolumeScale,
                                               QAudio::LinearVolumeScale);

    m_audioInput->setVolume(linearVolume);
}

void InputTest::makeDetectorBank()
{
    const double sr_dbl = static_cast<double>(sr);
    const double bandwidth {0};
    const double dmp {0.0001};
    const double gain {5.};
    const float buffer[] = {0.};
    const std::size_t bufLen {1};
    
    const double edo {12.};
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
    
    std::cout << "Made DetectorBank with " << db->getChans() << " channels\n";
    
    
}
