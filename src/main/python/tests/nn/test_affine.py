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
from numpy.testing import assert_almost_equal

from systemds.context import SystemDSContext
from systemds.script_building.script import DMLScript
from systemds.operator.nn.affine import Affine

dim = 6
n = 5
m = 6
X = np.array([[9., 2., 5., 5., 9., 6.],
              [0., 8., 8., 0., 5., 7.],
              [2., 2., 6., 3., 4., 3.],
              [3., 5., 2., 6., 6., 0.],
              [3., 8., 5., 2., 5., 2.]])

W = np.array([[8., 3., 7., 2., 0., 1.],
              [6., 5., 1., 2., 6., 1.],
              [2., 4., 7., 7., 6., 4.],
              [3., 8., 9., 3., 5., 6.],
              [3., 8., 0., 5., 7., 9.],
              [7., 9., 7., 4., 5., 7.]])
dout = np.array([[9., 5., 4., 0., 4., 1.],
                 [1., 2., 2., 3., 3., 9.],
                 [7., 4., 0., 8., 7., 0.],
                 [8., 7., 0., 6., 0., 9.],
                 [1., 6., 5., 8., 8., 9.]])


class TestAffine(unittest.TestCase):
    sds: SystemDSContext = None

    @classmethod
    def setUpClass(cls):
        cls.sds = SystemDSContext()

    @classmethod
    def tearDownClass(cls):
        cls.sds.close()

    def test_init(self):
        affine = Affine(self.sds, dim, m, 10)
        w = affine.weight.compute()
        self.assertEqual(len(w), 6)
        self.assertEqual(len(w[0]), 6)

    def test_forward(self):
        Xm = self.sds.from_numpy(X)
        Wm = self.sds.from_numpy(W)
        bm = self.sds.full((1, 6), 0)

        # test class method
        affine = Affine(self.sds, dim, m, 10)
        out = affine.forward(Xm).compute()
        self.assertEqual(len(out), 5)
        self.assertEqual(len(out[0]), 6)

        # test static method
        out = Affine.forward(Xm, Wm, bm).compute()
        expected = np.matmul(X, W)
        assert_almost_equal(out, expected)

    def test_backward(self):
        Xm = self.sds.from_numpy(X)
        Wm = self.sds.from_numpy(W)
        bm = self.sds.full((1, 6), 0)
        doutm = self.sds.from_numpy(dout)

        # test class method
        affine = Affine(self.sds, dim, m, 10)
        [dx, dw, db] = affine.backward(doutm, Xm).compute()
        assert len(dx) == 5 and len(dx[0]) == 6
        assert len(dw) == 6 and len(dx[0]) == 6
        assert len(db) == 1 and len(db[0]) == 6

        # test static method
        res = Affine.backward(doutm, Xm, Wm, bm).compute()
        assert len(res) == 3

    def test_multiple_sourcing(self):
        a1 = Affine(self.sds, dim, m, 10)
        a2 = Affine(self.sds, m, 11, 10)

        Xm = self.sds.from_numpy(X)
        X1 = a1.forward(Xm)
        X2 = a2.forward(X1)

        scripts = DMLScript(self.sds)
        scripts.build_code(X2)

        self.assertEqual(1, self.count_sourcing(scripts.dml_script, layer_name="affine"))

    def test_multiple_context(self):
        # two context
        sds1 = SystemDSContext()
        sds2 = SystemDSContext()
        a1 = Affine(sds1, dim, m, 10)
        a2 = Affine(sds2, m, 11, 10)

        Xm = sds1.from_numpy(X)
        X1 = a1.forward(Xm)
        out_actual = a2.forward(X1).compute()

        # one context
        Xm = self.sds.from_numpy(X)
        a1 = Affine(self.sds, dim, m, 10)
        a2 = Affine(self.sds, m, 11, 10)

        X1 = a1.forward(Xm)
        out_expected = a2.forward(X1).compute()

        assert_almost_equal(out_actual, out_expected)

        sds1.close()
        sds2.close()

    def count_sourcing(self, script: str, layer_name: str):
        """
        Count the number of times the dml script is being sourced
        i.e. count the number of occurrences of lines like
        'source(...) as affine' in the dml script

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
