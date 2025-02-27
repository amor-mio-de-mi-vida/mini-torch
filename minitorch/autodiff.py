from dataclasses import dataclass
from typing import Any, Iterable, List, Tuple

from typing_extensions import Protocol

# ## Task 1.1
# Central Difference calculation


def central_difference(f: Any, *vals: Any, arg: int = 0, epsilon: float = 1e-6) -> Any:
    r"""
    Computes an approximation to the derivative of `f` with respect to one arg.

    See :doc:`derivative` or https://en.wikipedia.org/wiki/Finite_difference for more details.

    Args:
        f : arbitrary function from n-scalar args to one value
        *vals : n-float values $x_0 \ldots x_{n-1}$
        arg : the number $i$ of the arg to compute the derivative
        epsilon : a small constant

    Returns:
        An approximation of $f'_i(x_0, \ldots, x_{n-1})$
    """
    # TODO: Implement for Task 1.1.
    arg_1 = [i for i in vals]
    arg_1[arg] += epsilon
    m = f(*arg_1)
    arg_1[arg] -= 2 * epsilon
    n = f(*arg_1)
    return (m - n) / (2 * epsilon)
    # raise NotImplementedError('Need to implement for Task 1.1')


variable_count = 1


class Variable(Protocol):
    def accumulate_derivative(self, x: Any) -> None:
        pass

    @property
    def unique_id(self) -> int:
        pass

    def is_leaf(self) -> bool:
        pass

    def is_constant(self) -> bool:
        pass

    @property
    def parents(self) -> Iterable["Variable"]:
        pass

    def chain_rule(self, d_output: Any) -> Iterable[Tuple["Variable", Any]]:
        pass


def topological_sort(variable: Variable) -> Iterable[Variable]:
    """
    Computes the topological order of the computation graph.

    Args:
        variable: The right-most variable

    Returns:
        Non-constant Variables in topological order starting from the right.
    """
    # TODO: Implement for Task 1.4.
    result = []
    PermanentMarked = []
    TemporaryMarked = []

    def visit(n: Variable):
        # Don't do anything with constants
        if n.is_constant():
            return
        if n.unique_id in PermanentMarked:
            return
        elif n.unique_id in TemporaryMarked:
            raise RuntimeError("Not a DAG")

        TemporaryMarked.append(n.unique_id)

        if n.is_leaf():
            pass
        else:
            for input in n.history.inputs:
                visit(input)
        TemporaryMarked.remove(n.unique_id)
        PermanentMarked.append(n.unique_id)

        result.insert(0, n)

    visit(variable)
    return result
    # raise NotImplementedError('Need to implement for Task 1.4')


def backpropagate(variable: Variable, deriv: Any) -> None:
    """
    Runs backpropagation on the computation graph in order to
    compute derivatives for the leave nodes.

    Args:
        variable: The right-most variable
        deriv  : Its derivative that we want to propagate backward to the leaves.

    No return. Should write to its results to the derivative values of each leaf through `accumulate_derivative`.
    """
    # TODO: Implement for Task 1.4.
    order = topological_sort(variable)

    node2driv = {}
    node2driv[variable.unique_id] = deriv
    for node in order:
        if node.is_leaf():
            continue
        if node.unique_id in node2driv.keys():
            deriv = node2driv[node.unique_id]
        deriv_tmp = node.chain_rule(deriv)
        for key, item in deriv_tmp:
            if key.is_leaf():
                key.accumulate_derivative(item)
                continue
            if key.unique_id in node2driv.keys():
                node2driv[key.unique_id] += item
            else:
                node2driv[key.unique_id] = item
    # raise NotImplementedError('Need to implement for Task 1.4')


@dataclass
class Context:
    """
    Context class is used by `Function` to store information during the forward pass.
    """

    no_grad: bool = False
    saved_values: Tuple[Any, ...] = ()

    def save_for_backward(self, *values: Any) -> None:
        "Store the given `values` if they need to be used during backpropagation."
        if self.no_grad:
            return
        self.saved_values = values

    @property
    def saved_tensors(self) -> Tuple[Any, ...]:
        return self.saved_values
