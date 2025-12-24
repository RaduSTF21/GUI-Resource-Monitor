import unittest
import os
from utils import get_size,format_log_line, append_to_file

class TestResourceMonitor(unittest.TestCase):
    def test_get_size(self):
        self.assertEqual(get_size(100),"100.00B")
        self.assertEqual(get_size(1024),"1.00KB")
        self.assertEqual(get_size(2048),"2.00KB")
        self.assertEqual(get_size(1048576),"1.00MB")

    def test_format_log_line(self):
        result = format_log_line(25.5,60.2, 1000,500,1024,2048)
        self.assertIn("25.5",result)
        self.assertIn("60.2",result)
        self.assertIn("1000",result)
        self.assertTrue(result.endswith("\n"))
        self.assertIn(",",result)

    def test_append_to_file(self):
        nume_fis_test = "test_temp.txt"
        if os.path.exists(nume_fis_test):
            os.remove(nume_fis_test)
        success = append_to_file(nume_fis_test,"Linie de test \n")
        self.assertTrue(success)

        with open(nume_fis_test,"r") as f:
            line = f.read()
        self.assertEqual(line,"Linie de test \n")
        os.remove(nume_fis_test)

if __name__ == '__main__':
    unittest.main()