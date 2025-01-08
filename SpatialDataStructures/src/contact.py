from typing import Optional
from numpy.typing import ArrayLike
from dataclasses import dataclass

@dataclass
class Contact:
    obj_a: int
    obj_b: Optional[int]

    force: ArrayLike
    torque: ArrayLike
