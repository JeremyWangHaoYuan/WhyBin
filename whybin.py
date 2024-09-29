import itertools
from collections import namedtuple
from typing import overload, Literal
from collections.abc import Iterable, Sequence
from itertools import zip_longest, dropwhile

I = 2
J = 3
W = 4
# W = -1
N = 5
# N = -j
type WhyBinDigit = Literal[0, 1, 2, 3, 4, 5]
type WhyBinDigitSeq = Sequence[WhyBinDigit]

WhyBinDigitSum = namedtuple("WhyBinDigitSum", ("carry", "sum"))

# noinspection PyTypeChecker
CHR_TO_DIGIT: dict[str, WhyBinDigit] = {"0": 0, "1": 1, "i": 2, "j": 3, "I": 2, "J": 3, "w": 4, "n": 5, "W": 4, "N": 5}


def _parse_digit_sum(text: str) -> WhyBinDigitSum:
    if len(text) == 1:
        text = "0" + text
    return WhyBinDigitSum(*map(CHR_TO_DIGIT.__getitem__, text))


def _row(row_text: str) -> tuple[WhyBinDigitSum, ...]:
    return tuple(map(_parse_digit_sum, filter(bool, row_text.split(" "))))


SUM_MATRIX = (
    (
        _row(" 0  1  i  j  W   N"),
        _row(" 1 10  j 1i   0    i"),
        _row(" i  j  0  1  N   W"),
        _row(" j 1i  1 10   i    0"),
        _row("W  0 N  i W0  Wi"),
        _row("N  i W  0 Wi  W0"),
    ),
    (
        _row("  1  10  j  1i   0   i"),
        _row(" 10  11 1i  1j   1   j"),
        _row("  j  1i  1  10  N   0"),
        _row(" 1i  1j 10  11   i   1"),
        _row("  0   1  i   j W0  N"),
        _row("  i   j  0   1  N  W"),
    ),
    (
        _row(" i  j  0  1  N W"),
        _row(" j 1i  1 10   i  0"),
        _row(" 0  1  i  j  W N"),
        _row(" 1 10  j 1i   0  i"),
        _row("N  i W  0 Wi W0"),
        _row("W  0 N  i W0 Wi"),
    ),
    (
        _row("j 1i i 10 i 10"),
        _row("1i 1j 10 11 j 1"),
        _row("1 10 j 1i 0 i"),
        _row("10 11 1i 1j 1 j"),
        _row("i j 0 1 N W"),
        _row("W0 1 i j W N"),
    ),
    (
        _row("W 0 N i W0 Wi"),
        _row("0 1 i j W N"),
        _row("N i W 0 Wi W0"),
        _row("i j 0 1 N W"),
        _row("W0 W Wi N W1 Wj"),
        _row("Wj N W0 W Wj W1"),
    ),
    (
        _row("N i W j Wi W0"),
        _row("i j 0 1 N W"),
        _row("W 0 N i W0 Wi"),
        _row("j 1 i j W N"),
        _row("Wi N W0 W Wj W1"),
        _row("W0 W Wi N W1 Wj"),
    ),
)


def _mrow(row_text: str) -> tuple[WhyBinDigit, ...]:
    return tuple(map(CHR_TO_DIGIT.__getitem__, filter(bool, row_text.split(" "))))


MUL_MATRIX = (
    _mrow("0  0  0  0  0  0"),
    _mrow("0  1  0  1  W  W"),
    _mrow("0  0  i  i  0  i"),
    _mrow("0  1  i  j  W  N"),
    _mrow("0  W  0  W  1  1"),
    _mrow("0  W  i  N  1  j"),
)


class WhyBin:
    __slots__ = ["__digits"]

    @overload
    def __init__(self, value: str):
        pass

    @overload
    def __init__(self, value: int):
        pass

    @overload
    def __init__(self, value: Iterable[WhyBinDigit], lsb=False):
        pass

    def __init__(self, value, lsb=False):
        if lsb:  # make MSB-first for easy stripping
            value = reversed(tuple(value))

        if isinstance(value, str):
            try:
                self.__digits = map(CHR_TO_DIGIT.__getitem__, value)
            except KeyError:
                raise ValueError("Invalid WhyBin string")
        elif isinstance(value, Iterable):
            self.__digits = value
        elif isinstance(value, int):
            self.__digits = (value,)
        else:
            raise TypeError(value)

        self.__digits = dropwhile(lambda d: d == 0, self.__digits)
        # noinspection PyTypeChecker
        self.__digits: tuple[WhyBinDigit, ...] = tuple(reversed(tuple(self.__digits)))
        self._fix_zero()

    def _fix_zero(self):
        if not self.__digits:
            self.__digits = (0,)

    def __str__(self):
        return "".join(map("01ijwn".__getitem__, reversed(self.__digits)))

    def __repr__(self):
        return f"WhyBin({self.__str__()})"

    def __hash__(self):
        return hash(self.__digits)

    def __eq__(self, other):
        if not isinstance(other, WhyBin):
            return False
        return self.__digits == other.__digits

    @staticmethod
    def _a3(a: WhyBinDigit, b: WhyBinDigit, c: WhyBinDigit) -> WhyBinDigitSum:
        return SUM_MATRIX[c][b][a]

    @staticmethod
    def _m2(a: WhyBinDigit, b: WhyBinDigit) -> WhyBinDigit:
        return MUL_MATRIX[b][a]

    def __add__(self, other: "WhyBin"):
        def _add(a: WhyBinDigitSeq, b: WhyBinDigitSeq):
            carry = 0
            for na, nb in zip_longest(a, b, fillvalue=0):
                wbsum = WhyBin._a3(na, nb, carry)
                carry = wbsum.carry
                yield wbsum.sum
            yield WhyBin._a3(0, 0, carry).sum

        return WhyBin(_add(self.__digits, other.__digits), lsb=True)

    def __mul__(self, other: "WhyBin"):
        def _mul(a: WhyBinDigitSeq, b: WhyBinDigitSeq):
            for na in a:
                wbmul = WhyBin._m2(na, b[0])
                yield wbmul
            yield WhyBin._m2(0, 0)

        return WhyBin(_mul(self.__digits, other.__digits), lsb=True)

if __name__ == '__main__':
    digits = [0, 1, I, J, W, N]
    for x, y, z in itertools.product(digits, repeat=3):
        wx, wy, wz = WhyBin(x), WhyBin(y), WhyBin(z)
        print(f"({wx} + {wy}) * {wz} = {(wx + wy) *wz}")
        print(f"{wz} * {wx} + {wz} * {wy} = {(wx * wz) + (wy * wz)}")

        if (wx + wy) *wz != (wx * wz) + (wy * wz):
            print("false")

        else:
            print("true")


    # w1 = WhyBin("1i0j")
    # w2 = WhyBin("100i0")
    # print(f"{w1} + {w2} = {w1 + w2}")
