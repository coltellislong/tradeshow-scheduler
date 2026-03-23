"""CLI interface for tradeshow scheduler."""

from __future__ import annotations

import argparse
import sys
from datetime import date

from .models import Need, NeedPriority, NeedStatus, Tradeshow
from .store import Store


def _parse_date(s: str) -> date:
    try:
        return date.fromisoformat(s)
    except ValueError:
        print(f"Error: invalid date format '{s}'. Use YYYY-MM-DD.")
        sys.exit(1)


def _find_show(store: Store, show_id: str) -> Tradeshow:
    show = store.get(show_id)
    if not show:
        print(f"Error: no tradeshow found with id '{show_id}'.")
        sys.exit(1)
    return show


def _format_show(show: Tradeshow, verbose: bool = False) -> str:
    status = "UPCOMING" if show.is_upcoming else "PAST"
    days = f"in {show.days_until} days" if show.is_upcoming else "past"
    pending = len(show.pending_needs)
    lines = [
        f"[{show.id}] {show.name} ({status}, {days})",
        f"  Location: {show.location}",
        f"  Dates: {show.start_date} to {show.end_date}",
    ]
    if show.booth_number:
        lines.append(f"  Booth: {show.booth_number}")
    lines.append(f"  Pending needs: {pending}/{len(show.needs)}")
    if verbose and show.needs:
        lines.append("  Needs:")
        for n in show.needs:
            marker = "x" if n.status == NeedStatus.COMPLETED else " "
            lines.append(
                f"    [{marker}] [{n.id}] ({n.priority.value}) {n.description}"
                + (f" @{n.assignee}" if n.assignee else "")
            )
    if verbose and show.notes:
        lines.append(f"  Notes: {show.notes}")
    return "\n".join(lines)


def cmd_list(args: argparse.Namespace, store: Store) -> None:
    shows = store.load()
    if args.upcoming:
        shows = [s for s in shows if s.is_upcoming]
    shows.sort(key=lambda s: s.start_date)
    if not shows:
        print("No tradeshows found.")
        return
    for show in shows:
        print(_format_show(show, verbose=args.verbose))
        print()


def cmd_add(args: argparse.Namespace, store: Store) -> None:
    start = _parse_date(args.start)
    end = _parse_date(args.end)
    if end < start:
        print("Error: end date must be on or after start date.")
        sys.exit(1)
    show = Tradeshow(
        name=args.name,
        location=args.location,
        start_date=start,
        end_date=end,
        booth_number=args.booth or "",
        notes=args.notes or "",
    )
    store.add(show)
    print(f"Added tradeshow '{show.name}' (id: {show.id}).")


def cmd_show(args: argparse.Namespace, store: Store) -> None:
    show = _find_show(store, args.id)
    print(_format_show(show, verbose=True))


def cmd_delete(args: argparse.Namespace, store: Store) -> None:
    show = _find_show(store, args.id)
    store.delete(show.id)
    print(f"Deleted tradeshow '{show.name}'.")


def cmd_add_need(args: argparse.Namespace, store: Store) -> None:
    show = _find_show(store, args.show_id)
    priority = NeedPriority(args.priority) if args.priority else NeedPriority.MEDIUM
    need = Need(
        description=args.description,
        priority=priority,
        assignee=args.assignee or "",
    )
    show.needs.append(need)
    store.update(show)
    print(f"Added need '{need.description}' (id: {need.id}) to '{show.name}'.")


def cmd_complete_need(args: argparse.Namespace, store: Store) -> None:
    show = _find_show(store, args.show_id)
    for need in show.needs:
        if need.id == args.need_id:
            need.status = NeedStatus.COMPLETED
            store.update(show)
            print(f"Marked need '{need.description}' as completed.")
            return
    print(f"Error: no need found with id '{args.need_id}'.")
    sys.exit(1)


def cmd_remove_need(args: argparse.Namespace, store: Store) -> None:
    show = _find_show(store, args.show_id)
    original_count = len(show.needs)
    show.needs = [n for n in show.needs if n.id != args.need_id]
    if len(show.needs) == original_count:
        print(f"Error: no need found with id '{args.need_id}'.")
        sys.exit(1)
    store.update(show)
    print("Removed need.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tradeshow",
        description="Track upcoming tradeshows and their needs.",
    )
    sub = parser.add_subparsers(dest="command")

    # list
    p_list = sub.add_parser("list", help="List tradeshows")
    p_list.add_argument("-u", "--upcoming", action="store_true", help="Only upcoming")
    p_list.add_argument("-v", "--verbose", action="store_true", help="Show needs")

    # add
    p_add = sub.add_parser("add", help="Add a tradeshow")
    p_add.add_argument("name")
    p_add.add_argument("location")
    p_add.add_argument("start", help="Start date (YYYY-MM-DD)")
    p_add.add_argument("end", help="End date (YYYY-MM-DD)")
    p_add.add_argument("--booth", help="Booth number")
    p_add.add_argument("--notes", help="Notes")

    # show
    p_show = sub.add_parser("show", help="Show tradeshow details")
    p_show.add_argument("id", help="Tradeshow ID")

    # delete
    p_del = sub.add_parser("delete", help="Delete a tradeshow")
    p_del.add_argument("id", help="Tradeshow ID")

    # add-need
    p_need = sub.add_parser("add-need", help="Add a need to a tradeshow")
    p_need.add_argument("show_id", help="Tradeshow ID")
    p_need.add_argument("description", help="Need description")
    p_need.add_argument(
        "-p",
        "--priority",
        choices=["low", "medium", "high", "critical"],
        default="medium",
    )
    p_need.add_argument("-a", "--assignee", help="Assign to someone")

    # complete-need
    p_done = sub.add_parser("complete-need", help="Mark a need as completed")
    p_done.add_argument("show_id", help="Tradeshow ID")
    p_done.add_argument("need_id", help="Need ID")

    # remove-need
    p_rm = sub.add_parser("remove-need", help="Remove a need")
    p_rm.add_argument("show_id", help="Tradeshow ID")
    p_rm.add_argument("need_id", help="Need ID")

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        sys.exit(0)

    store = Store()
    commands = {
        "list": cmd_list,
        "add": cmd_add,
        "show": cmd_show,
        "delete": cmd_delete,
        "add-need": cmd_add_need,
        "complete-need": cmd_complete_need,
        "remove-need": cmd_remove_need,
    }
    commands[args.command](args, store)


if __name__ == "__main__":
    main()
