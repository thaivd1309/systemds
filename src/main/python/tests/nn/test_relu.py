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

import unittest

import numpy as np

from systemds.context import SystemDSContext
from systemds.script_building.script import DMLScript
from systemds.operator.nn.relu import ReLU


class TestRelu(unittest.TestCase):
    sds: SystemDSContext = None

    @classmethod
    def setUpClass(cls):
        cls.sds = SystemDSContext()
        cls.X = np.array([0, -1, -2, 2, 3, -5])
        cls.dout = np.array([0, 1, 2, 3, 4, 5])

    @classmethod
    def tearDownClass(cls):
        cls.sds.close()

    def test_forward(self):
        relu = ReLU(self.sds)
        # forward
        Xm = self.sds.from_numpy(self.X)
        out = relu.forward(Xm).compute().flatten()
        expected = np.array([0, 0, 0, 2, 3, 0])
        self.assertTrue(np.allclose(out, expected))

        # test static
        sout = ReLU.forward(Xm).compute().flatten()
        self.assertTrue(np.allclose(sout, expected))

    def test_backward(self):
        relu = ReLU(self.sds)
        # forward
        Xm = self.sds.from_numpy(self.X)
        out = relu.forward(Xm)
        # backward
        doutm = self.sds.from_numpy(self.dout)
        dx = relu.backward(doutm).compute().flatten()
        expected = np.array([0, 0, 0, 3, 4, 0], dtype=np.double)
        self.assertTrue(np.allclose(dx, expected))

        # test static
        sdx = ReLU.backward(doutm, Xm).compute().flatten()
        self.assertTrue(np.allclose(sdx, expected))

    def test_multiple_sourcing(self):
        r1 = ReLU(self.sds)
        r2 = ReLU(self.sds)

        Xm = self.sds.from_numpy(self.X)
        X1 = r1.forward(Xm)
        X2 = r2.forward(X1)

        scripts = DMLScript(self.sds)
        scripts.build_code(X2)

        self.assertEqual(1,self.count_sourcing(scripts.dml_script, layer_name="relu"))

    def count_sourcing(self, script: str, layer_name: str):
        """
        Count the number of times the dml script is being sourced
        i.e. count the number of occurrences of lines like
        'source(...) as relu' in the dml script

        :param script: the sourced dml script text
        :param layer_name: example: "affine", "relu"
        :return:
        """
        return len([
            line for line in script.split("\n")
            if all([line.startswith("source"), line.endswith(layer_name)])
        ])


if __name__ == '__main__':
    unittest.main()
