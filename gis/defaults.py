# Copyright (C) 2020 Dmitry Ivanko. All Rights Reserved.
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

"""Module containing default variables. """

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BASE_CONFIG_FILES_DIR = f'{BASE_DIR}/config_files'

KERNEL_CONFIGURATOR_THEMES = [
    'bluetitle',  # a LCD friendly version of classic. (default)
    'mono',  # selects colors suitable for monochrome displays
    'blackbg',  # selects a color scheme with black background
    'classic',  # theme with blue background. The classic look
]
