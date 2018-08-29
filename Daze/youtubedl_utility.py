from __future__ import unicode_literals
import os
import youtube_dl


class YoutubeDLLogger(object):
    def debug(self, msg):
        print(msg)

    def warning(self, msg):
        print(msg)

    def error(self, msg):
        print(msg)


YOUTUBEDL_OPTS = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'logger': YoutubeDLLogger()
}


class YoutubeDLUtility(object):
    def __init__(self, link, dest_dir):
        '''
        Initialize utility class
        @param link: link provided by user
        @param dest_dir: destination directory where downloaded audio files
                         will be put
        '''
        self.link = link
        self.dest_dir = dest_dir
        self._filename = ''
        self.dest_file = '{}/%(title)s.%(ext)s'.format(self.dest_dir)
        self.options = {'progress_hooks': [self.progress_hook],
                        'outtmpl': self.output}
        self.options.update(YOUTUBEDL_OPTS)
        self.download_and_convert()

    def download_and_convert(self):
        '''
        Download and convert audio from specified link
        '''
        with youtube_dl.YoutubeDL(self.options) as ydl:
            ydl.download([self.link])

    def progress_hook(self, audio_metadata):
        '''
        Hooks that get called during download action to provide additional
        metadata
        @param audio_metadata: dictionary containing metadata about the audio
                               file
        '''
        if audio_metadata.get('eta') is not None:
            print('Estimated time of completiton: ', audio_metadata['eta'])

        if audio_metadata['status'] == 'finished':
            print('Done downloading, now converting ...')
            self.filename = audio_metadata['filename']

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, value):
        self._filename = '{}{}'.format(os.path.splitext(value)[0], '.mp3')

    @property
    def name(self):
        '''
        Return the name of the audio file parsing out the directory it's
        nested in
        '''
        return os.path.basename(os.path.splitext(self.filename)[0])

    @property
    def metadata(self):
        return {'filename': self.filename}

