import os
from datetime import datetime


class FileWriter:

    def __init__(self, *,
        filepath:str=None,
        outobj=None,
        no_out:bool=False,
        flush_each:bool=False,
        no_flush:bool=False,
        clear_exist:bool=False,
        make_dir:bool=True,
    ):
        
        if not no_out and not filepath and not outobj:
            raise RuntimeError('No output specified. If no output, set argument `no_out` to True.')
        
        self.filepath = filepath
        self.outobj = outobj
        self.no_out = no_out
        self.flush_each = flush_each
        self.no_flush = no_flush
        self.buffer = ''
        self.once_flashed = False
        self.clear_exist = clear_exist
        self.make_dir = make_dir


    # write with line feed
    def write(self, *contents:str):
        self.write_raw(''.join([content + '\n' for content in contents]))
        return self


    def write_raw(self, content:str):
        self.buffer += content
        if self.flush_each: self.flush()
        return self


    def flush(self):
        if not self.no_flush: self._flush()
        return self


    def _flush(self):
        if self.no_out or not self.buffer: return
        
        if self.outobj:
            print(self.buffer, file=self.outobj, end='')

        if self.filepath:
            if not self.once_flashed:
                if self.make_dir: prepare_directory(self.filepath)
                mode = 'w' if self.clear_exist else 'a'
            else:
                mode = 'a'

            with open(self.filepath, mode=mode) as f:
                print(self.buffer, file=f, end='')

        self.buffer = ''
        self.once_flashed = True


    def __del__(self):
        self._flush()



# def current_time_text() -> str:
#     return datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")


def prepare_directory(path:str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)


