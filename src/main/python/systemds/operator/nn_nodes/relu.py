# -------------------------------------------------------------
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
# -------------------------------------------------------------
import os.path

from systemds.context import SystemDSContext
from systemds.operator import Matrix, Source
from systemds.utils.helpers import get_path_to_script_layers


class ReLU:
    _sds_context: SystemDSContext
    _source: Source
    _X: Matrix

    def __init__(self):
        self._sds_context = SystemDSContext()
        path = get_path_to_script_layers()
        path = os.path.join(path, "relu.dml")
        self._source = self._sds_context.source(path, "relu")

    def forward(self, X):
        """
        X: input matrix
        return out: output matrix
        """
        self._X = X
        out = self._source.forward(X)
        return out

    def backward(self, dout):
        """
        dout: gradient of output, passed from the upstream
        return dX: gradient of input
        """
        dX = self._source.backward(dout, self._X)
        return dX
