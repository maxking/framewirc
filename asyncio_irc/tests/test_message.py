from itertools import product
from unittest import TestCase

from ..message import build_message, ReceivedMessage


class TestReceivedMessage(TestCase):
    """Test the ReceivedMessage class."""
    def build_message(self, prefix, params, suffix):
        raw_message = b'COMMAND'
        if prefix:
            raw_message = b':prefixed-data ' + raw_message
        if params:
            raw_message += b' param1 param2'
        if suffix:
            raw_message += b' :suffix message'

        return raw_message

    def test_permutations(self):
        """
        Make sure that Message attributes are set correctly.

        Checks every combination of a prefix, params, and suffix data.
        """
        on_off = True, False
        for prefix, params, suffix in product(on_off, on_off, on_off):
            with self.subTest(prefix=prefix, params=params, suffix=suffix):
                raw_message = self.build_message(prefix, params, suffix)

                message = ReceivedMessage(raw_message)

                expected_prefix = 'prefixed-data' if prefix else ''
                expected_params = ('param1', 'param2') if params else ()
                expected_suffix = 'suffix message' if suffix else ''

                self.assertEqual(message.command, 'COMMAND')
                self.assertEqual(message.prefix, expected_prefix)
                self.assertEqual(message.params, expected_params)
                self.assertEqual(message.suffix, expected_suffix)


class TestBuildMessage(TestCase):
    """Make sure that build_message correctly builds bytes objects."""
    def test_basic(self):
        """Simple command only."""
        message = build_message(b'COMMAND')
        self.assertEqual(message, b'COMMAND\r\n')

    def test_prefix(self):
        """Command with prefix."""
        message = build_message(b'COMMAND', prefix=b'something')
        self.assertEqual(message, b':something COMMAND\r\n')

    def test_params(self):
        """Command with params."""
        message = build_message(b'COMMAND', b'param1', b'param2')
        self.assertEqual(message, b'COMMAND param1 param2\r\n')

    def test_suffix(self):
        """Command with suffix."""
        message = build_message(b'COMMAND', suffix=b'suffix ftw!')
        self.assertEqual(message, b'COMMAND :suffix ftw!\r\n')

    def test_all(self):
        """Command with prefix, params, and suffix."""
        message = build_message(
            b'COMMAND',
            b'param1',
            b'param2',
            prefix=b'something',
            suffix=b'suffix ftw!',
        )
        expected = b':something COMMAND param1 param2 :suffix ftw!\r\n'
        self.assertEqual(message, expected)

    def test_unicode(self):
        """
        Make sure build_message works when passed strings.

        No valid commands contain unicode chars, so not bothering with ♬ in it.
        """
        message = build_message(
            'COMMAND',
            'tést',
            'test',
            prefix='mμ',
            suffix='ftẃ!',
        )
        expected = b':m\xce\xbc COMMAND t\xc3\xa9st test :ft\xe1\xba\x83!\r\n'
        self.assertEqual(message, expected)
