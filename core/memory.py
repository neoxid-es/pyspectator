import psutil
from .monitoring import AbcMonitor
from abc import ABCMeta, abstractmethod


class AbsMemory(AbcMonitor, metaclass=ABCMeta):

    # region initialization

    def __init__(self, monitoring_latency):
        super().__init__(monitoring_latency)
        self.__total = self._get_total_memory()
        self.__available = self._get_available_memory()

    # endregion

    # region properties

    @property
    def total(self):
        return self.__total

    @property
    def available(self):
        return self.__available

    @property
    def used(self):
        return self.total - self.available

    @property
    def percent(self):
        _percent = (self.total - self.available) / self.total
        _percent = '{:.2%}'.format(_percent)
        return _percent

    # endregion

    # region methods & abstract methods

    def _monitoring_action(self):
        self.__available = self._get_available_memory()

    @abstractmethod
    def _get_total_memory(self):
        raise NotImplementedError('Method not implemented by derived class!')

    @abstractmethod
    def _get_available_memory(self):
        raise NotImplementedError('Method not implemented by derived class!')

    # endregion

    pass


class VirtualMemory(AbsMemory):

    def __init__(self, monitoring_latency):
        super().__init__(monitoring_latency)

    def _get_available_memory(self):
        return psutil.virtual_memory().available

    def _get_total_memory(self):
        return psutil.virtual_memory().total


class SwapMemory(AbsMemory):

    def __init__(self, monitoring_latency):
        super().__init__(monitoring_latency)

    def _get_available_memory(self):
        return psutil.swap_memory().free

    def _get_total_memory(self):
        return psutil.swap_memory().total


class NonvolatileMemory(AbsMemory):

    def __init__(self, monitoring_latency, device):
        dev_info = None
        for current_dev_info in psutil.disk_partitions():
            if current_dev_info.device == device:
                dev_info = current_dev_info
                break
        if dev_info is None:
            raise DeviceNotFoundException('Device {0} not found!'.format(device))
        self.__device = device
        self.__mountpoint = dev_info.mountpoint
        self.__fstype = dev_info.fstype
        super().__init__(monitoring_latency)

    @property
    def device(self):
        return self.__device

    @property
    def mountpoint(self):
        return self.__mountpoint

    @property
    def fstype(self):
        return self.__fstype

    def _get_available_memory(self):
        return psutil.disk_usage(self.mountpoint).free

    def _get_total_memory(self):
        return psutil.disk_usage(self.mountpoint).total

    @staticmethod
    def connected_devices(monitoring_latency):
        devices = list()
        for current_dev_info in psutil.disk_partitions():
            current_dev = NonvolatileMemory(monitoring_latency, current_dev_info.device)
            devices.append(current_dev)
        return devices


class DeviceNotFoundException(Exception):
    pass
