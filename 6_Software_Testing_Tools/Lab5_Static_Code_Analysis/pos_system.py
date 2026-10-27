"""Retail Point of Sale & Discount Tracker module.

Provides cart checkout calculations, safe promo code evaluation,
stock management, and receipt logging functionality.
"""

import ast
import operator
import secrets
from typing import Dict, List, Optional, Tuple, Union

# Catalog price list for items available in the store
PRICE_LIST: Dict[str, float] = {
    "pen": 10.0,
    "notebook": 45.0,
    "bag": 799.0,
    "bottle": 150.0,
}

ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


class POSSystem:
    """Encapsulates store point of sale transactions and logging state."""

    def __init__(self) -> None:
        """Initialize running sales total and receipt records."""
        self.sales_total: float = 0.0
        self.receipt_lines: List[str] = []

    def _eval_node(self, node: ast.AST, context: Dict[str, float]) -> float:
        """Safely evaluate arithmetic AST nodes for promo calculations."""
        if isinstance(node, ast.Expression):
            return self._eval_node(node.body, context)
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return float(node.value)
        if isinstance(node, ast.Name):
            if node.id in context:
                return float(context[node.id])
            raise ValueError(f"Unknown variable in promo: {node.id}")
        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type in ALLOWED_OPERATORS:
                operand = self._eval_node(node.operand, context)
                return float(ALLOWED_OPERATORS[op_type](operand))
            raise ValueError(f"Unsupported unary operator: {op_type}")
        if isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type in ALLOWED_OPERATORS:
                left = self._eval_node(node.left, context)
                right = self._eval_node(node.right, context)
                return float(ALLOWED_OPERATORS[op_type](left, right))
            raise ValueError(f"Unsupported binary operator: {op_type}")
        raise ValueError(
            f"Unsupported AST node expression: {type(node).__name__}"
        )

    def process_checkout(
        self,
        cart_items: List[Tuple[str, Union[int, float]]],
        tax_rate: float = 0.05,
        receipts: Optional[List[float]] = None,
    ) -> float:
        """Calculate checkout subtotal and total including tax.

        Args:
            cart_items: List of (item_name, quantity) tuples.
            tax_rate: Applicable sales tax rate (default is 0.05).
            receipts: Optional list to store individual receipt totals.

        Returns:
            The grand total of the transaction.
        """
        if receipts is None:
            receipts = []

        subtotal = 0.0
        for item_name, qty in cart_items:
            try:
                quantity = float(qty)
                if item_name in PRICE_LIST and quantity > 0:
                    subtotal += PRICE_LIST[item_name] * quantity
            except (ValueError, TypeError):
                # Ignore invalid quantity specifications
                continue

        effective_tax = max(0.0, tax_rate)
        total = subtotal + (subtotal * effective_tax)
        receipts.append(total)
        self.sales_total += total

        receipt_id = secrets.randbelow(9000) + 1000
        self.receipt_lines.append(f"Receipt #{receipt_id} total={total:.2f}")
        return total

    def apply_promo_code(self, code_str: str) -> float:
        """Safely apply arithmetic promo codes using AST parsing.

        Args:
            code_str: Expression string such as 'total * 0.9' or 'total - 50'.

        Returns:
            Calculated promo discount or new total.
        """
        parsed = ast.parse(code_str.strip(), mode="eval")
        return self._eval_node(parsed, {"total": self.sales_total})

    @staticmethod
    def update_stock(item: str, qty: int) -> None:
        """Update stock log for a given item.

        Args:
            item: Item identifier.
            qty: Stock quantity adjustment.
        """
        if item in PRICE_LIST:
            print(f"Stock updated for {item} by {qty}")
        else:
            print(f"Item '{item}' not found in catalog.")

    def save_receipt_log(self, file_path: str = "pos_log.txt") -> None:
        """Persist generated receipt lines to a log file.

        Args:
            file_path: Destination path for the log file.
        """
        with open(file_path, "a", encoding="utf-8") as file:
            for line in self.receipt_lines:
                file.write(f"{line}\n")

    def print_sales(self) -> None:
        """Display the cumulative sales total."""
        print(f"Sales so far: {self.sales_total:.2f}")


# Module-level instance to support direct standalone script execution
_SYSTEM = POSSystem()


def process_checkout(
    cart_items: List[Tuple[str, Union[int, float]]],
    tax_rate: float = 0.05,
    receipts: Optional[List[float]] = None,
) -> float:
    """Module-level wrapper for checkout processing."""
    return _SYSTEM.process_checkout(cart_items, tax_rate, receipts)


def apply_promo_code(code_str: str) -> float:
    """Module-level wrapper for applying promo code."""
    return _SYSTEM.apply_promo_code(code_str)


def update_stock(item: str, qty: int) -> None:
    """Module-level wrapper for stock update."""
    _SYSTEM.update_stock(item, qty)


def save_receipt_log(file_path: str = "pos_log.txt") -> None:
    """Module-level wrapper for saving receipt log."""
    _SYSTEM.save_receipt_log(file_path)


def print_sales() -> None:
    """Module-level wrapper for displaying sales total."""
    _SYSTEM.print_sales()


def main() -> None:
    """Demonstrate POS workflow and checkout processing."""
    print("Bill 1:", process_checkout([("pen", 3), ("notebook", 2)]))
    print("Bill 2:", process_checkout([("bag", 1), ("laptop", 1)]))
    print("Bill 3:", process_checkout([("bottle", -4)]))
    print("Bill 4:", process_checkout([("pen", "2")], tax_rate=-1))
    update_stock("laptop", 5)
    print("After promo:", apply_promo_code("total * 0.9"))
    code = input("Enter promo code (e.g. total - 50): ") or "total - 50"
    print("After your promo:", apply_promo_code(code))
    save_receipt_log()
    print_sales()


if __name__ == "__main__":
    main()
