import unittest
import pressure_mat_posture as pmp
import numpy as np

class Pressure_Mat_Posture_Test(unittest.TestCase):

    #make sure mat data can be accessed
    def test_load_mat_data(self):
        self.assertIsInstance(np.load("./Testing/hands.npy"), np.ndarray)

    #make sure there are only 2 clusters
    def test_k_means(self):
        hands_array = np.load("./Testing/hands.npy")
        kmeans, coords_only = pmp.run_kmeans(hands_array)

        self.assertEquals(len(kmeans.cluster_centers_), 2)

    #make sure can create a mat data with empty values
    def test_create_mat_zeros(self):
        m = np.zeros(shape=(3,3), dtype=float)

        self.assertIsInstance(m, np.ndarray)

    def test_create_mat_1x3(self):
        m = np.array([1.0, 2.0, 3.0])

        self.assertIsInstance(m, np.ndarray)

    #make sure can create a 2d mat
    def test_create_mat_3x3(self):
        m = np.array([[1.0, 1.0, 1.0], [2.0, 2.0, 2.0], [3.0,3.0,3.0]])

        self.assertIsInstance(m, np.ndarray)

    #make sure can find 2 clusters with a simple 2d mat
    def test_kmeans(self):
        m = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 1.0], [0.0,0.0,0.0]])
        kmeans, coords_only = pmp.run_kmeans(m, 2, 3, 3)

        self.assertEquals(len(kmeans.cluster_centers_), 2)

    #make sure can find and separate 2 UNORDERED hands with a simple 2d mat
    def test_isolate_hands_unordered(self):
        m = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 2.0], [0.0,0.0,0.0]])
        kmeans, coords_only = pmp.run_kmeans(m, 2, 3, 3)
        h1, h2 = pmp.isolate_hands(m, kmeans, coords_only)

        #merge hand dictionaries
        rl = dict()
        rl.update(h1)
        rl.update(h2)
    
        self.assertDictEqual(rl, {(1,2): 2.0, (1,0): 1.0})

    def test_isolate_hands_ordered(self):
        m = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 2.0], [0.0,0.0,0.0]])
        kmeans, coords_only = pmp.run_kmeans(m, 2, 3, 3)
        h1, h2 = pmp.isolate_hands(m, kmeans, coords_only)
        actual_rcop, actual_lcop, ideal_cop, actual_cop, r, l = pmp.generate_cops(h1, h2)

        self.assertEquals(r.get((1, 2)), 2.0)
        self.assertEquals(l.get((1, 0)), 1.0)

    #make sure the basic cop calculation function works
    def test_calculate_cop(self):
        weighted_coords = dict()
        weighted_coords[(1.0, 2.0)] = 2.0
        weighted_coords[(1.0, 0.0)] = 1.0

        unweighted_coords = dict()
        unweighted_coords[(1.0, 2.0)] = 1.0
        unweighted_coords[(1.0, 0.0)] = 1.0

        self.assertEquals(pmp.calculate_cop(weighted_coords),[1.0, 4.0/3.0])
        self.assertEquals(pmp.calculate_cop(unweighted_coords), [1.0, 1.0])

    #make sure it's doing all the calculations properly on a simple mat example
    def test_cop_calculations(self):
        m = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 2.0], [0.0,0.0,0.0]])
        kmeans, coords_only = pmp.run_kmeans(m, 2, 3, 3)
        h1, h2 = pmp.isolate_hands(m, kmeans, coords_only)
        actual_rcop, actual_lcop, ideal_cop, actual_cop, r, l = pmp.generate_cops(h1, h2)

        self.assertEquals(actual_rcop, [1.0, 2.0])
        self.assertEquals(actual_lcop, [1.0, 0.0])
        self.assertEquals(actual_cop, [1.0, 4.0/3.0])
        self.assertEquals(ideal_cop, [1.0, 1.0])

    #probably doesn't need to be a test but w/e
    def test_create_actuators(self):
        a = pmp.create_actuator_dict()
        test_a = dict()
        test_a['i'] = False #index
        test_a['p'] = False #pinky
        test_a['w'] = False #wrist
        test_a['t'] = False #thumb

        self.assertIsInstance(a, dict)
        self.assertEquals(a, test_a)

    #make sure the basic vector calculation function works
    def test_create_vector(self):
        t1 = [1.0, 4.0/3.0]
        t2 = [1.0, 1.0]
        tv = [0.0, 0.0]
        tv[0] = t2[0] - t1[0]
        tv[1] = t2[1] - t1[1]

        self.assertEquals(pmp.create_vector(t1, t2), (tv[0], tv[1]))

    #make sure the vector is calculated properly using a simple mat example
    def test_vector(self):
        m = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 2.0], [0.0,0.0,0.0]])
        kmeans, coords_only = pmp.run_kmeans(m, 2, 3, 3)
        h1, h2 = pmp.isolate_hands(m, kmeans, coords_only)
        actual_rcop, actual_lcop, ideal_cop, actual_cop, r, l = pmp.generate_cops(h1, h2)
        vector = pmp.create_vector(actual_cop, ideal_cop)

        t1 = [1.0, 4.0/3.0]
        t2 = [1.0, 1.0]
        tv = [0.0, 0.0]
        tv[0] = t2[0] - t1[0]
        tv[1] = t2[1] - t1[1]

        self.assertEquals(vector, (tv[0], tv[1]))

    #make sure the actuators are selected properly using a simple mat example
    def test_select_actuators(self):
        m = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 2.0], [0.0,0.0,0.0]])
        kmeans, coords_only = pmp.run_kmeans(m, 2, 3, 3)
        h1, h2 = pmp.isolate_hands(m, kmeans, coords_only)
        actual_rcop, actual_lcop, ideal_cop, actual_cop, r, l = pmp.generate_cops(h1, h2)
        vector = pmp.create_vector(actual_cop, ideal_cop)
        actuators = pmp.create_actuator_dict()
        actuators = pmp.select_actuators(vector, actuators)

        self.assertFalse(actuators['i'])
        self.assertTrue(actuators['t'])
        self.assertTrue(actuators['w'])
        self.assertFalse(actuators['p'])


if __name__ == '__main__':
    unittest.main()