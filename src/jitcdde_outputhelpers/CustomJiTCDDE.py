from inspect import stack
from jinja2 import Environment, FileSystemLoader
from jitcdde import jitcdde
from os import path
from pathlib import Path
from warnings import warn
from typing import Any, TypeAlias
from symengine import Symbol, FunctionSymbol, Basic

# Typing for the formula
Tformula: TypeAlias = float | int | Symbol | FunctionSymbol | Basic
Thelpers: TypeAlias = list[tuple[Symbol, Tformula]]


class CustomJiTCDDE(jitcdde):
    """
    A wrapper around JitCDDE that:
    - Uses a custom C template from a file
    - Provides a custom integrate() method that also outputs the helper values

    Attributes:
        number_of_helpers: The number of helpers
        helper_names: The names of the helpers
    """

    def __init__(
        self,
        *args: tuple[Any, ...],
        helpers: Thelpers | None = None,
        **kwargs: dict[str, Any],
    ):
        """Initializes 'CustomJiTCDDE' by loading the template path, calculating the
        number of helpers, and setting both the helpers, the arguments and the kwargs.

        Args:
            args: Unnamed arguments
            helpers: Helper equations
            kwargs: Named arguments
        """
        self.template_source = self._load_template_source()
        self.number_of_helpers = 0 if helpers is None else len(helpers)
        super().__init__(*args, helpers=helpers, **kwargs)

    @property
    def helper_names(self):
        """Return the names of the newly ordered helper functions."""
        names = [str(helper[0]) for helper in self.helpers]
        return names[: self.number_of_helpers]

    def _load_template_source(self):
        """Load the custom template as a string. We use the loaded template to inject it
        later on in '_render_template'."""
        parent_dir = Path(__file__).resolve().parent
        custom_template_path = path.join(parent_dir, "jitced_adapted_template.c")
        if not path.exists(custom_template_path):
            raise FileNotFoundError(
                f"Custom template not found: {custom_template_path}"
            )
        # Read template
        with open(custom_template_path, "r", encoding="utf-8") as f:
            return f.read()

    def _render_template(self, **kwargs: dict[str, Any]):
        """Adapted code to use Jinja2 to render a template for the module. Now, we use
        our own template."""
        kwargs["module_name"] = self._modulename
        folder = path.dirname(stack()[1][1])
        env = Environment(loader=FileSystemLoader(folder))

        # Create a template from the string
        template = env.from_string(self.template_source)

        with open(self.sourcefile, "w") as codefile:
            codefile.write(template.render(kwargs))

    def integrate(self, target_time):
        """
        Tries to evolve the dynamics.

        Parameters
        ----------

        target_time : float
            time until which the dynamics is evolved

        Returns
        -------
        state : NumPy array
            the computed state of the system at `target_time`.
        """
        self._initiate()

        if self.DDE.get_t() > target_time:
            warn(
                "The target time is smaller than the current time. No integration "
                "step will happen. The returned state will be extrapolated from "
                "the interpolating Hermite polynomial for the last integration step. "
                "You may see this because you try to integrate backwards in time, in "
                "which case you did something wrong. You may see this just because your "
                "sampling step is small, in which case there is no need to worry (though you "
                "should think about increasing your sampling time).",
                stacklevel=2,
            )

        if not self.initial_discontinuities_handled:
            warn(
                "You did not explicitly handle initial discontinuities. Proceed only "
                "if you know what you are doing. This is only fine if you somehow chose "
                "your initial past such that the derivative of the last anchor complies "
                "with the DDE. In this case, you can set the attribute `initial_discontinuities_handled` "
                "to `True` to suppress this warning. See https://jitcdde.rtfd.io/#discontinuities for details.",
                stacklevel=2,
            )

        while self.DDE.get_t() < target_time:
            if self.try_single_step(self.dt):
                self.DDE.accept_step()

        result = self.DDE.get_recent_state(target_time)
        self.DDE.forget(self.max_delay)
        return result, self.DDE.get_helpers()[: self.number_of_helpers]
