from datetime import timedelta
import pickle
import math
import re

class Features:
    class BWindow:
        pktsCount = 101
        pktsCount_SR_ratio = 102

        interArrivalTimeMean = 103

        packetSizeSum = 104
        packetSizeSum_SR_ratio = 105
        packetSizeMean = 106
        packetSizeStd = 107
        packetSizeRange = 108

        ALL = [
            pktsCount, pktsCount_SR_ratio,
            interArrivalTimeMean,
            packetSizeSum,
            packetSizeSum_SR_ratio, packetSizeMean, packetSizeStd, packetSizeRange
        ]
        DEFAULT = [
            pktsCount, pktsCount_SR_ratio,
            interArrivalTimeMean,
            packetSizeSum_SR_ratio, packetSizeMean, packetSizeStd, packetSizeRange
	]

    class Flow:
        pktsCount = 201
        interArrivalTimeStd = 202
        packetSizeStd = 203

        ALL = [pktsCount, interArrivalTimeStd, packetSizeStd]
        DEFAULT = []

    class CWindow:
        pktsCount = 301
        packetSizeSum = 302
        flowsCount = 303
        hostsCount = 304

        ALL = [pktsCount, packetSizeSum, flowsCount, hostsCount]
        DEFAULT = []

class CompactedPacket:
    def __init__(self, time, size, to_outside):
        self.time = time
        self.size = size
        self.to_outside = to_outside

    @staticmethod
    def fromPacket(packet, to_outside):
        return CompactedPacket(packet.time, packet.data_len, to_outside)

class DataStructure:
    # ONE FOR THE WHOLE DATASET
    # WILL KEEP TRACK OF EACH USER INVOLVED
    def __init__(self, intranetPattern, w1, w2):
        self.intranetPattern = re.compile(r"{}".format(intranetPattern))
        self.w1 = w1
        self.w2 = w2
        self.hosts = {}

    def add_packet(self, packet):
        if self.intranetPattern.match(packet.ip_src):
            self.get_window_container(packet.ip_src).add_packet(
                c_packet = CompactedPacket.fromPacket(packet, to_outside = True),
                port = packet.src_port,
                other_host = packet.get_host(who = 'dst')
            )
        if self.intranetPattern.match(packet.ip_dst):
            self.get_window_container(packet.ip_dst).add_packet(
                c_packet = CompactedPacket.fromPacket(packet, to_outside = False),
                port = packet.dst_port,
                other_host = packet.get_host(who = 'src')
            )

    def get_window_container(self, host_ip):
        try: return self.hosts[host_ip]
        except KeyError:
            self.hosts[host_ip] = WindowContainer(self.w1, self.w2)
            return self.hosts[host_ip]

    def load_tmap(self, tmapfile):
        with open(tmapfile, 'r') as tmap:
            tmap.readline()
            for line in tmap:
                host, target = line.split('\n')[0].split(',')
                self.get_window_container(host).set_targets(target)

    def save(self, file):
        with open(file, 'wb') as f:
            pickle.dump(self, f)
    @staticmethod
    def load(file):
        return pickle.load(open(file, 'rb'))

class WindowContainer:
    # ONE FOR EACH HOST
    # WILL KEEP TRACK OF EACH CLASSIFICATION WINDOW
    def __init__(self, w1, w2):
        self.w1 = w1
        self.w2 = w2
        self.w1_index = 0
        self.initTime = None
        self.windows = []

    def add_packet(self, c_packet, port, other_host):
        if self.initTime == None: self.initTime = c_packet.time
        w1_offset = self.initTime + timedelta(milliseconds = 1000 * (self.w1_index + 1) * self.w1)

        if c_packet.time < w1_offset:
            self.get_window(self.w1_index).add_packet(c_packet, port, other_host)
        else :
            while c_packet.time >= w1_offset:
                self.w1_index += 1
                w1_offset = self.initTime + timedelta(milliseconds = 1000 * (self.w1_index + 1) * self.w1)
                tmpwindow = self.get_window(self.w1_index)
            self.get_window(self.w1_index).add_packet(c_packet, port, other_host)

    def get_window(self, w1_index):
        try : return self.windows[w1_index]
        except IndexError:
            self.windows.append(ClassificationWindow(
                w2_len = self.w2,
                w2_amount = int(self.w1 / self.w2) + (0 if (self.w1 / self.w2 == int(self.w1 / self.w2)) else 1),
                initTime = self.initTime + timedelta(milliseconds = 1000 * self.w1_index * self.w1)
            ))
            return self.windows[w1_index]

    def set_targets(self, target):
        for clswindow in self.windows:
            clswindow.set_target(target)

class ClassificationWindow:
    # WILL KEEP TRACK OF EACH FLOW INSIDE
    def __init__(self, w2_len, w2_amount, initTime):
        self.w2_len = w2_len
        self.w2_amount = w2_amount
        self.initTime = initTime
        self.flows = {}
        self.target = None

    def add_packet(self, c_packet, port, other_host):
        self.get_flow(port, other_host).add_packet(c_packet)

    def get_flow(self, port, other_host):
        key = '{}:{}'.format(port if port is not None else '', other_host)
        try : return self.flows[key]
        except KeyError:
            self.flows[key] = FlowStructure(self.initTime, self.w2_len, self.w2_amount)
            return self.flows[key]

    def export_features(self, f = Features.CWindow.ALL):
        if f == []: return []

        _pktsCount_s = sum([flow.get_pktsCount('s') for flow in self.flows.values()])
        _pktsCount_r = sum([flow.get_pktsCount('r') for flow in self.flows.values()])
        _packetSizeSum_s = sum([flow.get_pktSizeSum('s') for flow in self.flows.values()])
        _packetSizeSum_r = sum([flow.get_pktSizeSum('r') for flow in self.flows.values()])

        _features = []

        if Features.CWindow.pktsCount in f : _features += [_pktsCount_s, _pktsCount_r]
        if Features.CWindow.packetSizeSum in f : _features += [_packetSizeSum_s, _packetSizeSum_r]
        if Features.CWindow.flowsCount in f : _features += [len(self.flows.keys())]
        if Features.CWindow.hostsCount in f : _features += [len(set([k.split(':')[1] for k in self.flows.keys()]))]

        return _features

    def get_pktSizeSum(self, key = 'both'):
        if key == 'both': return (sum([f.get_pktSizeSum('s') for f in self.flows.values()]) + sum([f.get_pktSizeSum('r') for f in self.flows.values()]))
        else: return sum([f.get_pktSizeSum(key) for f in self.flows.values()])

    def set_target(self, target):
        self.target = target

class FlowStructure:
    # WILL KEEP TRACK OF EACH BEHAVIOUR WINDOW
    def __init__(self, initTime, w2_len, w2_amount):
        self.initTime = initTime
        self.w2_len = w2_len
        self.w2_amount = w2_amount
        self.w2_index = 0
        self.windows = [BehaviourWindow() for i in range(self.w2_amount)]
        self.cluster = None

    def add_packet(self, c_packet):
        w2_offset = self.initTime + timedelta(milliseconds = 1000 * (self.w2_index + 1) * self.w2_len)

        if c_packet.time < w2_offset:
            self.get_window(self.w2_index).add_packet(c_packet)
        else :
            while c_packet.time >= w2_offset:
                self.w2_index += 1
                w2_offset = self.initTime + timedelta(milliseconds = 1000 * (self.w2_index + 1) * self.w2_len)
            self.get_window(self.w2_index).add_packet(c_packet)

    def get_window(self, w2_index):
        return self.windows[w2_index]

    def get_pktsCount(self, key):
        return sum([w2.pktsCount[key] for w2 in self.windows])
    def get_pktSizeSum(self, key):
        return sum([w2.packetSizeSum[key] for w2 in self.windows])

    def export_features(self, f = Features.Flow.ALL):
        if f == []: return []

        _pktsCount_s = sum([w2.pktsCount['s'] for w2 in self.windows])
        _pktsCount_r = sum([w2.pktsCount['r'] for w2 in self.windows])
        _interTimeSum_s = sum([w2.interTimesSum['s'] for w2 in self.windows])
        _interTimeSum_r = sum([w2.interTimesSum['r'] for w2 in self.windows])
        _interTimeSquaredSum_s = sum([w2.interTimesSquaredSum['s'] for w2 in self.windows])
        _interTimeSquaredSum_r = sum([w2.interTimesSquaredSum['r'] for w2 in self.windows])
        _packetSizeSum_s = sum([w2.packetSizeSum['s'] for w2 in self.windows])
        _packetSizeSum_r = sum([w2.packetSizeSum['r'] for w2 in self.windows])
        _packetSizeSquaredSum_s = sum([w2.packetSizeSquaredSum['s'] for w2 in self.windows])
        _packetSizeSquaredSum_r = sum([w2.packetSizeSquaredSum['r'] for w2 in self.windows])

        _interTimeMean_s = (_interTimeSum_s / _pktsCount_s) if (_pktsCount_s > 1) else 0
        _interTimeMean_r = (_interTimeSum_r / _pktsCount_r) if (_pktsCount_r > 1) else 0
        _packetSizeSquaredSum_s = (_packetSizeSum_s / _pktsCount_s) if (_pktsCount_s > 0) else 0
        _packetSizeMean_r = (_packetSizeSum_r / _pktsCount_r) if (_pktsCount_r > 0) else 0

        _interTimeStd_s = ((_interTimeSquaredSum_s / (_pktsCount_s - 1)) - (_interTimeMean_s ** 2)) if (_pktsCount_s > 1) else 0
        _interTimeStd_r = ((_interTimeSquaredSum_r / (_pktsCount_r - 1)) - (_interTimeMean_r ** 2)) if (_pktsCount_r > 1) else 0
        _packetSizeStd_s = ((_packetSizeSquaredSum_s / (_pktsCount_s - 1)) - (_packetSizeSquaredSum_s ** 2)) if (_pktsCount_s > 1) else 0
        _packetSizeStd_r = ((_packetSizeSquaredSum_r / (_pktsCount_r - 1)) - (_packetSizeSquaredSum_r ** 2)) if (_pktsCount_r > 1) else 0

        _features = []

        if Features.Flow.pktsCount in f: _features += [_pktsCount_s, _pktsCount_r]
        if Features.Flow.interArrivalTimeStd in f: _features += [_interTimeStd_s, _interTimeStd_r]
        if Features.Flow.packetSizeStd in f: _features += [_packetSizeStd_s, _packetSizeStd_r]

        return _features

    def set_cluster(self, cluster):
        self.cluster = cluster

class BehaviourWindow:
    # WILL KEEP TRACK OF THE REQUIRED DATA TO EXPORT THE FEATURES

    def __init__(self):
        self.pktsCount = {'s' : 0, 'r' : 0}

        self.prevTime = {'s':None, 'r':None}
        self.interTimesSum = {'s' : 0, 'r' : 0}
        self.interTimesSquaredSum = {'s' : 0, 'r' : 0}

        self.packetSizeSum = {'s':0, 'r':0}
        self.packetSizeSquaredSum = {'s':0, 'r':0}
        self.packetSizeLimits = {
            's': {'max' : 0, 'min' : 1514},
            'r': {'max' : 0, 'min' : 1514}
        }
        self.cluster = None

    def add_packet(self, c_packet):
        key = 's' if (c_packet.to_outside == True) else 'r'

        self.pktsCount[key] += 1

        if self.prevTime[key] == None: self.prevTime[key] = c_packet.time
        else:
            _interTime = (c_packet.time - self.prevTime[key]).total_seconds()
            self.interTimesSum[key] += _interTime
            self.interTimesSquaredSum[key] += (_interTime * _interTime)
            self.prevTime[key] = c_packet.time

        self.packetSizeSum[key] += c_packet.size
        self.packetSizeSquaredSum[key] += (c_packet.size * c_packet.size)
        if c_packet.size > self.packetSizeLimits[key]['max']: self.packetSizeLimits[key]['max'] = c_packet.size
        if c_packet.size < self.packetSizeLimits[key]['min']: self.packetSizeLimits[key]['min'] = c_packet.size

    def export_features(self, f = Features.BWindow.ALL):
        if self.pktsCount['s'] == 0 and self.pktsCount['r'] == 0: return None
        if f == []: return []

        _pktsCountSum = self.pktsCount['s'] + self.pktsCount['r']
        _packetSizeSum = self.packetSizeSum['s'] +  self.packetSizeSum['r']

        _interTime_mean_s = (self.interTimesSum['s'] / self.pktsCount['s']) if (self.pktsCount['s'] > 1) else 0
        _interTime_mean_r = (self.interTimesSum['r'] / self.pktsCount['r']) if (self.pktsCount['r'] > 1) else 0
        _packetSize_mean_s = (self.packetSizeSum['s'] / self.pktsCount['s']) if (self.pktsCount['s'] > 0) else 0
        _packetSize_mean_r = (self.packetSizeSum['r'] / self.pktsCount['r']) if (self.pktsCount['r'] > 0) else 0

        _packetSize_std_s = ((self.packetSizeSquaredSum['s'] / self.pktsCount['s']) - (_packetSize_mean_s ** 2)) if (self.pktsCount['s'] > 0) else 0
        _packetSize_std_r = ((self.packetSizeSquaredSum['r'] / self.pktsCount['r']) - (_packetSize_mean_r ** 2)) if (self.pktsCount['r'] > 0) else 0

        _features = []

        if Features.BWindow.pktsCount in f: _features += [self.pktsCount['s'], self.pktsCount['r']]
        if Features.BWindow.pktsCount_SR_ratio in f: _features += [self.pktsCount['s'] / _pktsCountSum]
        if Features.BWindow.interArrivalTimeMean in f: _features += [_interTime_mean_s, _interTime_mean_r]
        if Features.BWindow.packetSizeSum in f: _features += [self.packetSizeSum['s'], self.packetSizeSum['r']]
        if Features.BWindow.packetSizeSum_SR_ratio in f: _features += [self.packetSizeSum['s'] / _packetSizeSum]
        if Features.BWindow.packetSizeMean in f: _features += [_packetSize_mean_s, _packetSize_mean_r]
        if Features.BWindow.packetSizeStd in f: _features += [_packetSize_std_s, _packetSize_std_r]
        if Features.BWindow.packetSizeRange in f: _features += [
            ((self.packetSizeLimits['s']['max'] - self.packetSizeLimits['s']['min']) / 1514) if (self.pktsCount['s'] > 0) else 0,
            ((self.packetSizeLimits['r']['max'] - self.packetSizeLimits['r']['min']) / 1514) if (self.pktsCount['r'] > 0) else 0
        ]

        return _features

    def set_cluster(self, cluster):
        self.cluster = cluster
