# jitcdde-outputhelpers

A **wrapper** for [`jitcdde`](https://github.com/neurophysik/jitcdde) that enables to **output the intermediate helper variables** alongside the states.

The wrapper replaces the default C code template with a custom one, allowing access to helper values after each integration step.

---

## Files

- **`jitced_adapted_template.c`**  
  Dynamic C template for optimized code generation (replaces the original `jitcdde` template).

- **`customjitcdde.py`**  
  Python wrapper exposing a `CustomJiTCDDE` class with enhanced functionality.

---

## Usage

```python
from customjitcdde import CustomJiTCDDE
from jitcdde import y, t
import numpy as np

# Define your equations and helper symbols
equations = [...]  # your DDE system
helpers  = [...]   # symbolic helper expressions

# Initialize the custom DDE
DDE = CustomJiTCDDE(equations, helpers=helpers)

# Configure as with regular jitcdde (anchors, constants, etc.)
# ...

# Integration (point-by-point)
timepoints = np.linspace(0, 10, 1000)

for i, t in enumerate(timepoints):
    state, helper_values = DDE.integrate(t)
    
    # state: main system state (numpy array)
    # helper_values: values of helper variables (numpy array)
```


If you use this code in your research, teaching, or publications, please cite and reference this repository:
```bibtex
@misc{ZenosAI2025,
  author       = {Zenos.AI},
  title        = {jitcdde_outputhelpers},
  year         = {2025},
  publisher    = {GitHub},
  journal      = {GitHub repository},
  howpublished = {\url{https://github.com/ZenoscienceAI/jitcdde-outputhelpers}},
  note         = {Accessed: November 2025}
}
```
