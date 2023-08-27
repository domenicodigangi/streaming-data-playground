from typing import Tuple, Collection

from pyflink.common.serializer import TypeSerializer
from pyflink.datastream import WindowAssigner, Trigger
from pyflink.datastream.window import TimeWindow, TimeWindowSerializer


class TumblingEventWindowAssigner(WindowAssigner[Tuple, TimeWindow]):
    def __init__(self, size: int, offset: int, is_event_time: bool):
        self._size = size
        self._offset = offset
        self._is_event_time = is_event_time

    def assign_windows(
        self,
        element: Tuple,
        timestamp: int,
        context: WindowAssigner.WindowAssignerContext,
    ) -> Collection[TimeWindow]:
        start = TimeWindow.get_window_start_with_offset(
            timestamp, self._offset, self._size
        )
        return [TimeWindow(start, start + self._size)]

    def get_default_trigger(self, env) -> Trigger[Tuple, TimeWindow]:
        return EventTimeTrigger()

    def get_window_serializer(self) -> TypeSerializer[TimeWindow]:
        return TimeWindowSerializer()

    def is_event_time(self) -> bool:
        return False
