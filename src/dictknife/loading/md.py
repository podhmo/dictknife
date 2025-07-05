# markdown table format
from dictknife.langhelpers import make_dict
from .raw import setup_extra_parser  # noqa
import itertools


def load(
    fp,
    *,
    loader=None,
    errors=None,
    make_dict=make_dict,
    null_value: str = "null",
    **kwargs,
):
    """Loads data from a Markdown table in a file-like object.

    The table should follow the GitHub Flavored Markdown table format.
    The first row with '|' is treated as headers.
    The second row with '|' and '---' is used to determine column alignment
    and basic type (numeric if alignment is right, i.e., ends with ':').
    Empty cells are skipped. Cells with the `null_value` (default "null")
    are loaded as None.

    Args:
        fp: A file-like object supporting iteration (e.g., an open file).
        loader: (Unused) The loader instance.
        errors: (Unused) Error handling scheme.
        make_dict: Function to create dictionary instances for rows.
        null_value: String representation of null values in the table.
        **kwargs: Additional keyword arguments (currently unused).

    Yields:
        Dictionaries representing rows from the Markdown table.
    """
    keys = None
    # Find the header row
    while keys is None:
        try:
            line = next(fp)
            if "|" in line:
                keys = [tok.strip() for tok in line.strip("|\n").split("|")]
        except StopIteration:
            return  # No header found or empty file

    maybe_nums = None
    # Find the separator row to determine numeric columns
    while maybe_nums is None:
        try:
            line = next(fp)
            if "|" in line and "---" in line:  # Check for separator pattern
                maybe_nums = [
                    tok.strip().endswith(":")
                    and not tok.strip().startswith(":")  # right-align for numbers
                    for tok in line.strip("|\n").split("|")
                ]
                if len(maybe_nums) != len(
                    keys
                ):  # header and separator column count mismatch
                    # This could be an error or a malformed table.
                    # For now, we'll proceed, but it might lead to issues.
                    # Consider raising an error or logging a warning.
                    # Fallback: assume no numeric columns if mismatch
                    maybe_nums = [False] * len(keys)
            elif (
                "|" not in line and "---" not in line and line.strip()
            ):  # Non-table content after header
                maybe_nums = [False] * len(
                    keys
                )  # Assume no numeric types if separator is missing
                break

        except StopIteration:
            # No separator line found after header, assume all non-numeric or handle error
            maybe_nums = [False] * len(keys)  # Default to non-numeric
            break  # Exit loop as fp is exhausted

    for line in fp:
        if "|" not in line:  # Skip non-table lines
            continue
        row = make_dict()
        cells = [tok.strip() for tok in line.strip("|\n").split("|")]

        # Handle rows with more or fewer cells than headers
        # For now, iterate up to the minimum of len(keys) or len(cells)
        # or consider padding/truncating if strictness is required.
        for i, name in enumerate(keys):
            if i >= len(cells):  # Fewer cells than headers
                # row[name] = None # Or some default, or skip
                continue

            val_str = cells[i]
            is_numeric_column = maybe_nums[i] if i < len(maybe_nums) else False

            if not val_str:  # Empty cell
                # row[name] = None # Or skip, current behavior is to skip
                continue
            elif val_str == null_value:
                row[name] = None
            elif is_numeric_column:
                try:
                    if "." in val_str or "e" in val_str.lower():
                        row[name] = float(val_str)
                    else:
                        row[name] = int(val_str)
                except ValueError:
                    row[name] = val_str  # Fallback to string if conversion fails
            else:
                row[name] = val_str
        if row:  # Only yield if row is not empty
            yield row


def dump(
    rows, fp, *, sort_keys: bool = False, null_value: str = "null", **kwargs
) -> None:
    """Dumps a list of dictionaries to a file-like object as a Markdown table.

    Args:
        rows: An iterable of dictionaries to dump. If a single dictionary or string
              is passed, it's wrapped appropriately.
        fp: A file-like object supporting .write().
        sort_keys: If True, the table columns (dictionary keys) will be sorted.
                   Defaults to False.
        null_value: String representation for None values in the output table.
        **kwargs: Additional keyword arguments (currently unused).
    """
    if not rows:
        return
    if hasattr(rows, "keys"):  # Single dictionary
        rows = [rows]
    elif isinstance(rows, str):  # Single string, treat as a single cell in a single row
        rows = [{"column1": rows}]  # Assign a default key if it's just a string

    # Use itertools.tee to avoid exhausting the iterator if `rows` is a generator
    row_iter_for_keys, row_iter_for_data = itertools.tee(iter(rows))

    keys = []
    seen_keys = set()
    maybe_nums = {}  # Store type information (True if numeric)

    # First pass: determine all keys and guess if columns are numeric
    # This ensures all columns are captured even if not present in the first row.
    for row in row_iter_for_keys:
        if not isinstance(row, dict):  # Handle cases where items in rows are not dicts
            # For example, if `rows` was `["string1", "string2"]`
            # This part might need more robust handling depending on expected input.
            # For now, skip non-dict rows or convert them if a strategy is defined.
            continue
        for k, val in row.items():
            if k not in seen_keys:
                keys.append(k)
                seen_keys.add(k)
                maybe_nums[k] = isinstance(val, (int, float)) and not isinstance(
                    val, bool
                )
            elif (
                not maybe_nums[k]
                and isinstance(val, (int, float))
                and not isinstance(val, bool)
            ):
                # If a column was previously thought non-numeric, but a number appears, update.
                maybe_nums[k] = True

    if not keys:  # No keys found (e.g., rows was empty or contained no dicts)
        return

    if sort_keys:
        keys.sort()

    # Print header
    header_str = "| {} |".format(" | ".join(str(k) for k in keys))
    print(header_str, file=fp)

    # Print separator
    separator_parts = []
    for k in keys:
        if maybe_nums.get(
            k, False
        ):  # Default to non-numeric if key somehow missing from maybe_nums
            separator_parts.append("---:")  # Right-align for numbers
        else:
            separator_parts.append(":---")  # Left-align for text
    separator_str = "| {} |".format(" | ".join(separator_parts))
    print(separator_str, file=fp)

    # Print data rows
    for row in row_iter_for_data:
        if not isinstance(row, dict):
            # Handle non-dict items in the data iterator as well
            # e.g., print a row of empty strings or skip
            # For now, print based on keys, substituting empty for missing
            print("| {} |".format(" | ".join([""] * len(keys))), file=fp)
            continue

        cells = []
        for k in keys:  # keys は全行から集めたヘッダーのリスト
            if k not in row:  # ケース1: キー自体が存在しない
                cells.append("")
            else:
                val = row[k]  # キーが存在するので直接アクセス
                if val is None:  # ケース2: 値がNone (JSONのnull)
                    cells.append(str(null_value))
                elif val == "":  # ケース3: 値が空文字列
                    cells.append("")
                else:
                    cells.append(str(val))
        row_str = "| {} |".format(" | ".join(cells))
        print(row_str, file=fp)
