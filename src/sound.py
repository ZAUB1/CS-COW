def SoundWin(sound):
    from ctypes import c_buffer, windll;
    from random import random;
    from time import sleep;
    from sys import getfilesystemencoding;

    def WinCommand(*command):
        buf = c_buffer(255);
        command = ' '.join(command).encode(getfilesystemencoding());
        errorCode = int(windll.winmm.mciSendStringA(command, buf, 254, 0));

        if errorCode:
            errorBuffer = c_buffer(255);
            windll.winmm.mciGetErrorStringA(errorCode, errorBuffer, 254);
            print("Oskour");

        return buf.value

    alias = 'playsound_' + str(random());
    WinCommand('open "' + sound + '" alias', alias);
    WinCommand('set', alias, 'time format milliseconds');
    durationInMS = WinCommand('status', alias, 'length');
    WinCommand('play', alias, 'from 0 to', durationInMS.decode());

    sleep((float(durationInMS) + 500.0) / 1000.0);

def SoundLinux(sound):
    import os;
    from urllib.request import pathname2url;
    import gi;

    gi.require_version('Gst', '1.0');
    from gi.repository import Gst;

    Gst.init(None);

    playbin = Gst.ElementFactory.make('playbin', 'playbin');

    playbin.props.uri = 'file://' + pathname2url(os.path.abspath(sound));

    set_result = playbin.set_state(Gst.State.PLAYING);

    bus = playbin.get_bus();
    bus.poll(Gst.MessageType.EOS, Gst.CLOCK_TIME_NONE);
    playbin.set_state(Gst.State.NULL);

from platform import system;
system = system();

if system == 'Windows':
    playsound = SoundWin;
else:
    playsound = SoundLinux;