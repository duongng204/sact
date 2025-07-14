#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: SDuongR
# GNU Radio version: 3.10.11.0

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from PyQt5.QtCore import QObject, pyqtSlot
from gnuradio import analog
from gnuradio import audio
from gnuradio import blocks
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import iio
import sip
import threading



class nbfm_rcvr(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "SDuongR", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("SDuongR")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "nbfm_rcvr")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables
        ##################################################
        self.volume = volume = 0.3
        self.tuning = tuning = 94000000
        self.sq_lvl = sq_lvl = -50
        self.samp_rate = samp_rate = 1920000
        self.rf_decim = rf_decim = 5
        self.interp = interp = 1
        self.deviation = deviation = 25000
        self.audio_decim = audio_decim = 8

        ##################################################
        # Blocks
        ##################################################

        # Create the options list
        self._tuning_options = [94000000, 102700000, 91000000, 99900000]
        # Create the labels list
        self._tuning_labels = ['VOV1: 94.0 MHz', 'VOV3: 102.7 MHz', 'Giao thong: 91.0 MHz', 'VOH: 99.9 MHz']
        # Create the combo box
        self._tuning_tool_bar = Qt.QToolBar(self)
        self._tuning_tool_bar.addWidget(Qt.QLabel("station" + ": "))
        self._tuning_combo_box = Qt.QComboBox()
        self._tuning_tool_bar.addWidget(self._tuning_combo_box)
        for _label in self._tuning_labels: self._tuning_combo_box.addItem(_label)
        self._tuning_callback = lambda i: Qt.QMetaObject.invokeMethod(self._tuning_combo_box, "setCurrentIndex", Qt.Q_ARG("int", self._tuning_options.index(i)))
        self._tuning_callback(self.tuning)
        self._tuning_combo_box.currentIndexChanged.connect(
            lambda i: self.set_tuning(self._tuning_options[i]))
        # Create the radio buttons
        self.top_layout.addWidget(self._tuning_tool_bar)
        self._volume_range = qtgui.Range(0, 1, 0.05, 0.3, 200)
        self._volume_win = qtgui.RangeWidget(self._volume_range, self.set_volume, "Volume", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._volume_win)
        self._sq_lvl_range = qtgui.Range(-100, 0, 5, -50, 200)
        self._sq_lvl_win = qtgui.RangeWidget(self._sq_lvl_range, self.set_sq_lvl, "Squelch", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._sq_lvl_win)
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=5,
                decimation=1,
                taps=[],
                fractional_bw=0)
        self.qtgui_sink_x_0 = qtgui.sink_c(
            4096, #fftsize
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "", #name
            True, #plotfreq
            True, #plotwaterfall
            True, #plottime
            True, #plotconst
            None # parent
        )
        self.qtgui_sink_x_0.set_update_time(1.0/10)
        self._qtgui_sink_x_0_win = sip.wrapinstance(self.qtgui_sink_x_0.qwidget(), Qt.QWidget)

        self.qtgui_sink_x_0.enable_rf_freq(False)

        self.top_layout.addWidget(self._qtgui_sink_x_0_win)
        self.iio_pluto_source_0 = iio.fmcomms2_source_fc32('usb:2.4.5' if 'usb:2.4.5' else iio.get_pluto_uri(), [True, True], 0x4000)
        self.iio_pluto_source_0.set_len_tag_key('packet_len')
        self.iio_pluto_source_0.set_frequency(tuning)
        self.iio_pluto_source_0.set_samplerate(samp_rate)
        self.iio_pluto_source_0.set_gain_mode(0, 'fast_attack')
        self.iio_pluto_source_0.set_gain(0, 64)
        self.iio_pluto_source_0.set_quadrature(True)
        self.iio_pluto_source_0.set_rfdc(True)
        self.iio_pluto_source_0.set_bbdc(True)
        self.iio_pluto_source_0.set_filter_params('Auto', '', 0, 0)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_ff(0.3)
        self.audio_sink_0 = audio.sink(48000, 'plughw:CARD=AudioPCI,DEV=0', True)
        self.analog_simple_squelch_cc_0 = analog.simple_squelch_cc((-50), 1)
        self.analog_fm_demod_cf_0 = analog.fm_demod_cf(
        	channel_rate=(samp_rate/rf_decim),
        	audio_decim=audio_decim,
        	deviation=deviation,
        	audio_pass=16000,
        	audio_stop=20000,
        	gain=1.0,
        	tau=(75e-6),
        )


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_fm_demod_cf_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.analog_simple_squelch_cc_0, 0), (self.analog_fm_demod_cf_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.audio_sink_0, 0))
        self.connect((self.iio_pluto_source_0, 0), (self.qtgui_sink_x_0, 0))
        self.connect((self.iio_pluto_source_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.analog_simple_squelch_cc_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "nbfm_rcvr")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_volume(self):
        return self.volume

    def set_volume(self, volume):
        self.volume = volume

    def get_tuning(self):
        return self.tuning

    def set_tuning(self, tuning):
        self.tuning = tuning
        self._tuning_callback(self.tuning)
        self.iio_pluto_source_0.set_frequency(self.tuning)

    def get_sq_lvl(self):
        return self.sq_lvl

    def set_sq_lvl(self, sq_lvl):
        self.sq_lvl = sq_lvl

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.iio_pluto_source_0.set_samplerate(self.samp_rate)
        self.qtgui_sink_x_0.set_frequency_range(0, self.samp_rate)

    def get_rf_decim(self):
        return self.rf_decim

    def set_rf_decim(self, rf_decim):
        self.rf_decim = rf_decim

    def get_interp(self):
        return self.interp

    def set_interp(self, interp):
        self.interp = interp

    def get_deviation(self):
        return self.deviation

    def set_deviation(self, deviation):
        self.deviation = deviation

    def get_audio_decim(self):
        return self.audio_decim

    def set_audio_decim(self, audio_decim):
        self.audio_decim = audio_decim




def main(top_block_cls=nbfm_rcvr, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()


    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
