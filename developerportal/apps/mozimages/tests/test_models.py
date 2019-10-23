from django.test import TestCase

from developerportal.apps.mozimages.models import MozImage


class MozImageTests(TestCase):
    def test_extract_suffix(self):
        cases = (
            ("example.jpg", ".", ".jpg"),
            ("example.file.jpeg", ".", ".jpeg"),
            ("example.jpg", None, ".jpg"),
            ("example.file.png", None, ".png"),
            ("example_file", ".", ""),
            ("example_tiff", "_", "_tiff"),
        )
        image = MozImage()

        for input_, delimiter, expected in cases:
            with self.subTest(input_=input_, delimiter=delimiter, expected=expected):
                if delimiter:
                    self.assertEqual(
                        image._extract_suffix(filename=input_, delimiter=delimiter),
                        expected,
                    )
                else:
                    self.assertEqual(image._extract_suffix(filename=input_), expected)

    def test_get_image_upload_to(self):
        image = MozImage()
        cases = (
            ("example.jpg", "original_images/f3b0002ea58a851a514fec772d8ab7eb.jpg"),
            ("Amélie.png", "original_images/b464cdb73f309351707ec74dd36867ca.png"),
        )

        for input_, expected_result in cases:
            with self.subTest(input_=input_, expected_result=expected_result):
                upload_to = image.get_upload_to(input_)
                self.assertEqual(upload_to, expected_result)

        # This test also acts as a canary, implicitly checking that `original_images`
        #  is still what Wagtail is using internally
