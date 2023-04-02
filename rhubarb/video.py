import subprocess as sp
import json

class VideoOut:
    def __init__(self, size: tuple[int, int], fps: float, path: str) -> None:
        cmd = (
            "ffmpeg",
            "-loglevel",    "warning",
            "-y",
            "-s",           "%ix%i" % size,
            "-r",           str(fps),
            "-f",           "rawvideo",
            "-pix_fmt",     "rgb24",
            "-i",           "-",
            "-codec:v",     "mpeg4",
            "-qscale:v",    "1",
            path
        )

        self.pipe = sp.Popen(cmd, stdin=sp.PIPE)

    # def __del__(self) -> None:
    #     self.pipe.terminate()

    def write(self, data: bytes) -> None:
        self.pipe.stdin.write(data)

class VideoIn:
    def __init__(self, path: str) -> None:
        # get video metadata
        cmd = ("ffprobe", "-show_streams", "-of", "json", path)
        metadata, _ = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE).communicate()
        metadata = json.loads(metadata)["streams"][0]

        self.path = path
        self.num_frames = int(metadata["nb_frames"])
        self.size = metadata["width"], metadata["height"]
        self.bufsize = self.size[0] * self.size[1] * 3
        
        self.init()

    def init(self):
        """call init to start from begining of video again"""
        cmd = (
            "ffmpeg",
            "-i",           self.path,
            "-f",           "image2pipe",
            "-pix_fmt",     "rgb24",
            "-codec:v",     "rawvideo",
            "-"
        )

        self.pipe = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE)

        self.frame_id = 0
        
    def __del__(self) -> None:
        self.pipe.terminate()

    def read(self) -> bytes:
        if self.frame_id >= self.num_frames:
            self.pipe.terminate()
            self.init()

        self.frame_id += 1

        return self.pipe.stdout.read(self.bufsize)
    