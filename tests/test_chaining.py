'''
Test the ability of the TrixyInput, TrixyProcessor, and TrixyOutput
classes to chain together.
'''
import asyncore
import socket
import trixy
from tests import utils
from tests.utils import SRV_HOST, SRV_PORT, LOC_HOST, LOC_PORT


class TestChainingDummyOutput(trixy.TrixyOutput):

    def handle_packet_down(self, data):
        self.forward_packet_up(data)


class TestChainingDummyInput(trixy.TrixyInput):
    def __init__(self, sock, addr):
        super().__init__(sock, addr)

        processor = trixy.TrixyProcessor()
        self.connect_node(processor)

        # Create output, but tell it not to autoconnect. LOC_HOST and LOC_PORT
        #   are just used as place-holders because a connection is never made.
        output = TestChainingDummyOutput(LOC_HOST, LOC_PORT, autoconnect=False)
        processor.connect_node(output)


class TestChaining(utils.TestCase):
    def setUp(self):
        super().setUp()
        self.server = trixy.TrixyServer(TestChainingDummyInput, SRV_HOST, SRV_PORT)

    def tearDown(self):
        super().tearDown()
        self.server.close()
        del self.server

    def test_input_output_via_roundtrip(self):
        '''
        Test that data can flow all the way through the chain to the
        output and then back.
        '''
        sock = socket.socket()
        sock.connect((SRV_HOST, SRV_PORT))

        sock.send(b'hello world')
        self.assertEqual(sock.recv(32), b'hello world')

        sock.close()
