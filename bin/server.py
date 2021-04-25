# Copyright (C) 2021 Dmitry Ivanko. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Module contains web application. """

import os
import pty
import signal
import sys
import uuid
from pathlib import Path

import psutil
import tornado.web
from tornado import gen
from shirow.ioloop import IOLoop
from shirow.server import RPCServer, TOKEN_PATTERN, remote

from gis.codes import (
    READY,
    IMAGE_MISSING,
    KERNEL_CONFIGURATOR_COULD_NOT_BE_PREPARED,
    KERNEL_CONFIGURATOR_TERMINATED,
    KERNEL_CONFIGURATOR_THEME_DOES_NOT_EXIST,
)
from gis import defaults
from gis.db import Image
from gis.docker import CHECK_RUNNING_CONFIGURATION_ATTEMPTS, PORT
from gis.exceptions import ImageDoesNotExist, KernelConfigFileDoesNotExist


class Application(tornado.web.Application):
    """Tornado web application. """

    def __init__(self):
        handlers = [
            (r'/gis/token/' + TOKEN_PATTERN, GiS),
        ]

        super().__init__(handlers)


class GiS(RPCServer):
    """Class contains remote procedures. """

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)

        self._file_desc = None
        self._image = None
        self._script_process = None
        self._config_name = str(uuid.uuid4())
        self._configurator_theme = defaults.KERNEL_CONFIGURATOR_THEMES[0]

    def destroy(self):
        if self._file_desc:
            self.io_loop.remove_handler(self._file_desc)
            try:
                self.logger.debug('Closing %s', self._file_desc)
                os.close(self._file_desc)
            except OSError as exc:
                self.logger.error('An error occurred when attempting to close %s: %s',
                                  self._file_desc, exc)

        if self._script_process and psutil.pid_exists(self._script_process.pid):
            pid = self._script_process.pid
            try:
                self.logger.debug('Killing script process %s', pid)
                os.kill(pid, signal.SIGKILL)
            except OSError as exc:
                self.logger.error('An error occurred when attempting to kill %s: %s', pid, exc)

        try:
            self._image.save_kernel_config(self._config_name)
        except KernelConfigFileDoesNotExist:
            self.logger.error('Not found kernel config file(%s)', self._config_name)

    @remote
    async def init_new_kernel_configuration(self, request, image_id):
        """Try to get current image. """

        try:
            self._image = Image(image_id=image_id)
        except ImageDoesNotExist:
            request.ret_error(IMAGE_MISSING)

        request.ret(READY)

    @remote
    async def start(self, request):
        """Run pts process with kernel configurator. """

        request.ret_and_continue('The kernel configurator will be started in a few seconds...\r\n')

        pid, file_desc = pty.fork()
        self._file_desc = file_desc

        if pid == 0:  # child process
            cmd = [
                'run-configuration.sh',
                str(os.path.join(defaults.BASE_CONFIG_FILES_DIR, f'.{self._config_name}')),
                self._configurator_theme,
            ]
            env = {
                'PATH': f"{os.environ['PATH']}:{defaults.BASE_DIR}",
                'TERM': 'xterm',
            }

            os.execvpe(cmd[0], cmd, env)
        else:  # parent process
            self.logger.debug('kernel configurator started with pid %s', pid)

            self._script_process = psutil.Process(pid)
            for _ in range(CHECK_RUNNING_CONFIGURATION_ATTEMPTS):
                if psutil.pid_exists(pid):
                    break
                await gen.sleep(1)
            else:
                request.ret_error(KERNEL_CONFIGURATOR_COULD_NOT_BE_PREPARED)

            def callback(*_args, **_kwargs):
                # There can be the Input/output error if the process was
                # terminated unexpectedly.
                try:
                    buf = os.read(self._file_desc, 65536)
                except OSError:
                    self.destroy()
                    request.ret(KERNEL_CONFIGURATOR_TERMINATED)

                request.ret_and_continue(buf.decode('utf8', errors='replace'))

            self.io_loop.add_handler(self._file_desc, callback, self.io_loop.READ)

    @remote
    async def enter(self, request, data):
        """Receives and send data to kernel configurator. """

        try:
            os.write(self._file_desc, data.encode('utf8'))
        except (IOError, OSError):
            self.destroy()
            request.ret(KERNEL_CONFIGURATOR_TERMINATED)

    @remote
    async def get_configurator_themes(self, request):
        """Returns available kernel configurator themes. """

        request.ret(defaults.KERNEL_CONFIGURATOR_THEMES)

    @remote
    async def set_configurator_theme(self, request, theme):
        """Set current kernel configurator theme. """

        if theme in defaults.KERNEL_CONFIGURATOR_THEMES:
            self._configurator_theme = theme
            request.ret(READY)
        else:
            request.ret(KERNEL_CONFIGURATOR_THEME_DOES_NOT_EXIST)


def main():
    """Running Tornado web application. """

    if os.getuid() != 0:
        sys.stderr.write('{} must run as root\n'.format(sys.argv[0]))
        sys.exit(1)

    Path(defaults.BASE_CONFIG_FILES_DIR).mkdir(exist_ok=True)

    tornado.options.parse_command_line()
    IOLoop().start(Application(), PORT)


if __name__ == "__main__":
    main()
