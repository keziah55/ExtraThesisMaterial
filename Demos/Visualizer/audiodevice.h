#ifndef AUDIODEVICE_H
#define AUDIODEVICE_H

#include <QIODevice>
#include <QAudioFormat>

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


#endif
