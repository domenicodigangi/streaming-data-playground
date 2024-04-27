from abc import ABC, abstractmethod
from typing import Generic, Iterable, TypeVar
from pyflink.common import TypeInformation, Types
from pyflink.datastream import StreamExecutionEnvironment, TimeCharacteristic
from pyflink.datastream.functions import KeyedProcessFunction, ProcessWindowFunction
from pyflink.datastream.window import TimeWindow
from pyflink.datastream.state import ValueState, ValueStateDescriptor
from pyflink.datastream.functions import IN, OUT, KEY, W, W2, Function, KeyedStateStore


class ProcessWindowFunction(Function, Generic[IN, OUT, KEY, W]):
    """
    Base interface for functions that are evaluated over keyed (grouped) windows using a context
    for retrieving extra information.
    """

    class Context(ABC, Generic[W2]):
        """
        The context holding window metadata.
        """

        @abstractmethod
        def window(self) -> W2:
            """
            :return: The window that is being evaluated.
            """
            pass

        @abstractmethod
        def current_processing_time(self) -> int:
            """
            :return: The current processing time.
            """
            pass

        @abstractmethod
        def current_watermark(self) -> int:
            """
            :return: The current event-time watermark.
            """
            pass

        @abstractmethod
        def window_state(self) -> KeyedStateStore:
            """
            State accessor for per-key and per-window state.

            .. note::
                If you use per-window state you have to ensure that you clean it up by implementing
                :func:`~ProcessWindowFunction.clear`.

            :return: The :class:`KeyedStateStore` used to access per-key and per-window states.
            """
            pass

        @abstractmethod
        def global_state(self) -> KeyedStateStore:
            """
            State accessor for per-key global state.
            """
            pass

    @abstractmethod
    def process(
        self, key: KEY, content: "ProcessWindowFunction.Context", elements: Iterable[IN]
    ) -> Iterable[OUT]:
        """
        Evaluates the window and outputs none or several elements.

        :param key: The key for which this window is evaluated.
        :param content: The context in which the window is being evaluated.
        :param elements: The elements in the window being evaluated.
        :return: The iterable object which produces the elements to emit.
        """
        pass

    @abstractmethod
    def clear(self, context: "ProcessWindowFunction.Context") -> None:
        """
        Deletes any state in the :class:`Context` when the Window expires (the watermark passes its
        max_timestamp + allowed_lateness).

        :param context: The context to which the window is being evaluated.
        """
        pass
