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

"""Module contains methods for working with the database. """

import os

from gis import defaults
from gis.exceptions import ImageDoesNotExist, KernelConfigFileDoesNotExist
from images.models import Image as ImageModel   # pylint: disable=wrong-import-order,import-error


class Image:
    """Class representing an image. """

    def __init__(self, image_id):
        self._image = None
        self.image_id = image_id

        try:
            self._image = ImageModel.objects.get(image_id=image_id)
        except ImageModel.DoesNotExist as exc:
            raise ImageDoesNotExist from exc

    @staticmethod
    def _serialize_props(props):
        """Serialize props while saving data. """

        for prop_key, prop_value in props.items():
            if isinstance(prop_value, bool):
                props[prop_key] = str(prop_value).lower()

    def save_kernel_config(self, config_name):
        """Saving config file to field props in Image model. """

        config_path = os.path.join(defaults.BASE_CONFIG_FILES_DIR, f'.{config_name}')
        if not os.path.exists(config_path):
            raise KernelConfigFileDoesNotExist

        with open(config_path) as file:
            kernel_config = file.read()

        props = self._image.props
        props.update({
            'PIEMAN_KERNEL_CONFIG': kernel_config,
        })
        self._serialize_props(props)

        self._image.props = props
        self._image.save()
