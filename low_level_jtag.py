from typing import Protocol
from abc import abstractmethod

class LowLevelJTAG(Protocol):
    def blink_on(self) -> None:
        ...

    def blink_off(self) -> None:
        ...

    def read_tdo(self) -> bool:
        ...

    def quit(self) -> None:
        ...

    def write(self, *, tck: bool, tms: bool, tdi: bool) -> None:
        ...

    def reset(self, *, trst, srst) -> None:
        ...

