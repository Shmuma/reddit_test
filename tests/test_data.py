import unittest

from lib import data


class TestData(unittest.TestCase):
    def test_images_simple(self):
        self.assertTrue(data.is_image_url("http://i.imgur.com/hr3jA.jpg"))
        self.assertTrue(data.is_image_url("http://i.imgur.com/hr3jA.Jpeg"))

    def test_images_weirdo(self):
        self.assertTrue(data.is_image_url("http://i.imgur.com/hr3jA.jpg[/IMG]"))

    def test_parse(self):
        r = data.parse_input_line('[something is wrong]')
        self.assertIsNone(r)

        r = data.parse_input_line('["reddit.com","kelly brooks","http://www.hollyhotty.com/?p=1837","/r/reddit.com/comments/eut3e/kelly_brooks/","t3_eut3e"]')
        self.assertIsNotNone(r)
        self.assertEqual("reddit.com", r[0])
        self.assertEqual("kelly brooks", r[1])
        self.assertEqual("http://www.hollyhotty.com/?p=1837", r[2])
