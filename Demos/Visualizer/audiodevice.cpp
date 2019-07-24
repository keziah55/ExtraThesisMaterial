#include "audiodevice.h"

#include <qendian.h>

// This class is mostly taken from the AudioInput example
AudioDevice::AudioDevice(const QAudioFormat &format)
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

void AudioDevice::start()
{
    open(QIODevice::ReadWrite);
}

void AudioDevice::stop()
{
    close();
}

qint64 AudioDevice::readData(char *data, qint64 maxlen)
{
    Q_UNUSED(data)
    Q_UNUSED(maxlen)

    return 0;
}

qint64 AudioDevice::writeData(const char *data, qint64 len)
{
    if (maxAmplitude) {
        
        Q_ASSERT(format.sampleSize() % 8 == 0);
        const int channelBytes = format.sampleSize() / 8;
        const int sampleBytes = format.channelCount() * channelBytes;
        Q_ASSERT(len % sampleBytes == 0);
        const int numSamples = len / sampleBytes;
        
        audioBuffer.reset(new float[numSamples]);

//         quint32 maxValue = 0;
        const unsigned char *ptr = reinterpret_cast<const unsigned char *>(data);

        for (int i = 0; i < numSamples; ++i) {
            
            // if multiple channels, take the max at  each sample
            quint32 maxValue = 0;
            
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
            // put value in audioBuffer
            audioBuffer[i] = maxValue;
        }

//         maxValue = qMin(maxValue, maxAmplitude);
//         level = qreal(maxValue) / maxAmplitude;
    }

    emit update();
    return len;
}

