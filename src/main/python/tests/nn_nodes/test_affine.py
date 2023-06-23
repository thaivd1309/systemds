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

from systemds.operator.nn_nodes.affine import Affine

dim = 6
n = 10
m = 5
np.random.seed(11)
X = np.random.rand(n, dim)

np.random.seed(10)
W = np.random.rand(dim, m)
b = np.random.rand(m)


class TestAffine(unittest.TestCase):
    sds: SystemDSContext = None

    @classmethod
    def setUpClass(cls):
        cls.sds = SystemDSContext()

    @classmethod
    def tearDownClass(cls):
        cls.sds.close()

    def test_affine(self):
        Xm = self.sds.from_numpy(X)
        Wm = self.sds.from_numpy(W)
        bm = self.sds.from_numpy(b)

        affine = Affine(dim, m, 10)
        out = affine.forward(Xm)
        print(out.compute())
        print(out.script_str)
        dout = self.sds.from_numpy(np.random.rand(n, m))
        dX, dW, db = affine.backward(dout)
        assert True


if __name__ == '__main__':
    unittest.main()
